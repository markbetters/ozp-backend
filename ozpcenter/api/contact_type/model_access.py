"""
Model Access
"""
import logging
import os.path

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

import ozpcenter.models as models
import ozpcenter.utils as utils

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

def get_all_contact_types():
    """
    Get all models.ContactType objects

    key = contact_types
    """
    key = 'contact_types'
    data = cache.get(key)
    if data is None:
        try:
            data = models.ContactType.objects.all()
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data

def get_contact_type_by_name(name):
    """
    key = contact_type:<name>
    """
    key = 'contact_type:%s' % utils.make_keysafe(name)
    data = cache.get(key)
    if data is None:
        try:
            data = models.ContactType.objects.get(name=name)
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data