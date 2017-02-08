"""
Storefront and Metadata Model Access
"""
import logging

from django.db.models.functions import Lower
from ozpcenter import models
import ozpcenter.api.listing.serializers as listing_serializers

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


def get_storefront(username):
    """
    Returns data for /storefront api invocation including:
        * featured listings (max=12?)
        * recent (new) listings (max=24?)
        * most popular listings (max=36?)

    NOTE: think about adding Bookmark status to this later on

    Args:
        username

    Returns:
        {
            'featured': [Listing],
            'recent': [Listing],
            'most_popular': [Listing]
        }
    """
    profile = models.Profile.objects.get(user__username=username)
    try:
        # get recommended listing for owner
        # Ensure that the Listing are viewable by the current user
        recommended_listings_raw = models.RecommendationsEntry.objects.filter(target_profile=profile,
                                                                         listing__is_enabled=True,
                                                                         listing__approval_status=models.Listing.APPROVED,
                                                                         listing__is_deleted=False).order_by('-score')[:10]
        recommended_listings = [recommendations_entry.listing for recommendations_entry in recommended_listings_raw]

        # Get Featured Listings
        featured_listings = models.Listing.objects.for_user(
            username).filter(
                is_featured=True,
                approval_status=models.Listing.APPROVED,
                is_enabled=True,
                is_deleted=False)[:12]

        # Get Recent Listings
        recent_listings = models.Listing.objects.for_user(
            username).order_by(
                '-approved_date').filter(
                    approval_status=models.Listing.APPROVED,
                    is_enabled=True,
                    is_deleted=False)[:24]

        # Get most popular listings via a weighted average
        most_popular_listings = models.Listing.objects.for_user(
            username).filter(
                approval_status=models.Listing.APPROVED,
                is_enabled=True,
                is_deleted=False).order_by('-avg_rate', '-total_reviews')[:36]

        featured_listings = listing_serializers.ListingSerializer.setup_eager_loading(featured_listings)
        recent_listings = listing_serializers.ListingSerializer.setup_eager_loading(recent_listings)
        most_popular_listings = listing_serializers.ListingSerializer.setup_eager_loading(most_popular_listings)

        data = {
            'recommended': recommended_listings,
            'featured': featured_listings,
            'recent': recent_listings,
            'most_popular': most_popular_listings
        }
    except Exception as e:
        raise Exception({'error': True, 'msg': 'Error getting storefront: {0!s}'.format(str(e))})
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

        listing_titles = models.Listing.objects.for_user(username).filter(approval_status=models.Listing.APPROVED) \
            .filter(is_deleted=False, is_enabled=True).all()

        data['listing_titles'] = [record.get('title') for record in values_query_set_to_dict(listing_titles.values(
            'title'))]

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
