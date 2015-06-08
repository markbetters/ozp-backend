"""
Model (data) access methods

Should support caches. Basically stuff like:

data = cache.get('stuff')
if data is None:
    data = list(Stuff.objects.all())
    cache.set('stuff', data)
return data

Think about Listing queries: must support private apps and classification
levels, which are user dependent. Possible keys:
storefront:org1:max_classification_level


Read https://docs.djangoproject.com/en/1.8/topics/cache/
"""
import logging
import re

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

def make_keysafe(key):
	"""
	given an input string, make it lower case and remove all non alpha-numeric
	characters so that it will be safe to use as a cache keyname
	"""
	return re.sub(r'\W+', '', key)


def get_storefront(username):
	"""
	Returns data for /storefront api invocation including:
		* featured listings
		* recent (new) listings
		* most popular listings

	TODO: include bookmarked status or not?

	Key: storefront:<org_name>:<max_classification_level>
	"""
	pass

def get_metadata():
	"""
	Returns metadata including:
		* categories
		* organizations (agencies)
		* listing types
		* intents
		* contact types

	Key: metadata
	"""
	key = 'metadata'
	data = cache.get(key)
	if data is None:
		try:
			data = {}
			data['categories'] = models.Category.objects.all().values(
				'title', 'description')
			data['listing_types'] = models.ListingType.objects.all().values(
				'title', 'description')
			data['agencies'] = models.Agency.objects.all().values(
				'title', 'short_name', 'icon_url')
			data['contact_types'] = models.ContactType.objects.all().values(
				'name', 'required')
			data['intents'] = models.Intent.objects.all().values(
				'action', 'media_type', 'label', 'icon')

			cache.set(key, data)
		except Exception as e:
			return {'error': True, 'msg': 'Error getting metadata: %s' % str(e)}
	return data

def get_profile(username):
	"""
	get a user's Profile

	Key: current_profile:<username>
	"""
	username = make_keysafe(username)
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

def get_self(username):
	return get_profile()

def get_self_notifications(username):
	"""
	Get notifications for user

	Key: notifications:<username>
	"""
	pass

def get_self_application_library(username):
	"""
	Get the ApplicationLibrary for this user

	Key: app_library:<username>
	"""
	pass

def get_self_listings(username):
	"""
	Get the Listings that belong to this user

	Key: self_listings:<username>
	"""
	pass

def search_listings(username, search_params):
	"""
	Search for Listings

	Must respect private apps (only from user's agency) and user's
	max_classification_level

	search_params can contain:
		* text (full-text search, case insensitve)
		* categories (AND logic)
		* agencies (OR logic)
		* listing_types (OR logic)
		* offset (for pagination)

	Too many variations to cache

	TODO: use elasticsearch for text searches
	"""
	pass

def get_listings(username):
	"""
	Get Listings this user can see

	This requires filtering out:
	a) listings that are private to an organization this user does not belong to
	b) listings with classifications above that of this user

	Key: listings:<username>
	"""
	username = make_keysafe(username)
	key = 'listings:%s' % username
	data = cache.get(key)
	if data is None:
		try:
			user = get_profile(username)
			user_orgs = user.organizations.all()
			user_orgs = [i.title for i in user_orgs]
			# get all agencies for which this user is not a member
			exclude_orgs = models.Agency.objects.exclude(title__in=user_orgs)
			data = models.Listing.objects.exclude(is_private=True,
				agency__in=exclude_orgs)
			cache.set(key, data)
			return data
		except ObjectDoesNotExist:
			return None
	else:
		return data



