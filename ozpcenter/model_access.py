"""
Generic model access methods
"""
import logging

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

import ozpcenter.models as models
import ozpcenter.utils as utils

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

def get_profile(username):
	"""
	get a user's Profile

	Key: current_profile:<username>
	"""
	username = utils.make_keysafe(username)
	key = 'current_profile:%s' % username

	data = cache.get(key)
	if data is None:
		try:
			data = models.Profile.objects.get(username=username)
			cache.set(key, data)
			logger.info('NOT getting data for key: %s from cache' % key)
			return data
		except ObjectDoesNotExist:
			return None
	else:
		logger.info('GOT data for key: %s from cache' % key)
		return data