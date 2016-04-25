"""
Model access
"""
import logging

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

import ozpcenter.models as models
import ozpcenter.utils as utils

# Get an instance of a logger
logger = logging.getLogger('ozp-center.'+str(__name__))


def get_all_library_entries():
    """
    Get all ApplicationLibrary objects

    Key: library_entries
    """
    key = 'library_entries'
    data = cache.get(key)
    if data is None:
        try:
            data = models.ApplicationLibraryEntry.objects.all()
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
    key = 'library:%s' % id
    data = cache.get(key)
    if data is None:
        try:
            data = models.ApplicationLibraryEntry.objects.get(id=id)
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
    key = 'app_library:%s' % username
    data = cache.get(key)
    if data is None:
        try:
            data = models.ApplicationLibraryEntry.objects.filter(
                owner__user__username=username).filter(listing__is_enabled=True)

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
    key = 'app_library_type(%s):%s' % (username, listing_type_key)
    data = cache.get(key)
    if data is None:
        try:
            data = models.ApplicationLibraryEntry.objects.filter(
                owner__user__username=username).filter(listing__listing_type__title=listing_type).filter(listing__is_enabled=True)
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data
