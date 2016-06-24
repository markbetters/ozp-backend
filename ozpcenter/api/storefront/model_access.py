"""
Storefront and Metadata Model Access
"""
import logging

from django.db.models.functions import Lower
from django.core.cache import cache
from ozpcenter import models
import ozpcenter.api.storefront.serializers as serializers

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


def get_storefront(username):
    """
    Returns data for /storefront api invocation including:
        * featured listings (max=12?)
        * recent (new) listings (max=24?)
        * most popular listings (max=36?)

    NOTE: think about adding Bookmark status to this later on
    """
    user = models.Profile.objects.get(user__username=username)  # flake8: noqa TODO: Is Necessary? - Variable not being used in method
    try:
        # get featured listings
        featured_listings = models.Listing.objects.for_user(
            username).filter(
                is_featured=True,
                approval_status=models.Listing.APPROVED,
                is_enabled=True,
                is_deleted=False)[:12]

        # get recent listings
        recent_listings = models.Listing.objects.for_user(
            username).order_by(
                '-approved_date').filter(
                    approval_status=models.Listing.APPROVED,
                    is_enabled=True,
                    is_deleted=False)[:24]

        # get most popular listings via a weighted average
        most_popular_listings = models.Listing.objects.for_user(
            username).filter(
                approval_status=models.Listing.APPROVED,
                is_enabled=True,
                is_deleted=False).order_by('-avg_rate', '-total_reviews')[:36]

        featured_listings = serializers.ListingSerializer.setup_eager_loading(featured_listings)
        recent_listings = serializers.ListingSerializer.setup_eager_loading(recent_listings)
        most_popular_listings = serializers.ListingSerializer.setup_eager_loading(most_popular_listings)

        data = {
            'featured': featured_listings,
            'recent': recent_listings,
            'most_popular': most_popular_listings
        }
    except Exception as e:
        return {'error': True, 'msg': 'Error getting storefront: {0!s}'.format(str(e))}
    return data


def values_query_set_to_dict(vqs):
    return [item for item in vqs]

def get_metadata(username):
    """
    Returns metadata including:
        * categories
        * organizations (agencies)
        * listing types
        * intents
        * contact types

    Key: metadata
    """
    try:
        data = {}
        data['categories'] = values_query_set_to_dict(models.Category.objects.all().values(
            'title', 'description').order_by(Lower('title')))


        data['listing_types'] = values_query_set_to_dict(models.ListingType.objects.all().values(
            'title', 'description'))
        data['agencies'] = values_query_set_to_dict(models.Agency.objects.all().values(
            'title', 'short_name', 'icon', 'id'))
        data['contact_types'] = values_query_set_to_dict(models.ContactType.objects.all().values(
            'name', 'required'))
        data['intents'] = values_query_set_to_dict(models.Intent.objects.all().values(
            'action', 'media_type', 'label', 'icon', 'id'))

        # return icon/image urls instead of the id and get listing counts
        for i in data['agencies']:
            # i['icon'] = models.Image.objects.get(id=i['icon']).image_url()
            # i['icon'] = '/TODO'
            i['listing_count'] = models.Listing.objects.for_user(
                username).filter(agency__title=i['title'],
                approval_status=models.Listing.APPROVED).count()

        for i in data['intents']:
            # i['icon'] = models.Image.objects.get(id=i['icon']).image_url()
            i['icon'] = '/TODO'
        return data
    except Exception as e:
        return {'error': True, 'msg': 'Error getting metadata: {0!s}'.format(str(e))}
