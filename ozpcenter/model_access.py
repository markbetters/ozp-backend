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
    Get a User's Profile

    Args:
        username

    Return:
        Profile
    """
    try:
        return models.Profile.objects.get(user__username=username)
    except ObjectDoesNotExist:
        return None
