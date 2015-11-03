"""
All authorization classes must inherit from this base class

Checks models.Profile.auth_expires. If auth is expired, refresh it.

- models.Profile.user.groups (User, Org Steward, or Apps Mall Steward)
- models.Profile.stewarded_organizations (clear all if user is not an Org Steward)
- models.Profile.organizations
- models.Profile.access_control
- models.Profile.display_name (use CN)
"""
import datetime
import logging
import pytz

from django.contrib.auth.models import Group

import ozpcenter.model_access as model_access
import ozpcenter.errors as errors
import ozpcenter.models as models

logger = logging.getLogger('ozp-center')

class BaseAuthorization:

    def get_auth_data(self, username):
        """
        Get authorization data for given user

        Return:
        {
            'dn': 'user DN',
            'cn': 'user CN',
            'clearances': ['U', 'S'],
            'formal_accesses': ['AB', 'CD'],
            'visas': ['ABC', 'XYZ'],
            'duty_org': 'org',
            'is_org_steward': False,
            'is_apps_mall_steward': False,
            'is_metrics_user': True
        }
        """
        raise NotImplementedError('Auth class failed to implement get_auth_data method')

    def authorization_update(self, username, updated_auth_data=None):
        """
        Update authorization info for this user

        Args:
            username: username for which to update auth data
            updated_auth_data: for testing purposes - if this is passed in,
                the data is used instead of invoking the parent class's
                get_auth_data() method

        Return True if update succeeds, False otherwise
        """
        profile = model_access.get_profile(username)
        if not profile:
            raise errors.NotFound('User %s was not found - cannot update authorization info' % username)

        # check profile.auth_expires. if auth_expires - now > 24 hours, raise an
        # exception (auth data should never be cached for more than 24 hours)
        now = datetime.datetime.now(pytz.utc)
        logger.debug('profile for %s expires at %s' % (username, profile.auth_expires))
        logger.debug('now is: %s' % now)
        expires_in = profile.auth_expires - now
        if expires_in.days >=1:
            raise errors.AuthorizationFailure('User %s had auth expires set to expire more than 24 hours from last check' % username)
        else:
            raise errors.AuthorizationFailure('wat? expires in: %s days, %s seconds' % (expires_in.days, expires_in.seconds))

        # if auth_data cache hasn't expired, we're good to go
        if now <= profile.auth_expires:
            return True

        # otherwise, auth data must be updated
        if not updated_auth_data:
            updated_auth_data = self.get_auth_data(username)

        # update the user's org (profile.organizations) from duty_org
        # validate the org
        duty_org = updated_auth_data['duty_org']
        orgs = models.Agency.objects.values_list('short_name', flat=True)
        if duty_org not in orgs:
            raise errors.AuthorizationFailure('User %s has invalid duty org %s' % (username, duty_org))

        # update the user's org
        profile.organizations.clear()
        org = models.Agency.objects.get(short_name=duty_org)
        profile.organizations.add(org)

        if not updated_auth_data.is_org_steward:
            # remove all profile.stewarded_orgs
            profile.stewarded_organizations.clear()
            # remove ORG_STEWARD from profile.user.groups
            for g in profile.user.groups:
                if g.name == 'ORG_STEWARD':
                    profile.user.groups.remove(g)
        else:
            # ensure ORG_STEWARD is in profile.user.groups
            g = Group.objects.get(name='ORG_STEWARD')
            profile.user.groups.add(g)

        if not updated_auth_data.is_apps_mall_steward:
            # ensure APPS_MALL_STEWARD is not in profile.user.groups
            for g in profile.user.groups:
                if g.name == 'APPS_MALL_STEWARD':
                    profile.user.groups.remove(g)
        else:
            # ensure APPS_MALL_STEWARD is in profile.user.groups
            g = Group.objects.get(name='APPS_MALL_STEWARD')
            profile.user.groups.add(g)

        # TODO: handle metrics user

        # update profile.access_control:
        profile.access_control = json.dumps(updated_auth_data)
        # reset profile.auth_expires to now + 24 hours
        profile.auth_expires = now + datetime.timedelta(seconds=24*60*60)
        profile.save()
        return True