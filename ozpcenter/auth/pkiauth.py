"""
PKI Authentication
"""
import logging

from rest_framework import authentication
from rest_framework import exceptions

import ozpcenter.models as models
import ozpcenter.utils as utils

try:
    from django.contrib.auth import get_user_model

    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User

logger = logging.getLogger('ozp-center')

class PkiAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # ensure we're using HTTPS
        if not request.is_secure():
            logger.error('Insecure request (not HTTPS): incompatible with PkiAuthentication')
            return None

        # get status of client authentication
        authentication_status = request.META.get('HTTP_X_SSL_AUTHENTICATED', None)
        if not authentication_status:
            logger.error('Missing header: HTTP_X_SSL_AUTHENTICATED')
            return None

        # this assumes that we're using nginx and that the value of
        # $ssl_client_verify was put into the HTTP_X_SSL_AUTHENTICATED header
        if authentication_status != 'SUCCESS':
            logger.error('Value of HTTP_X_SSL_AUTHENTICATED header not SUCCESS, got %s instead' % authentication_status)
            return None

        # get the user's DN
        dn = request.META.get('HTTP_X_SSL_USER_DN', None)
        # TODO: do we need to preprocess/sanitize this in any way?
        if not dn:
            logger.error('HTTP_X_SSL_USER_DN missing from header')
            return None

        logger.debug('Attempting to authenticate user with dn: %s' % dn)

        profile = _get_profile_by_dn(dn)

        if profile:
            logger.debug('found user %s, authentication succeeded' % profile.user.username)
            return (profile.user, None)
        else:
            logger.error('Failed to find/create user for dn %s. Authentication failed' % dn)
            return None

def _get_profile_by_dn(dn):
    """
    Returns a user profile for a given DN

    If a profile isn't found with the given DN, create one
    """
    # look up the user with this dn. if the user doesn't exist, create them
    try:
        profile = models.Profile.objects.get(dn=dn)
        if not profile.user.is_active:
            logger.warning('User %s tried to login but is inactive' % dn)
            return None
        return profile
    except models.Profile.DoesNotExist:
        logger.info('creating new user for dn: %s' % dn)
        if 'CN=' in dn:
            cn = utils.find_between(dn, 'CN=', ',')
        else:
            cn = dn
        kwargs = {'display_name': cn, 'dn': dn}
        # sanitize username
        username = cn[0:30] # limit to 30 chars
        username = username.replace(' ', '_') # no spaces
        username = username.replace("'", "") # no apostrophes
        username = username.lower() # all lowercase
        # make sure this username doesn't exist
        count = User.objects.filter(
            username=username).count()
        if count != 0:
            username = '%s_%s' % (username, count + 1)

        profile = models.Profile.create_user(username, **kwargs)
        logger.debug('created new profile for user %s' % profile.user.username)
        return profile
