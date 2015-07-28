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

from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import filters
from rest_framework import viewsets
from rest_framework.response import Response

import ozpcenter.api.listing.serializers as serializers
import ozpcenter.permissions as permissions
import ozpcenter.models as models
import ozpcenter.api.listing.model_access as model_access
import ozpcenter.model_access as generic_model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class ContactViewSet(viewsets.ModelViewSet):
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactSerializer

class DocUrlViewSet(viewsets.ModelViewSet):
    queryset = models.DocUrl.objects.all()
    serializer_class = serializers.DocUrlSerializer

class ItemCommentViewSet(viewsets.ModelViewSet):
    """
    Item comments (reviews) for a given listing

    The unique_together contraints make it difficult to use the standard
    Serializer classes (see the Note here:
        http://www.django-rest-framework.org/api-guide/serializers/#specifying-read-only-fields)

    For that reason, we forego using Serializers for POST and PUT
    """
    queryset = models.ItemComment.objects.all()
    serializer_class = serializers.ItemCommentSerializer

    def list(self, request, listing_pk=None):
        # TODO: enforce access control
        queryset = self.queryset.filter(listing=listing_pk)
        serializer = serializers.ItemCommentSerializer(queryset, many=True,
            context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None, listing_pk=None):
        # TODO: enforce access control
        queryset = self.queryset.get(pk=pk, listing=listing_pk)
        serializer = serializers.ItemCommentSerializer(queryset,
            context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, pk=None, listing_pk=None):
        # TODO: permission check. either the current user must be the
        #   author of this item_comment, or the user must be an Org Steward
        #   or higher
        queryset = self.queryset
        item_comment = get_object_or_404(queryset, pk=pk)
        item_comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, listing_pk=None):
        """
        Create a new item_comment
        """
        logger.info('create itemComment. listing_pk: %s' % listing_pk)
        author = generic_model_access.get_profile(
            request.user.username)
        # TODO: check that this user has access to the given listing
        try:
            listing = models.Listing.objects.get(id=listing_pk)
        except:
            return Response('Invalid listing',
                status=status.HTTP_400_BAD_REQUEST)

        # TODO: validate, raise errors as needed
        try:
            rate = int(request.data['rate'])
            text = request.data['text']
        except:
            return Response('Bad request to create new item_comment',
                status=status.HTTP_400_BAD_REQUEST)

        comment = models.ItemComment(listing=listing, author=author,
            rate=rate, text=text)
        comment.save()
        output = {"rate": rate, "text": text, "author": author.id,
            "listing": listing.id, "id": comment.id}
        return Response(output, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, listing_pk=None):
        """
        Update an existing item_comment
        """
        logger.info('update itemComment. listing_pk: %s' % listing_pk)

        try:
            instance = models.ItemComment.objects.get(id=pk)
        except models.ItemComment.DoesNotExist:
            return Response('Invalid item comment',
                status=status.HTTP_400_BAD_REQUEST)


        # TODO: make sure current user is owner of this comment OR
        #   current user is org steward or above

        # TODO: validate, raise errors as needed
        try:
            rate = request.data.get('rate', instance.rate)
            text = request.data.get('text', instance.text)
        except:
            return Response('Bad request to create new item_comment',
                status=status.HTTP_400_BAD_REQUEST)

        instance.rate = rate
        instance.text = text
        instance.save()
        output = {"rate": instance.rate, "text": instance.text,
            "author": instance.author.id,
            "listing": instance.listing.id, "id": instance.id}
        return Response(output, status=status.HTTP_200_OK)


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
    Get all listings this user can see
    """
    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.ListingSerializer

    def get_queryset(self):
        user = generic_model_access.get_profile(self.request.user.username)
        return models.Listing.objects.for_user(
            self.request.user.username).all()

    def list(self, request):
        return super(ListingViewSet, self).list(self, request)

class ListingUserViewSet(viewsets.ModelViewSet):
    """
    Get all listings owned by this user
    """
    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.ListingSerializer

    def get_queryset(self):
        user = generic_model_access.get_profile(self.request.user.username)
        return models.Listing.objects.for_user(
            self.request.user.username).filter(
                owners__in=[user.id])

    def list(self, request):
        return super(ListingUserViewSet, self).list(self, request)


class ListingSearchViewSet(viewsets.ModelViewSet):
    """
    Search for listings
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
            - name: search
              description: Text to search
              paramType: query
            - name: category
              description: List of category names (AND logic)
              required: false
              paramType: query
              allowMultiple: true
            - name: agency
              description: List of agencies
              paramType: query
            - name: type
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