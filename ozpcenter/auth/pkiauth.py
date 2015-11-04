"""
PKI Authentication
"""
import logging

from rest_framework import authentication
from rest_framework import exceptions

import ozpcenter.models as models

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
            logger.error('Insecure request: incompatible with PkiAuthentication')
            return None

        authentication_status = request.META.get('HTTP_X_SSL_AUTHENTICATED', None)

        # ensure client authentication was successful and that the header
        # containing the user's DN is present

        # this assumes that we're using nginx and that the value of
        # $ssl_client_verify was put into the HTTP_X_SSL_AUTHENTICATED header
        if (authentication_status != 'SUCCESS' or
                    'HTTP_X_SSL_USER_DN' not in request.META):
            logger.error(
                'HTTP_X_SSL_AUTHENTICATED marked failed or '
                'HTTP_X_SSL_USER_DN '
                'header missing')
            return None

        # get the user's dn
        # TODO: do we need to preprocess/sanitize this in any way?
        dn = request.META.get('HTTP_X_SSL_USER_DN')
        profile = _get_profile_by_dn(dn)

        return (profile.user, None)

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
        kwargs = {'display_name': dn}
        # sanitize username
        username = dn[:30] # limit to 30 chars
        username = username.replace(' ', '_') # no spaces
        username = username.replace("'", "") # no apostrophes
        username = username.lower() # all lowercase
        # make sure this username doesn't exist
        # TODO: find a unique username if this check fails
        if User.objects.filter(username=username).first():
            logger.error('Username collision for dn: %s' % dn)
            return None

        return models.Profile.create_user(username, **kwargs)
