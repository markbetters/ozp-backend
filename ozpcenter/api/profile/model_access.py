"""
Profile Model Access
"""
import logging

from ozpcenter import models
from django.contrib import auth
import ozpcenter.model_access as generic_model_access

from plugins_util.plugin_manager import system_has_access_control

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


def get_self(username):
    """
    Get Profile by username

    Args:
        username(str)

    Return:
        Profile
    """
    return generic_model_access.get_profile(username)


def get_all_profiles():
    """
    Get All Profiles
    """
    return models.Profile.objects.all().order_by('display_name')


def get_profile_by_id(profile_id):
    """
    Get profile by id
    """
    try:
        return models.Profile.objects.get(id=profile_id)
    except models.Listing.DoesNotExist:
        return None


def get_all_listings_for_profile_by_id(current_request_username, profile_id, listing_id=None):
    """
    Get all Listing for a profile by profile_id and listing_id

    Args:
        current_request_username
        profile_id
        listing_id

    """
    try:
        if profile_id == 'self':
            profile_instance = models.Profile.objects.get(user__username=current_request_username).user
        else:
            profile_instance = models.Profile.objects.get(id=profile_id).user
    except models.Profile.DoesNotExist:
        return None

    try:
        listings = models.Listing.objects.filter(owners__id=profile_instance.id)
        listings = listings.exclude(is_private=True)
        # filter out listings by user's access level
        titles_to_exclude = []
        for i in listings:
            if not i.security_marking:
                logger.debug('Listing {0!s} has no security_marking'.format(i.title))
            if not system_has_access_control(current_request_username, i.security_marking):
                titles_to_exclude.append(i.title)
        listings = listings.exclude(title__in=titles_to_exclude)  # TODO: Base it on ids

        if listing_id:
            filtered_listing = listings.get(id=listing_id)
        else:
            filtered_listing = listings.all()

        return filtered_listing
    except models.Listing.DoesNotExist:
        return None


def get_profiles_by_role(role):
    """
    Get Profiles by the role and ordered by display_name

    Args:
        role(str): Role of user - USER, ORG_STEWARD..
    """
    return models.Profile.objects.filter(
        user__groups__name__exact=role).order_by('display_name')


def filter_queryset_by_username_starts_with(queryset, starts_with):
    return queryset.filter(user__username__startswith=starts_with)


def get_all_users():
    """
    Get all Users (User Objects)
    """
    return auth.models.User.objects.all()


def get_all_groups():
    """
    Get all groups
    """
    return auth.models.Group.objects.all()
