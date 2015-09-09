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

def get_all_categories():
    """
    Get all models.Category objects

    key = agencies
    """
    key = 'categories'
    data = cache.get(key)
    if data is None:
        try:
            data = models.Category.objects.all()
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data

def get_category_by_title(title):
    """
    key = category:<title>
    """
    key = 'category:%s' % utils.make_keysafe(title)
    data = cache.get(key)
    if data is None:
        try:
            data = models.Category.objects.get(title=title)
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data