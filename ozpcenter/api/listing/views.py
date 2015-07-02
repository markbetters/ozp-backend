"""
Views
"""
import logging

from rest_framework import filters
from rest_framework import viewsets

import ozpcenter.api.listing.serializers as serializers
import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class ListingTypeViewSet(viewsets.ModelViewSet):
    queryset = models.ListingType.objects.all()
    serializer_class = serializers.ListingTypeSerializer

class ListingActivityViewSet(viewsets.ModelViewSet):
    queryset = models.ListingActivity.objects.all()
    serializer_class = serializers.ListingActivitySerializer

class RejectionListingViewSet(viewsets.ModelViewSet):
    queryset = models.RejectionListing.objects.all()
    serializer_class = serializers.RejectionListingSerializer

class ScreenshotViewSet(viewsets.ModelViewSet):
    queryset = models.Screenshot.objects.all()
    serializer_class = serializers.ScreenshotSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class ListingViewSet(viewsets.ModelViewSet):
    """
    Listings
    """
    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.ListingSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('title', 'description', 'description_short',)

    def get_queryset(self):
        filter_params = {}
        categories = self.request.query_params.getlist('categories', False)
        agencies = self.request.query_params.getlist('agencies', False)
        listing_types = self.request.query_params.getlist('listing_types', False)
        limit = self.request.query_params.get('limit', False)
        offset = self.request.query_params.get('offset', False)
        if categories:
            filter_params['categories'] = categories
        if agencies:
            filter_params['agencies'] = agencies
        if listing_types:
            filter_params['listing_types'] = listing_types
        if limit:
            filter_params['limit'] = limit
        if offset:
            filter_params['offset'] = offset


        return model_access.filter_listings(self.request.user.username,
            filter_params)

    def list(self, request):
        """
        ---
        # YAML (must be separated by `---`)

        omit_serializer: false

        parameters:
            - name: categories
              description: List of category names (AND logic)
              required: false
              paramType: query
              allowMultiple: true
            - name: agencies
              description: List of agencies
              paramType: query
            - name: listing_types
              description: List of application types
              paramType: query
            - name: limit
              description: Max number of listings to retrieve
              paramType: query
            - name: offset
              description: Offset
              paramType: query

        responseMessages:
            - code: 401
              message: Not authenticated
        """
        return super(ListingViewSet, self).list(self, request)