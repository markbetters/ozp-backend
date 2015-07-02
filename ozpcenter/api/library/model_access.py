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
	pass