"""
Model access
"""
import logging

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

import ozpcenter.models as models
import ozpcenter.utils as utils

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


def get_all_library_entries():
    """
    Get all ApplicationLibrary objects

    Key: library_entries
    """
    key = 'library_entries'
    data = cache.get(key)
    if data is None:
        try:
            data = models.ApplicationLibraryEntry.objects.filter(listing__is_deleted=False).all()
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data


def get_library_entry_by_id(id):
    """
    Get ApplicationLibrary by id

    Key: library:<id>
    """
    key = 'library:{0!s}'.format(id)
    data = cache.get(key)
    if data is None:
        try:
            data = models.ApplicationLibraryEntry.objects.get(id=id)  # Is this need filter(listing__is_deleted=False)
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data


def get_self_application_library(username):
    """
    Get the ApplicationLibrary for this user

    Key: app_library:<username>
    """
    username = utils.make_keysafe(username)
    key = 'app_library:{0!s}'.format(username)
    data = cache.get(key)
    if data is None:
        try:
            data = models.ApplicationLibraryEntry.objects.filter(
                owner__user__username=username).filter(listing__is_enabled=True) \
                .filter(listing__is_deleted=False)

            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data


def get_self_application_library_by_listing_type(username, listing_type):
    """
    Get the ApplicationLibrary for this user filtered by listing type

    Key: app_library_type(<listing_type>):<username>
    """
    username = utils.make_keysafe(username)
    listing_type_key = utils.make_keysafe(listing_type)
    key = 'app_library_type({0!s}):{1!s}'.format(username, listing_type_key)
    data = cache.get(key)
    if data is None:
        try:
            data = models.ApplicationLibraryEntry.objects.filter(
                owner__user__username=username).filter(listing__listing_type__title=listing_type) \
                .filter(listing__is_enabled=True) \
                .filter(listing__is_deleted=False)
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data
