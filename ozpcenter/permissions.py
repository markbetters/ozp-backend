"""
Custom permissions for API endpoints

Can do things like if view.action == 'create'

"""
from ozpcenter import models
from ozpcenter import utils
from rest_framework import permissions
import ozpcenter.model_access as model_access

from plugins_util import plugin_manager


SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']


class IsAppsMallStewardOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated():
            return False

        ozp_authorization = plugin_manager.get_system_authorization_plugin()
        ozp_authorization.authorization_update(request.user.username, request=request)
        user_profile = model_access.get_profile(request.user.username)
        if (request.method in SAFE_METHODS or
                user_profile.highest_role() in ['APPS_MALL_STEWARD']):
            return True
        return False


class IsOrgStewardOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated():
            return False

        ozp_authorization = plugin_manager.get_system_authorization_plugin()
        ozp_authorization.authorization_update(request.user.username, request=request)
        user_profile = model_access.get_profile(request.user.username)
        if (request.method in SAFE_METHODS or
                user_profile.highest_role() in ['APPS_MALL_STEWARD', 'ORG_STEWARD']):
            return True
        return False


class IsUser(permissions.BasePermission):
    """
    Global permission check if current user is a User
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated():
            return False

        ozp_authorization = plugin_manager.get_system_authorization_plugin()
        ozp_authorization.authorization_update(request.user.username, request=request)
        profile = model_access.get_profile(request.user.username)
        if profile is None:
            return False
        if profile.highest_role() in ['USER', 'ORG_STEWARD', 'APPS_MALL_STEWARD']:
            return True
        else:
            return False


class IsOrgSteward(permissions.BasePermission):
    """
    Global permission check if current user is an OrgSteward
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated():
            return False

        ozp_authorization = plugin_manager.get_system_authorization_plugin()
        ozp_authorization.authorization_update(request.user.username, request=request)
        profile = model_access.get_profile(request.user.username)
        if profile is None:
            return False
        if profile.highest_role() in ['ORG_STEWARD', 'APPS_MALL_STEWARD']:
            return True
        else:
            return False


class IsAppsMallSteward(permissions.BasePermission):
    """
    Global permission check if current user is an AppsMallSteward
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated():
            return False

        ozp_authorization = plugin_manager.get_system_authorization_plugin()
        ozp_authorization.authorization_update(request.user.username, request=request)
        profile = model_access.get_profile(request.user.username)
        if profile is None:
            return False
        if profile.highest_role() == 'APPS_MALL_STEWARD':
            return True
        else:
            return False
