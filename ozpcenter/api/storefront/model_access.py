"""
Storefront and Metadata Model Access
"""
import logging

import msgpack
from django.db.models.functions import Lower
from ozpcenter import models
import ozpcenter.api.listing.serializers as listing_serializers

from ozpcenter.pipe import pipes
from ozpcenter.pipe import pipeline
from ozpcenter.recommend import recommend_utils

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
        # Get Recommended Listings for owner
        target_profile_recommended_entry = models.RecommendationsEntry.objects.filter(target_profile=profile).first()  # Get

        recommended_entry_data = msgpack.unpackb(target_profile_recommended_entry.recommendation_data)

        recommendation_combined_dict = {'profile': {}}

        for recommender_friendly_name in recommended_entry_data:
            recommender_name_data = recommended_entry_data[recommender_friendly_name]
            # print(recommender_name_data)
            recommender_name_weight = recommender_name_data[b'weight']
            recommender_name_recommendations = recommender_name_data[b'recommendations']

            for recommendation_tuple in recommender_name_recommendations:
                current_listing_id = recommendation_tuple[0]
                current_listing_score = recommendation_tuple[1]

                if current_listing_id in recommendation_combined_dict['profile']:
                    recommendation_combined_dict['profile'][current_listing_id] = recommendation_combined_dict['profile'][current_listing_id] + (current_listing_score * recommender_name_weight)
                else:
                    recommendation_combined_dict['profile'][current_listing_id] = current_listing_score * recommender_name_weight

        sorted_recommendations_combined_dict = recommend_utils.get_top_n_score(recommendation_combined_dict, 40)
        listing_ids_list = [entry[0] for entry in sorted_recommendations_combined_dict['profile']]

        recommended_listings_queryset = models.Listing.objects.for_user_organization_minus_security_markings(username).filter(pk__in=listing_ids_list,
                                                                                                                              approval_status=models.Listing.APPROVED,
                                                                                                                              is_enabled=True,
                                                                                                                              is_deleted=False).all()

        recommended_listings_objects = [recommendations_listing for recommendations_listing in recommended_listings_queryset]

        # Post security_marking check - lazy loading
        recommended_listings = pipeline.Pipeline(recommend_utils.ListIterator(recommended_listings_objects),
                                          [pipes.ListingPostSecurityMarkingCheckPipe(username),
                                           pipes.LimitPipe(10)]).to_list()

        # Get Featured Listings
        featured_listings_raw = models.Listing.objects.for_user_organization_minus_security_markings(
            username).filter(
                is_featured=True,
                approval_status=models.Listing.APPROVED,
                is_enabled=True,
                is_deleted=False)

        featured_listings_raw = listing_serializers.ListingSerializer.setup_eager_loading(featured_listings_raw)

        featured_listings = pipeline.Pipeline(recommend_utils.ListIterator([listing for listing in featured_listings_raw]),
                                          [pipes.ListingPostSecurityMarkingCheckPipe(username),
                                           pipes.LimitPipe(12)]).to_list()

        # Get Recent Listings
        recent_listings_raw = models.Listing.objects.for_user_organization_minus_security_markings(
            username).order_by('-approved_date').filter(
            approval_status=models.Listing.APPROVED,
            is_enabled=True,
            is_deleted=False)

        recent_listings_raw = listing_serializers.ListingSerializer.setup_eager_loading(recent_listings_raw)

        recent_listings = pipeline.Pipeline(recommend_utils.ListIterator([listing for listing in recent_listings_raw]),
                                          [pipes.ListingPostSecurityMarkingCheckPipe(username),
                                           pipes.LimitPipe(24)]).to_list()

        # Get most popular listings via a weighted average
        most_popular_listings_raw = models.Listing.objects.for_user_organization_minus_security_markings(
            username).filter(
                approval_status=models.Listing.APPROVED,
                is_enabled=True,
                is_deleted=False).order_by('-avg_rate', '-total_reviews')

        most_popular_listings_raw = listing_serializers.ListingSerializer.setup_eager_loading(most_popular_listings_raw)

        most_popular_listings = pipeline.Pipeline(recommend_utils.ListIterator([listing for listing in most_popular_listings_raw]),
                                          [pipes.ListingPostSecurityMarkingCheckPipe(username),
                                           pipes.LimitPipe(36)]).to_list()

        data = {
            'recommended': recommended_listings,
            'featured': featured_listings,
            'recent': recent_listings,
            'most_popular': most_popular_listings
        }
    except Exception:
        # raise Exception({'error': True, 'msg': 'Error getting storefront: {0!s}'.format(str(e))})
        raise  # Should be catch in the django framwork
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
            'id', 'title', 'description').order_by(Lower('title')))

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
