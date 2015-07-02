"""
Custom permissions for API endpoints

Can do things like if view.action == 'create'

"""
from rest_framework import permissions
import ozpcenter.models as models
import ozpcenter.model_access as model_access

class IsUser(permissions.BasePermission):
    """
    Global permission check if current user is a User
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated():
        	return False
        profile = model_access.get_profile(request.user.username)
        if profile is None:
           return False
        if profile.highest_role in [models.Profile.USER,
            models.Profile.ORG_STEWARD, models.Profile.APPS_MALL_STEWARD]:
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
    	profile = model_access.get_profile(request.user.username)
    	if profile is None:
    		return False
    	if profile.highest_role in [models.Profile.ORG_STEWARD,
            models.Profile.APPS_MALL_STEWARD]:
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
    	profile = model_access.get_profile(request.user.username)
    	if profile is None:
    		return False
    	if profile.highest_role == models.Profile.APPS_MALL_STEWARD:
    		return True
    	else:
    		return False
