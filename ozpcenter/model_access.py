"""
Model (data) access methods

Should support memcache. Basically stuff like:

data = cache.get('stuff')
if data is None:
    data = list(Stuff.objects.all())
    cache.set('stuff', data)
return data

Think about Listing queries: must support private apps and classification
levels, which are user dependent. Possible keys:
storefront:org1:max_classification_level

Be sure to remove all non alpha-numeric characters from the key names and
make lower-case

Profle data: current_profile:username

Read https://docs.djangoproject.com/en/1.8/topics/cache/
"""
import logging
import re

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger(__name__)

def make_keysafe(key):
	"""
	given an input string, make it lower case and remove all non alpha-numeric
	characters so that it will be safe to use as a cache keyname
	"""
	return re.sub(r'\W+', '', key)


def get_storefront(username):
	"""
	Returns data for /storefront api invocation

	Key: storefront:<org_name>:<max_classification_level>
	"""
	pass


def get_current_profile(username):
	"""
	get a user's Profile

	Key: current_profile:<username>
	"""
	username = make_keysafe(username)

	data = cache.get('current_profile:%s' % username)
	if data is None:
		try:
			data = models.Profile.objects.get(username=username)
			cache.set('current_profile:%s' % username, data)
			logger.info('NOT getting data for key: current_profile:%s from cache' % username)
			return data
		except ObjectDoesNotExist:
			return None
	else:
		logger.info('GOT data for key: current_profile:%s from cache' % username)
		return data

