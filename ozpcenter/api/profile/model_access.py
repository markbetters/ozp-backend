"""
Model access
"""
import logging

from ozpcenter import models
from django.contrib import auth
import ozpcenter.model_access as generic_model_access

from plugins_util import plugin_manager

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


def get_self(username):
    return generic_model_access.get_profile(username)


def get_all_profiles():
    return models.Profile.objects.all().order_by('display_name')


def get_profile_by_id(profile_id):
    try:
        return models.Profile.objects.get(id=profile_id)
    except models.Listing.DoesNotExist:
        return None


def get_all_listings_for_profile_by_id(current_request_username, profile_id, listing_id=None):
    access_control_instance = plugin_manager.get_system_access_control_plugin()
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

        current_profile_instance = models.Profile.objects.get(user__username=current_request_username)
        # filter out listings by user's access level
        titles_to_exclude = []
        for i in listings:
            if not i.security_marking:
                logger.debug('Listing {0!s} has no security_marking'.format(i.title))
            if not access_control_instance.has_access(current_profile_instance.access_control, i.security_marking):
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
    return models.Profile.objects.filter(
        user__groups__name__exact=role).order_by('display_name')


def filter_queryset_by_username_starts_with(queryset, starts_with):
    return queryset.filter(user__username__startswith=starts_with)


def get_all_users():
    return auth.models.User.objects.all()


def get_all_groups():
    return auth.models.Group.objects.all()
