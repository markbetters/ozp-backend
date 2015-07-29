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
                owner__user__username=username)
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data