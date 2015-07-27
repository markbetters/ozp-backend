"""
Views

TODO: POST on api/listing, with all fields in models.Listing. images have
uuids that identify them. Response header has Location set to this Listing's
url, which includes the listing's db id (not uuid) that was generated when
the listing was created, and which can be used to query for this listing later
(I guess)

TODO: GET on api/listing/<#>/activity - get all activity
for this listing, including (list of these):
  * listing data (title, agency, iconUrl, id)
  * author data (displayName, username, id)
  * activityDate
  * changeDetails - as a list
  * action
  * id

TODO: PUT on api/listing/<#> - sends all the same data as the POST to this
  url, but updates an existing Listing

NOTE: when an app is Published (submitted for approval), it's the same PUT
  request as above, but with the approvalStatus changed from IN_PROGRESS to PENDING
  A new ListingAction is also created, action: SUBMITTED

TODO: GET api/listing/search? - see model_access.search_listings for params

TODO DELETE api/listing/<id>

TODO: GET api/listing/<id>/itemComment get all reviews for the listing

TODO: POST api/listing/<id>/itemComment - create a review

TODO: PUT api/listing/<id>/itemComment/<id> - edit a review

TODO: DELETE api/listing/<id>/itemComment/<id> - delete a review

TODO: GET api/listing/activity - params: offset, max

TODO: GET api/listing - params: approvalStatus, offset, max, org, enabled
"""
import logging

from rest_framework import filters
from rest_framework import viewsets

import ozpcenter.api.listing.serializers as serializers
import ozpcenter.permissions as permissions
import ozpcenter.models as models
import ozpcenter.api.listing.model_access as model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class ContactViewSet(viewsets.ModelViewSet):
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactSerializer

class DocUrlViewSet(viewsets.ModelViewSet):
    queryset = models.DocUrl.objects.all()
    serializer_class = serializers.DocUrlSerializer

class ItemCommentViewSet(viewsets.ModelViewSet):
    queryset = models.ItemComment.objects.all()
    serializer_class = serializers.ItemCommentSerializer

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


class ListingSearchViewSet(viewsets.ModelViewSet):
    """
    Listings
    """
    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.ListingSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('title', 'description', 'description_short',)

    def get_queryset(self):
        filter_params = {}
        categories = self.request.query_params.getlist('category', False)
        agencies = self.request.query_params.getlist('agency', False)
        listing_types = self.request.query_params.getlist('type', False)
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
        return super(ListingSearchViewSet, self).list(self, request)