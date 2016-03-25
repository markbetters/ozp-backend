"""
Model access
"""
import logging

import django.contrib.auth

import ozpcenter.models as models
import ozpcenter.model_access as generic_model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center')


def get_self(username):
    return generic_model_access.get_profile(username)


def get_all_profiles():
    return models.Profile.objects.all()


def get_profile_by_id(profile_id):
    try:
        return models.Profile.objects.get(id=profile_id)
    except models.Listing.DoesNotExist:
        return None


def get_all_listings_for_profile_by_id(profile_id):
    try:
        profile_instance = models.Profile.objects.get(id=profile_id).user
    except models.Profile.DoesNotExist:
        return None

    try:
        return models.Listing.objects.for_user(profile_instance.username).all()
    except models.Listing.DoesNotExist:
        return None


def get_listing_by_id_for_profile_by_id(profile_id, listing_id):
    try:
        profile_instance = models.Profile.objects.get(id=profile_id).user
    except models.Listing.DoesNotExist:
        return None

    try:
        return models.Listing.objects.for_user(profile_instance.username).get(id=listing_id)
    except models.Listing.DoesNotExist:
        return None


def get_profiles_by_role(role):
    return models.Profile.objects.filter(
        user__groups__name__exact=role)


def filter_queryset_by_username_starts_with(queryset, starts_with):
    return queryset.filter(user__username__startswith=starts_with)


def get_all_users():
    return django.contrib.auth.models.User.objects.all()


def get_all_groups():
    return django.contrib.auth.models.Group.objects.all()
