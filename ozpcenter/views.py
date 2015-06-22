"""
Views
"""
import datetime
import logging

import django.contrib.auth
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework import filters
from rest_framework import viewsets
from rest_framework.response import Response

import ozpcenter.serializers as serializers
import ozpcenter.permissions as permissions
import ozpcenter.models as models
import ozpcenter.model_access as model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center')


class ProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsUser,)
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    filter_fields = ('highest_role',)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    filter_fields = ('title',)

class ContactTypeViewSet(viewsets.ModelViewSet):
    queryset = models.ContactType.objects.all()
    serializer_class = serializers.ContactTypeSerializer

class AgencyViewSet(viewsets.ModelViewSet):
    queryset = models.Agency.objects.all()
    serializer_class = serializers.AgencySerializer

class ContactViewSet(viewsets.ModelViewSet):
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactSerializer

class DocUrlViewSet(viewsets.ModelViewSet):
    queryset = models.DocUrl.objects.all()
    serializer_class = serializers.DocUrlSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer

class IntentViewSet(viewsets.ModelViewSet):
    queryset = models.Intent.objects.all()
    serializer_class = serializers.IntentSerializer

class ItemCommentViewSet(viewsets.ModelViewSet):
    queryset = models.ItemComment.objects.all()
    serializer_class = serializers.ItemCommentSerializer

class ApplicationLibraryEntryViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.ApplicationLibraryEntrySerializer

    def get_queryset(self):
        return  models.ApplicationLibraryEntry.objects.filter(
            owner__username=self.request.user.username)

class ListingViewSet(viewsets.ModelViewSet):
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

class ListingActivityViewSet(viewsets.ModelViewSet):
    queryset = models.ListingActivity.objects.all()
    serializer_class = serializers.ListingActivitySerializer

class RejectionListingViewSet(viewsets.ModelViewSet):
    queryset = models.RejectionListing.objects.all()
    serializer_class = serializers.RejectionListingSerializer

class ScreenshotViewSet(viewsets.ModelViewSet):
    queryset = models.Screenshot.objects.all()
    serializer_class = serializers.ScreenshotSerializer

class ListingTypeViewSet(viewsets.ModelViewSet):
    queryset = models.ListingType.objects.all()
    serializer_class = serializers.ListingTypeSerializer

class AccessControlViewSet(viewsets.ModelViewSet):
    queryset = models.AccessControl.objects.all()
    serializer_class = serializers.AccessControlSerializer

class IconViewSet(viewsets.ModelViewSet):
    queryset = models.Icon.objects.all()
    serializer_class = serializers.IconSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = models.Notification.objects.all()
    serializer_class = serializers.NotificationSerializer

class NotificationSelfViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.NotificationSerializer

    def get_queryset(self):
        """
        get all notifications that have not yet expired AND:
            * have not been dismissed by this user
            * are regarding a listing in this user's library (if the
                notification is listing-specific)
        """
        # TODO: add logic to ignore listing-specific notifications that are
        #   for listings not part of user's library
        return  models.Notification.objects.filter(
            expires_date__gt=datetime.datetime.now())

class DjangoUserViewSet(viewsets.ModelViewSet):
	queryset = django.contrib.auth.models.User.objects.all()
	serializer_class = serializers.DjangoUserSerializer


@api_view(['GET'])
@permission_classes((permissions.IsUser, ))
def metadataView(request):
	"""
	Metadata for the store including categories, agencies, contact types,
	intents, and listing types
	"""
	data = model_access.get_metadata()
	return Response(data)

@api_view(['GET'])
@permission_classes((permissions.IsUser, ))
def storefrontView(request):
    """
    Featured, recent, and most popular listings
    """
    data = model_access.get_storefront(request.user)
    serializer = serializers.StorefrontSerializer(data,
        context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes((permissions.IsUser, ))
def current_user(request):
    data = model_access.get_profile(request.user.username)
    serializer = serializers.ProfileSerializer(data,
        context={'request': request})
    return Response(serializer.data)

# TODO: POST on api/image (create/edit listing) w/ contentType and id fields

# TODO: POST on api/listing, with all fields in models.Listing. images have
# uuids that identify them. Response header has Location set to this Listing's
# url, which includes the listing's db id (not uuid) that was generated when
# the listing was created, and which can be used to query for this listing later
# (I guess)

# TODO: GET on api/listing/<#>/activity - get all activity
# for this listing, including (list of these):
# 	* listing data (title, agency, iconUrl, id)
# 	* author data (displayName, username, id)
#	* activityDate
#	* changeDetails - as a list
#	* action
#	* id

# TODO: PUT on api/listing/<#> - sends all the same data as the POST to this
#	url, but updates an existing Listing

# NOTE: when an app is Published (submitted for approval), it's the same PUT
#	request as above, but with the approvalStatus changed from IN_PROGRESS to PENDING
#	A new ListingAction is also created, action: SUBMITTED

# TODO: GET api/listing/search? - see model_access.search_listings for params

# TODO: GET api/profile?role=ORG_STEWARD for view (shown on create/edit listing page)

# TODO DELETE api/listing/<id>

# TODO: GET api/listing/<id>/itemComment get all reviews for the listing

# TODO: POST api/listing/<id>/itemComment - create a review

# TODO: PUT api/listing/<id>/itemComment/<id> - edit a review

# TODO: DELETE api/listing/<id>/itemComment/<id> - delete a review

# TODO: POST api/profile/self/library - add listing to library (bookmark)
#	params: listing id

# TODO: DELETE api/profile/self/library/<id> - unbookmark a listing

# TODO: GET api/listing/activity - params: offset, max

# TODO: GET api/listing - params: approvalStatus, offset, max, org, enabled

# TODO: CRUD for Categories, ContactTypes, Intents, Organizations, Stewards, AccessControls, and Notifications

# TODO: Identify endpoints used by IWC
