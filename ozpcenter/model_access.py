"""
Generic Model Access
"""
import logging

from django.core.exceptions import ObjectDoesNotExist

from ozpcenter import models


# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


def get_profile(username):
    """
    get a user's Profile

    Key: current_profile:<username>
    """
    try:
        return models.Profile.objects.get(user__username=username)
    except ObjectDoesNotExist:
        return None
