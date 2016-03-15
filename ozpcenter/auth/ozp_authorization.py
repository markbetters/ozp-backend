"""
Authorization for OZP using the DemoAuth service

Checks models.Profile.auth_expires. If auth is expired, refresh it.

- models.Profile.user.groups (User, Org Steward, or Apps Mall Steward)
- models.Profile.stewarded_organizations (clear all if user is not an Org Steward)
- models.Profile.organizations
- models.Profile.access_control
- models.Profile.display_name (use CN)
"""
import datetime
import json
import logging
import pytz

import requests

from django.conf import settings
from django.contrib.auth.models import Group

import ozpcenter.errors as errors
import ozpcenter.model_access as model_access
import ozpcenter.models as models
import ozpcenter.utils as utils

logger = logging.getLogger('ozp-center')


def _get_auth_data(username):
    """
    Get authorization data for given user

    Return:
    {
        'dn': 'user DN',
        'clearances': ['U', 'S'],
        'formal_accesses': ['AB', 'CD'],
        'visas': ['ABC', 'XYZ'],
        'duty_org': 'org',
        'is_org_steward': False,
        'is_apps_mall_steward': False,
        'is_metrics_user': True
    }
    """
    profile = model_access.get_profile(username)
    # get user's basic data
    url = settings.OZP['OZP_AUTHORIZATION']['USER_INFO_URL'] % (profile.dn, profile.issuer_dn)
    server_crt = settings.OZP['OZP_AUTHORIZATION']['SERVER_CRT']
    server_key = settings.OZP['OZP_AUTHORIZATION']['SERVER_KEY']
    r = requests.get(url, cert=(server_crt, server_key), verify=False)
    logger.debug('hitting url %s for user with dn %s' % (url, profile.dn))

    if r.status_code != 200:
        raise errors.AuthorizationFailure('Error contacting authorization server: %s' % r.text)
    user_data = r.json()

    # convert dutyorg -> duty_org
    user_data['duty_org'] = user_data['dutyorg']
    user_data.pop('dutyorg', None)

    # convert formalAcccesses -> formal_accesses
    user_data['formal_accesses'] = user_data['formalAccesses']
    user_data.pop('formalAccesses', None)

    # get groups for user
    url = settings.OZP['OZP_AUTHORIZATION']['USER_GROUPS_URL'] % (profile.dn, settings.OZP['OZP_AUTHORIZATION']['PROJECT_NAME'])
    logger.debug('hitting url %s for user with dn %s for group info' % (url, profile.dn))
    r = requests.get(url, cert=(server_crt, server_key), verify=False)
    if r.status_code != 200:
        raise errors.AuthorizationFailure('Error contacting authorization server: %s' % r.text)

    groups = r.json()['groups']
    user_data['is_org_steward'] = False
    user_data['is_apps_mall_steward'] = False
    user_data['is_metrics_user'] = False

    for g in groups:
        if settings.OZP['OZP_AUTHORIZATION']['APPS_MALL_STEWARD_GROUP_NAME'] == utils.find_between(g, 'cn=', ','):
            user_data['is_apps_mall_steward'] = True
        if settings.OZP['OZP_AUTHORIZATION']['ORG_STEWARD_GROUP_NAME'] == utils.find_between(g, 'cn=', ','):
            user_data['is_org_steward'] = True
        if settings.OZP['OZP_AUTHORIZATION']['METRICS_GROUP_NAME'] == utils.find_between(g, 'cn=', ','):
            user_data['is_org_steward'] = True

    return user_data


def authorization_update(username, updated_auth_data=None):
        """
        Update authorization info for this user

        Args:
            username: username for which to update auth data
            updated_auth_data: for testing purposes - if this is passed in,
                the data is used instead of invoking the parent class's
                get_auth_data() method

        Return True if update succeeds, False otherwise
        """
        if not settings.OZP['USE_AUTH_SERVER']:
            return True

        profile = model_access.get_profile(username)
        if not profile:
            raise errors.NotFound('User %s was not found - cannot update authorization info' % username)

        # check profile.auth_expires. if auth_expires - now > 24 hours, raise an
        # exception (auth data should never be cached for more than 24 hours)
        now = datetime.datetime.now(pytz.utc)
        seconds_to_cache_data = int(settings.OZP['OZP_AUTHORIZATION']['SECONDS_TO_CACHE_DATA'])
        if seconds_to_cache_data > 24 * 3600:
            raise errors.AuthorizationFailure('Cannot cache data for more than 1 day')
        expires_in = profile.auth_expires - now
        if expires_in.days >= 1:
            raise errors.AuthorizationFailure('User %s had auth expires set to expire in more than 24 hours' % username)

        # if auth_data cache hasn't expired, we're good to go
        # TODO: might want to check and see if auth expires in 12 hours
        # (or something like that)
        # and if so, try to preemptively update user's credentials. This would
        # help to alleviate errors due to the authorization service being down
        if now <= profile.auth_expires:
            logger.debug('no auth refresh required. Expires in %s seconds' % expires_in.seconds)
            return True

        # otherwise, auth data must be updated
        if not updated_auth_data:
            updated_auth_data = _get_auth_data(username)
            if not updated_auth_data:
                return False

        # update the user's org (profile.organizations) from duty_org
        # validate the org
        duty_org = updated_auth_data['duty_org']
        orgs = models.Agency.objects.values_list('short_name', flat=True)

        if duty_org not in orgs:
            if (hasattr(settings, 'DEFAULT_AGENCY') and (settings.DEFAULT_AGENCY != '')):
                duty_org = settings.DEFAULT_AGENCY
            else:
                raise errors.AuthorizationFailure('User %s has invalid duty org %s' % (username, duty_org))

        # update the user's org
        try:
            profile.organizations.clear()
            org = models.Agency.objects.get(short_name=duty_org)
            profile.organizations.add(org)
        except Exception as e:
            logger.error('Failed to update organizations for user %s. Error: %s' % (username, str(e)))
            return False

        if not updated_auth_data['is_org_steward']:
            # remove all profile.stewarded_orgs
            profile.stewarded_organizations.clear()
            # remove ORG_STEWARD from profile.user.groups
            for g in profile.user.groups.all():
                if g.name == 'ORG_STEWARD':
                    profile.user.groups.remove(g)
            # add to USER group
            g = Group.objects.get(name='USER')
            profile.user.groups.add(g)
        else:
            # ensure ORG_STEWARD is in profile.user.groups
            g = Group.objects.get(name='ORG_STEWARD')
            profile.user.groups.add(g)

        if not updated_auth_data['is_apps_mall_steward']:
            # ensure APPS_MALL_STEWARD is not in profile.user.groups
            for g in profile.user.groups.all():
                if g.name == 'APPS_MALL_STEWARD':
                    profile.user.groups.remove(g)
            # add to USER group
            g = Group.objects.get(name='USER')
            profile.user.groups.add(g)
        else:
            # ensure APPS_MALL_STEWARD is in profile.user.groups
            g = Group.objects.get(name='APPS_MALL_STEWARD')
            profile.user.groups.add(g)

        # TODO: handle metrics user

        # update profile.access_control:
        access_control = json.dumps(updated_auth_data)
        profile.access_control = access_control
        # reset profile.auth_expires to now + 24 hours
        profile.auth_expires = now + datetime.timedelta(seconds=seconds_to_cache_data)
        profile.save()
        return True
