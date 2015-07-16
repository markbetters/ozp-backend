"""
Model access
"""
import logging

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

import ozpcenter.models as models
import ozpcenter.utils as utils

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

def filter_listings(username, filter_params):
    """
    Filter Listings

    Respects private apps (only from user's agency) and user's
    max_classification_level

    filter_params can contain:
        * list of category names (AND logic)
        * list of agencies (OR logic)
        * list of listing types (OR logic)
        * offset (for pagination)

    Too many variations to cache
    """
    objects = models.Listing.objects.for_user(username).all()
    if 'categories' in filter_params:
        logger.info('filtering categories: %s' % filter_params['categories'])
        # TODO: this is OR logic not AND
        objects = objects.filter(
            categories__title__in=filter_params['categories'])
    if 'agencies' in filter_params:
        logger.info('filtering agencies: %s' % filter_params['agencies'])
        objects = objects.filter(
            agency__title__in=filter_params['agencies'])
    if 'listing_types' in filter_params:
        logger.info('filtering listing_types: %s' % filter_params['listing_types'])
        objects = objects.filter(
            app_type__title__in=filter_params['listing_types'])

    # enforce any pagination params
    if 'offset' in filter_params:
        offset = int(filter_params['offset'])
        objects = objects[offset:]

    if 'limit' in filter_params:
        limit = int(filter_params['limit'])
        objects = objects[0:limit]

    return objects

def get_self_listings(username):
    """
    Get the Listings that belong to this user

    Key: self_listings:<username>
    """
    pass

def get_listings(username):
    """
    Get Listings this user can see

    Key: listings:<username>
    """
    username = utils.make_keysafe(username)
    key = 'listings:%s' % username
    data = cache.get(key)
    if data is None:
        try:
            data = models.Listing.objects.for_user(username).all()
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data