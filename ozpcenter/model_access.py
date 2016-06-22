"""
Generic Model Access
"""
import logging

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from ozpcenter import models
from ozpcenter import utils

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


def get_profile(username):
    """
    get a user's Profile

    Key: current_profile:<username>
    """
    username = utils.make_keysafe(username)
    key = 'current_profile:{0!s}'.format(username)

    data = cache.get(key)
    if data is None:
        try:
            data = models.Profile.objects.get(user__username=username)
            cache.set(key, data)
            # logger.debug('NOT getting data for key: %s from cache' % key)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        # logger.debug('GOT data for key: %s from cache' % key)
        return data
