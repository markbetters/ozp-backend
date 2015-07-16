"""
Model access
"""
import logging

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

import ozpcenter.models as models
import ozpcenter.utils as utils
import ozpcenter.model_access as generic_model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

def get_self(username):
    return generic_model_access.get_profile(username)