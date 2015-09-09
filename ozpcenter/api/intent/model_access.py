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

def get_all_intents():
    """
    Get all models.Intent objects

    key = intents
    """
    key = 'intents'
    data = cache.get(key)
    if data is None:
        try:
            data = models.Intent.objects.all()
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data

def get_intent_by_action(action):
    """
    key = intent:<action>
    """
    key = 'intent:%s' % utils.make_keysafe(action)
    data = cache.get(key)
    if data is None:
        try:
            data = models.Intent.objects.get(action=action)
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data