"""
Storefront and Metadata Views for the Discovery page

These are GET only views for retrieving a) metadata (categories, organizations,
etc) and b) the apps displayed in the storefront (featured, recent, and
most popular)
"""

import logging

from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework import viewsets
from rest_framework.response import Response

from ozpcenter import permissions
import ozpcenter.api.storefront.model_access as model_access
import ozpcenter.api.storefront.serializers as serializers

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


@api_view(['GET'])
@permission_classes((permissions.IsUser, ))
def MetadataView(request):
    """
    Metadata for the store including categories, agencies, contact types,
    intents, and listing types
    """
    request_username = request.user.username
    data = model_access.get_metadata(request_username)
    return Response(data)


class StorefrontViewSet(viewsets.ViewSet):
    """
    TODO: Simply Recommended sections

    Access Control
    ===============
    - All users can view

    URIs
    ======
    GET /api/storefront
    Summary:
        Get the Storefront view
    Response:
        200 - Successful operation - [StorefrontSerializer]
    """
    permission_classes = (permissions.IsUser,)

    def list(self, request):
        """
        Recommended, Featured, recent, and most popular listings
        ---
        serializer: ozpcenter.api.storefront.serializers.StorefrontSerializer
        """
        # return Response(model_access.get_storefront_new(request.user, request))
        data, extra_data = model_access.get_storefront(request.user, True)
        serializer = serializers.StorefrontSerializer(data,
            context={'request': request})

        serialized_data = serializer.data

        # extra_data = {'recommended_entry_data': {'Baseline': {'ms_took': 1204.51953125, 'weight': 1.0, 'recommendations': [
        #     [11, 8.5], [112, 8.0], [85, 7.0], [86, 7.0], [87, 7.0], [88, 7.0], [89, 7.0], [90, 7.0], [62, 6.0],
        #     [81, 6.0], [21, 5.5], [1, 5.0], [111, 5.0], [113, 5.0], [114, 5.0], [64, 4.0], [66, 4.0], [68, 4.0],
        #     [70, 4.0], [72, 4.0]]}}}
        # TO
        # {listing_id#1 : {friendly_name#1: {'raw_score': score#1, 'weight': weight#1}
        #                  friendly_name#2: {'raw_score': score#1, 'weight': weight#1}},
        # listing_id#2 : {friendly_name#1: {'raw_score': score#1, 'weight': weight#1},
        #                  friendly_name#2: {'raw_score': score#1, 'weight': weight#1}}
        # }
        # Insert into each serialized listing into serialized_data
        if 'recommended_entry_data' in extra_data:
            recommended_entry_data = extra_data['recommended_entry_data']

            listing_recommend_data = {}

            for friendly_name in recommended_entry_data:
                current_weight = recommended_entry_data[friendly_name]['weight']
                recommendations = recommended_entry_data[friendly_name]['recommendations']

                for current_recommendations in recommendations:
                    current_listing = current_recommendations[0]
                    current_score = current_recommendations[1]

                    if current_listing in listing_recommend_data:
                        listing_recommend_data[current_listing][friendly_name] = {'raw_score': current_score, 'weight': current_weight}
                    else:
                        listing_recommend_data[current_listing] = {}
                        listing_recommend_data[current_listing][friendly_name] = {'raw_score': current_score, 'weight': current_weight}

            recommendation_serialized_list = []

            for serialized_listing in serialized_data['recommended']:
                serialized_listing_id = serialized_listing['id']

                serialized_listing['_score'] = listing_recommend_data[serialized_listing_id]

                recommendation_serialized_list.append(serialized_listing)

            serialized_data['recommended'] = recommendation_serialized_list

        # request_username = request.user.username
        # cache_key = 'storefront-{0}'.format(request_username)
        # cache_data = cache.get(cache_key)
        # if not cache_data:
        #    cache_data = serializer.data
        #    cache.set(cache_key, cache_data, timeout=settings.GLOBAL_SECONDS_TO_CACHE_DATA)
        # return Response(cache_data)
        return Response(serialized_data)

    def retrieve(self, request, pk=None):
        # return Response(model_access.get_storefront_new(request.user, request))
        data, extra_data = model_access.get_storefront(request.user, True, pk)
        serializer = serializers.StorefrontSerializer(data,
            context={'request': request})

        serialized_data = serializer.data

        # extra_data = {'recommended_entry_data': {'Baseline': {'ms_took': 1204.51953125, 'weight': 1.0, 'recommendations': [
        #     [11, 8.5], [112, 8.0], [85, 7.0], [86, 7.0], [87, 7.0], [88, 7.0], [89, 7.0], [90, 7.0], [62, 6.0],
        #     [81, 6.0], [21, 5.5], [1, 5.0], [111, 5.0], [113, 5.0], [114, 5.0], [64, 4.0], [66, 4.0], [68, 4.0],
        #     [70, 4.0], [72, 4.0]]}}}
        # TO
        # {listing_id#1 : {friendly_name#1: {'raw_score': score#1, 'weight': weight#1}
        #                  friendly_name#2: {'raw_score': score#1, 'weight': weight#1}},
        # listing_id#2 : {friendly_name#1: {'raw_score': score#1, 'weight': weight#1},
        #                  friendly_name#2: {'raw_score': score#1, 'weight': weight#1}}
        # }
        # Insert into each serialized listing into serialized_data
        if 'recommended_entry_data' in extra_data:
            recommended_entry_data = extra_data['recommended_entry_data']

            listing_recommend_data = {}

            for friendly_name in recommended_entry_data:
                current_weight = recommended_entry_data[friendly_name]['weight']
                recommendations = recommended_entry_data[friendly_name]['recommendations']

                for current_recommendations in recommendations:
                    current_listing = current_recommendations[0]
                    current_score = current_recommendations[1]

                    if current_listing in listing_recommend_data:
                        listing_recommend_data[current_listing][friendly_name] = {'raw_score': current_score, 'weight': current_weight}
                    else:
                        listing_recommend_data[current_listing] = {}
                        listing_recommend_data[current_listing][friendly_name] = {'raw_score': current_score, 'weight': current_weight}

            recommendation_serialized_list = []

            for serialized_listing in serialized_data['recommended']:
                serialized_listing_id = serialized_listing['id']

                serialized_listing['_score'] = listing_recommend_data[serialized_listing_id]

                recommendation_serialized_list.append(serialized_listing)

            serialized_data['recommended'] = recommendation_serialized_list
        return Response(serialized_data)
