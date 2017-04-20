"""
Storefront and Metadata Views for the Discovery page

These are GET only views for retrieving a) metadata (categories, organizations,
etc) and b) the apps displayed in the storefront (featured, recent, and
most popular)

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

import logging

from django.conf import settings
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
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


@api_view(['GET'])
@permission_classes((permissions.IsUser, ))
def StorefrontView(request):
    """
    Featured, recent, and most popular listings
    ---
    serializer: ozpcenter.api.storefront.serializers.StorefrontSerializer
    """
    # return Response(model_access.get_user_listings(request.user))

    data = model_access.get_storefront(request.user, True)
    serializer = serializers.StorefrontSerializer(data,
        context={'request': request})

    request_username = request.user.username
    cache_key = 'storefront-{0}'.format(request_username)
    cache_data = cache.get(cache_key)
    if not cache_data:
        cache_data = serializer.data
        cache.set(cache_key, cache_data, timeout=settings.GLOBAL_SECONDS_TO_CACHE_DATA)
    return Response(cache_data)
