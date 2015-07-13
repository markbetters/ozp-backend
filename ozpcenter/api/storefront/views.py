"""
Storefront views for the Discovery page

These are GET only views for retrieving a) metadata (categories, organizations,
etc) and b) the apps displayed in the storefront (featured, recent, and
most popular)
"""
import logging

from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework import generics, status
from rest_framework.response import Response

import ozpcenter.api.storefront.serializers as serializers
import ozpcenter.permissions as permissions
import ozpcenter.models as models
import ozpcenter.api.storefront.model_access as model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

@api_view(['GET'])
@permission_classes((permissions.IsUser, ))
def MetadataView(request):
	"""
	Metadata for the store including categories, agencies, contact types,
	intents, and listing types
	"""
	data = model_access.get_metadata()
	return Response(data)

@api_view(['GET'])
@permission_classes((permissions.IsUser, ))
def StorefrontView(request):
    """
    Featured, recent, and most popular listings
    ---
    serializer: ozpcenter.api.storefront.serializers.StorefrontSerializer
    """
    data = model_access.get_storefront(request.user)
    serializer = serializers.StorefrontSerializer(data,
        context={'request': request})
    return Response(serializer.data)