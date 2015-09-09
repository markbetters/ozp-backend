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

def get_all_agencies():
    """
    Get all models.Agency objects

    key = agencies
    """
    key = 'agencies'
    data = cache.get(key)
    if data is None:
        try:
            data = models.Agency.objects.all()
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data

def get_agency_by_title(title):
    """
    key = agency:<title>
    """
    key = 'agency:%s' % utils.make_keysafe(title)
    data = cache.get(key)
    if data is None:
        try:
            data = models.Agency.objects.get(title=title)
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data