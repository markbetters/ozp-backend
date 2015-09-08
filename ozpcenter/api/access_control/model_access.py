"""
Access Control model access
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

def get_all_access_controls():
    """
    Get all models.AccessControl objects

    key = access_control
    """
    key = 'access_control'
    data = cache.get(key)
    if data is None:
        try:
            data = models.AccessControl.objects.all()
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data