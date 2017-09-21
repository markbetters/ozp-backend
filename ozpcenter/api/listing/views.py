"""
Listing Views
"""
import logging
import operator

from django.shortcuts import get_object_or_404
from django.db.models import Min
from django.db.models.functions import Lower
from rest_framework import filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import list_route

#  from ozpcenter import pagination  # TODO: Is Necessary?
from ozpcenter import permissions
from ozpcenter.pipe import pipes
from ozpcenter.pipe import pipeline
from ozpcenter.recommend import recommend_utils
import ozpcenter.api.listing.model_access as model_access
import ozpcenter.api.listing.serializers as serializers
import ozpcenter.model_access as generic_model_access
import ozpcenter.api.listing.model_access_es as model_access_es

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class ContactViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for getting all contacts for a given listing

    Access Control
    ===============
    - All users can view

    URIs
    ======
    GET /api/contact
    Summary:
        Get a list of all system-wide Contact entries
    Response:
        200 - Successful operation - [ContactSerializer]

    POST /api/contact/
    Summary:
        Add a Contact
    Request:
        data: ContactSerializer Schema
    Response:
        200 - Successful operation - ContactSerializer

    GET /api/contact/{pk}
    Summary:
        Find a Contact Entry by ID
    Response:
        200 - Successful operation - ContactSerializer

    PUT /api/contact/{pk}
    Summary:
        Update a Contact Entry by ID

    PATCH /api/contact/{pk}
    Summary:
        Update (Partial) a Contact Entry by ID

    DELETE /api/contact/{pk}
    Summary:
        Delete a Contact Entry by ID
    """

    permission_classes = (permissions.IsUser,)
    queryset = model_access.get_all_contacts()
    serializer_class = serializers.ContactSerializer


class DocUrlViewSet(viewsets.ModelViewSet):
    """
    TODO: Remove?
    """

    permission_classes = (permissions.IsUser,)
    queryset = model_access.get_all_doc_urls()
    serializer_class = serializers.DocUrlSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Reviews for a given listing

    The unique_together contraints on models.Review make it difficult to
    use the standard Serializer classes (see the Note here:
        http://www.django-rest-framework.org/api-guide/serializers/#specifying-read-only-fields)

    Primarily for that reason, we forgo using Serializers for POST and PUT
    actions

    ModelViewSet for getting all Reviews for a given listing

    Access Control
    ===============
    - All users can view

    URIs
    ======
    GET /api/listing/{pk}/review
    Summary:
        Find a Review Entry by ID
    Response:
        200 - Successful operation - ReviewSerializer

    DELETE /api/listing/{pk}/review
    Summary:
        Delete a Review Entry by ID
    """

    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.ReviewSerializer
    filter_backends = (filters.OrderingFilter,)
    pagination_class = pagination.ReviewLimitOffsetPagination

    ordering_fields = ('id', 'listing', 'text', 'rate', 'edited_date', 'created_date')
    ordering = ('-created_date')

    def get_queryset(self):
        return model_access.get_reviews(self.request.user.username)

    def list(self, request, listing_pk=None):
        queryset = self.get_queryset().filter(listing=listing_pk, review_parent__isnull=True)
        queryset = self.filter_queryset(queryset)
        # it appears that because we override the queryset here, we must
        # manually invoke the pagination methods
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ReviewSerializer(page, context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.ReviewSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None, listing_pk=None):
        queryset = self.get_queryset().get(pk=pk, listing=listing_pk)
        serializer = serializers.ReviewSerializer(queryset, context={'request': request})
        return Response(serializer.data)

    def create(self, request, listing_pk=None):
        """
        Create a new review
        """
        listing = model_access.get_listing_by_id(request.user.username, listing_pk, True)

        serializer = serializers.ReviewSerializer(data=request.data, context={'request': request, 'listing': listing}, partial=True)
        if not serializer.is_valid():
            logger.error('{0!s}'.format(serializer.errors), extra={'request': request})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, listing_pk=None):
        """
        Update an existing review
        """
        listing = model_access.get_listing_by_id(request.user.username, listing_pk, True)
        review = model_access.get_review_by_id(pk)

        serializer = serializers.ReviewSerializer(review, data=request.data, context={'request': request, 'listing': listing}, partial=True)
        if not serializer.is_valid():
            logger.error('{0!s}'.format(serializer.errors), extra={'request': request})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None, listing_pk=None):
        queryset = self.get_queryset()
        review = get_object_or_404(queryset, pk=pk)
        model_access.delete_listing_review(request.user.username, review)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SimilarViewSet(viewsets.ModelViewSet):
    """
    Similar Apps for a given listing

    # TODO (Rivera 2017-2-22) Implement Similar Listing Algorithm

    Primarily for that reason, we forgo using Serializers for POST and PUT
    actions

    ModelViewSet for getting all Similar Apps for a given listing

    Access Control
    ===============
    - All users can view

    URIs
    ======
    GET /api/listing/{pk}/similar
    Summary:
        Find a Similar App Entry by ID
    Response:
        200 - Successful operation - ListingSerializer
    """

    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.ListingSerializer
    # pagination_class = pagination.StandardPagination

    def get_queryset(self, listing_pk):
        approval_status = self.request.query_params.get('approval_status', None)
        # org = self.request.query_params.get('org', None)
        orgs = self.request.query_params.getlist('org', False)
        enabled = self.request.query_params.get('enabled', None)
        ordering = self.request.query_params.getlist('ordering', None)
        if enabled:
            enabled = enabled.lower()
            if enabled in ['true', '1']:
                enabled = True
            else:
                enabled = False

        listings = model_access.get_similar_listings(self.request.user.username, listing_pk)

        if approval_status:
            listings = listings.filter(approval_status=approval_status)
        if orgs:
            listings = listings.filter(agency__title__in=orgs)
        if enabled is not None:
            listings = listings.filter(is_enabled=enabled)
        # have to handle this case manually because the ordering includes an app multiple times
        # if there are multiple owners. We instead do sorting by case insensitive compare of the
        # app owner that comes first alphabetically
        param = [s for s in ordering if 'owners__display_name' == s or '-owners__display_name' == s]
        if ordering is not None and param:
            orderby = 'min'
            if param[0].startswith('-'):
                orderby = '-min'
            listings = listings.annotate(min=Min(Lower('owners__display_name'))).order_by(orderby)
            self.ordering = None
        return listings

    def list(self, request, listing_pk=None):
        queryset = self.filter_queryset(self.get_queryset(listing_pk))
        serializer = serializers.ListingSerializer(queryset, context={'request': request}, many=True)

        similar_listings = pipeline.Pipeline(recommend_utils.ListIterator(serializer.data),
                                          [pipes.ListingDictPostSecurityMarkingCheckPipe(self.request.user.username),
                                           pipes.LimitPipe(10)]).to_list()

        r = Response(similar_listings)
        return r


class ListingTypeViewSet(viewsets.ModelViewSet):
    """
    Listing Types

    ModelViewSet for getting all Listing Types for a given listing

    Access Control
    ===============
    - All users can view

    URIs
    ======
    GET /api/listingtype
    Summary:
        Get a list of all system-wide ListingType entries
    Response:
        200 - Successful operation - [ListingTypeSerializer]

    POST /api/listingtype
    Summary:
        Add a ListingType
    Request:
        data: ListingTypeSerializer Schema
    Response:
        200 - Successful operation - ListingTypeSerializer

    GET /api/listingtype/{pk}
    Summary:
        Find a ListingType Entry by ID
    Response:
        200 - Successful operation - ListingTypeSerializer

    PUT /api/listingtype/{pk}
    Summary:
        Update a ListingType Entry by ID

    PATCH /api/listingtype/{pk}
    Summary:
        Update (Partial) a ListingType Entry by ID

    DELETE /api/listingtype/{pk}
    Summary:
        Delete a ListingType Entry by ID
    """
    permission_classes = (permissions.IsUser,)
    queryset = model_access.get_all_listing_types()
    serializer_class = serializers.ListingTypeSerializer


class ListingUserActivitiesViewSet(viewsets.ModelViewSet):
    """
    ListingUserActivitiesViewSet endpoints are read-only

    ModelViewSet for getting all Listing User Activities for a given listing

    Access Control
    ===============
    - All users can view

    URIs
    ======
    GET /api/self/listings/activity
    Summary:
        Get a list of all system-wide ListingUserActivities entries
    Response:
        200 - Successful operation - [ListingActivitySerializer]

    GET /api/self/listings/activity/{pk}
    Summary:
        Find a Listing User Activity Entry by ID
    Response:
        200 - Successful operation - ListingActivitySerializer
    """

    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.ListingActivitySerializer

    def get_queryset(self):
        return model_access.get_listing_activities_for_user(
            self.request.user.username)

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ListingActivitySerializer(page,
                context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.ListingActivitySerializer(queryset,
            context={'request': request}, many=True)
        return Response(serializer.data)


class ListingActivitiesViewSet(viewsets.ModelViewSet):
    """
    ListingActivity endpoints are read-only

    ModelViewSet for getting all Listing Activities for a given listing

    Access Control
    ===============
    - AppsMallSteward can view

    URIs
    ======
    GET /api/listings/activity
    Summary:
        Get a list of all system-wide ListingActivities entries
    Response:
        200 - Successful operation - [ListingActivitySerializer]

    GET /api/listings/activity/{pk}
    Summary:
        Find a Listing User Activity Entry by ID
    Response:
        200 - Successful operation - ListingActivitySerializer
    """
    permission_classes = (permissions.IsOrgSteward,)
    serializer_class = serializers.ListingActivitySerializer

    def get_queryset(self):
        return model_access.get_all_listing_activities(
            self.request.user.username).order_by('-activity_date')

    def list(self, request):
        queryset = self.get_queryset()
        # it appears that because we override the queryset here, we must
        # manually invoke the pagination methods
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ListingActivitySerializer(page,
                context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.ListingActivitySerializer(queryset,
            context={'request': request}, many=True)
        return Response(serializer.data)


class ListingActivityViewSet(viewsets.ModelViewSet):
    """
    ListingActivity endpoints are read-only

    ModelViewSet for getting all Listing Activities for a given listing

    Access Control
    ===============
    - All users can view

    URIs
    ======
    GET /api/listing/{pk}/activity
    Summary:
        Find a Listing Activity Entry by ID
    Response:
        200 - Successful operation - ListingActivitySerializer
    """
    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.ListingActivitySerializer

    def get_queryset(self):
        return model_access.get_all_listing_activities(
            self.request.user.username).order_by('-activity_date')

    def list(self, request, listing_pk=None):
        queryset = self.get_queryset().filter(listing=listing_pk)
        # it appears that because we override the queryset here, we must
        # manually invoke the pagination methods
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ListingActivitySerializer(page,
                context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.ListingActivitySerializer(queryset,
            context={'request': request}, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, listing_pk=None):
        queryset = self.get_queryset().get(pk=pk, listing=listing_pk)
        serializer = serializers.ListingActivitySerializer(queryset,
            context={'request': request})
        return Response(serializer.data)


class ListingRejectionViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for getting all Listing Rejections

    Access Control
    ===============
    - AppsMallSteward can view

    URIs
    ======
    POST /api/listing/{pk}/rejection
    Summary:
        Add a ListingRejection
    Request:
        data: ListingRejectionSerializer Schema
    Response:
        200 - Successful operation - ListingActivitySerializer

    GET /api/listing/{pk}/rejection
    Summary:
        Find a ListingRejection Entry by ID
    Response:
        200 - Successful operation - ListingActivitySerializer
    """

    permission_classes = (permissions.IsOrgStewardOrReadOnly,)
    serializer_class = serializers.ListingActivitySerializer

    def get_queryset(self):
        queryset = model_access.get_rejection_listings(
            self.request.user.username)
        return queryset

    def list(self, request, listing_pk=None):
        queryset = self.get_queryset().filter(listing__id=listing_pk)
        serializer = serializers.ListingActivitySerializer(queryset,
            context={'request': request}, many=True)
        return Response(serializer.data)

    def create(self, request, listing_pk=None):
        try:
            user = generic_model_access.get_profile(request.user.username)
            listing = model_access.get_listing_by_id(request.user.username,
                listing_pk)
            rejection_description = request.data['description']
            listing = model_access.reject_listing(user, listing,
                rejection_description)
            return Response(data={"listing": {"id": listing.id}},
                status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error('Exception: {}'.format(e), extra={'request': request})
            return Response("Error rejecting listing",
                    status=status.HTTP_400_BAD_REQUEST)


class ScreenshotViewSet(viewsets.ModelViewSet):
    """
    Listing Types

    ModelViewSet for getting all Screenshots for a given listing

    Access Control
    ===============
    - All users can view

    URIs
    ======
    GET /api/screenshot/
    Summary:
        Get a list of all system-wide Screenshot entries
    Response:
        200 - Successful operation - [ScreenshotSerializer]

    POST /api/screenshot/
    Summary:
        Add a Screenshot
    Request:
        data: ScreenshotSerializer Schema
    Response:
        200 - Successful operation - ScreenshotSerializer

    GET /api/screenshot/{pk}
    Summary:
        Find a Screenshot Entry by ID
    Response:
        200 - Successful operation - ScreenshotSerializer

    PUT /api/screenshot/{pk}
    Summary:
        Update a Screenshot Entry by ID

    PATCH /api/screenshot/{pk}
    Summary:
        Update (Partial) a Screenshot Entry by ID

    DELETE /api/screenshot/{pk}
    Summary:
        Delete a Screenshot Entry by ID
    """

    permission_classes = (permissions.IsUser,)
    queryset = model_access.get_all_screenshots()
    serializer_class = serializers.ScreenshotSerializer


class TagViewSet(viewsets.ModelViewSet):
    """
    Listing Types

    ModelViewSet for getting all Tags for a given listing

    Access Control
    ===============
    - All users can view

    URIs
    ======
    GET /api/tag/
    Summary:
        Get a list of all system-wide Tag entries
    Response:
        200 - Successful operation - [TagSerializer]

    POST /api/tag/
    Summary:
        Add a Tag
    Request:
        data: TagSerializer Schema
    Response:
        200 - Successful operation - TagSerializer

    GET /api/tag/{pk}
    Summary:
        Find a Tag Entry by ID
    Response:
        200 - Successful operation - TagSerializer

    PUT /api/tag/{pk}
    Summary:
        Update a Tag Entry by ID

    PATCH /api/tag/{pk}
    Summary:
        Update (Partial) a Tag Entry by ID

    DELETE /api/tag/{pk}
    Summary:
        Delete a Tag Entry by ID
    """

    permission_classes = (permissions.IsUser,)
    queryset = model_access.get_all_tags()
    serializer_class = serializers.TagSerializer


class ListingViewSet(viewsets.ModelViewSet):
    """
    Get all listings this user can see

    Listing Types

    ModelViewSet for getting all Listings

    Access Control
    ===============
    - All users can view

    URIs
    ======
    GET /api/listing
    Summary:
        Get a list of all system-wide Listings
    Response:
        200 - Successful operation - [ListingSerializer]

    POST /api/listing/
    Summary:
        Add a Listing
    Request:
        data: ListingSerializer Schema
    Response:
        200 - Successful operation - ListingSerializer

    GET /api/listing/{pk}
    Summary:
        Find a Listing Entry by ID
    Response:
        200 - Successful operation - ListingSerializer

    PUT /api/listing/{pk}
    Summary:
        Update a Listing Entry by ID

    PATCH /api/listing/{pk}
    Summary:
        Update (Partial) a Listing Entry by ID

    DELETE /api/listing/{pk}
    Summary:
        Delete a Listing Entry by ID
    """

    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.ListingSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('title', 'id', 'owners__display_name', 'agency__title', 'agency__short_name',)
    ordering_fields = ('title', 'id', 'agency__title', 'agency__short_name', 'is_enabled', 'is_featured', 'edited_date', 'security_marking', 'is_private', 'approval_status')
    ordering = ('is_deleted', '-edited_date')

    def get_queryset(self):
        approval_status = self.request.query_params.get('approval_status', None)
        # org = self.request.query_params.get('org', None)
        orgs = self.request.query_params.getlist('org', False)
        enabled = self.request.query_params.get('enabled', None)
        ordering = self.request.query_params.getlist('ordering', None)
        if enabled:
            enabled = enabled.lower()
            if enabled in ['true', '1']:
                enabled = True
            else:
                enabled = False

        listings = model_access.get_listings(self.request.user.username)
        if approval_status:
            listings = listings.filter(approval_status=approval_status)
        if orgs:
            listings = listings.filter(agency__title__in=orgs)
        if enabled is not None:
            listings = listings.filter(is_enabled=enabled)
        # have to handle this case manually because the ordering includes an app multiple times
        # if there are multiple owners. We instead do sorting by case insensitive compare of the
        # app owner that comes first alphabetically
        param = [s for s in ordering if 'owners__display_name' == s or '-owners__display_name' == s]
        if ordering is not None and param:
            orderby = 'min'
            if param[0].startswith('-'):
                orderby = '-min'
            listings = listings.annotate(min=Min(Lower('owners__display_name'))).order_by(orderby)
            self.ordering = None
        return listings

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        counts_data = model_access.put_counts_in_listings_endpoint(queryset)
        # it appears that because we override the queryset here, we must
        # manually invoke the pagination methods
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ListingSerializer(page,
                context={'request': request}, many=True)
            r = self.get_paginated_response(serializer.data)
            # add counts to response
            r.data['counts'] = counts_data
            return r

        serializer = serializers.ListingSerializer(queryset,
            context={'request': request}, many=True)
        r = Response(serializer.data)
        # add counts to response
        counts = {'counts': counts_data}
        r.data.append(counts)
        return r

    def create(self, request):
        """
        Save a new Listing - only title is required

        Sample Payload:
        {
           "title":"My Test App",
           "description":"This is the full description of my app",
           "descriptionShort":"short app description",
           "contacts":[
              {
                 "type":"Technical Support",
                 "name":"Tech Support Contact",
                 "organization":"ABC Inc",
                 "email":"tsc@gmail.com",
                 "securePhone":"555-555-5555",
                 "unsecurePhone":"111-222-3454"
              }
           ],
           "tags":[
              "tag1",
              "tag2"
           ],
           "type":"Web Application",
           "requirements":"None",
           "versionName":"1.0.0",
           "launchUrl":"http://www.google.com/myApp",
           "whatIsNew":"Nothing is new",
           "owners":[
              {
                 "username":"alan"
              }
           ],
           "agency":"Test Organization",
           "categories":[
              "Entertainment",
              "Media and Video"
           ],
           "intents":[
              "application/json/edit",
              "application/json/view"
           ],
           "docUrls":[
              {
                 "name":"wiki",
                 "url":"http://www.wikipedia.com/myApp"
              }
           ],
           "smallIconId":"b0b54993-0668-4419-98e8-787e4c3a2dc2",
           "largeIconId":"e94128ab-d32d-4241-8820-bd2c69a64a87",
           "bannerIconId":"ecf79771-79a0-4884-a36d-5820c79c6d72",
           "featuredBannerIconId":"c3e6a369-4773-485e-b369-5cebaa331b69",
           "changeLogs":[

           ],
           "screenshots":[
              {
                 "smallImageId":"0b8db892-b669-4e86-af23-d899cb4d4d91",
                 "largeImageId":"80957d25-f34b-48bc-b860-b353cfd9e101"
              }
           ]
        }

        ---
        parameters:
            - name: body
              required: true
              paramType: body
        parameters_strategy:
            form: replace
            query: replace
        omit_serializer: true
        """
        # logger.debug('inside ListingViewSet.create', extra={'request': request})
        serializer = serializers.ListingSerializer(data=request.data,
            context={'request': request}, partial=True)

        if not serializer.is_valid():
            logger.error('{0!s}'.format(serializer.errors), extra={'request': request})
            return Response(serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        Get a Listing by id
        """
        queryset = self.get_queryset().get(pk=pk)
        serializer = serializers.ListingSerializer(queryset,
            context={'request': request})
        # TODO: Refactor in future to use django ordering (mlee)
        temp = serializer.data.get('screenshots')
        temp.sort(key=operator.itemgetter('order'))
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """
        Delete a listing
        """
        queryset = self.get_queryset()
        listing = get_object_or_404(queryset, pk=pk)
        model_access.delete_listing(request.user.username, listing)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, pk=None):
        """
        Update a Listing

        Sample payload:

        {
           "id":45,
           "title":"My Test App",
           "description":"This is the full description of my app",
           "descriptionShort":"short app description",
           "contacts":[
              {
                 "securePhone":"555-555-5555",
                 "unsecurePhone":"111-222-3454",
                 "email":"tsc@gmail.com",
                 "organization":"ABC Inc",
                 "name":"Tech Support Contact",
                 "type":"Technical Support"
              }
           ],
           "totalReviews":0,
           "avgRate":0,
           "totalRate1":0,
           "totalRate2":0,
           "totalRate3":0,
           "totalRate4":0,
           "height":null,
           "width":null,
           "totalRate5":0,
           "totalVotes":0,
           "tags":[
              "tag2",
              "tag1"
           ],
           "type":"Web Application",
           "uuid":"e378c427-bba6-470c-b2f3-e550b9129504",
           "requirements":"None",
           "iframe_compatible":false,
           "versionName":"1.0.0",
           "launchUrl":"http://www.google.com/myApp",
           "whatIsNew":"Nothing is new",
           "owners":[
              {
                 "displayName":"kevink",
                 "username":"kevink",
                 "id":5
              }
           ],
           "agency":"Test Organization",
           "agencyShort":"TO",
           "currentRejection":null,
           "isEnabled":true,
           "categories":[
              "Media and Video",
              "Entertainment"
           ],
           "editedDate":"2015-08-12T10:53:47.036+0000",
           "intents":[
              "application/json/edit",
              "application/json/view"
           ],
           "docUrls":[
              {
                 "url":"http://www.wikipedia.com/myApp",
                 "name":"wiki"
              }
           ],
           "approvalStatus":"IN_PROGRESS",
           "isFeatured":false,
           "smallIconId":"b0b54993-0668-4419-98e8-787e4c3a2dc2",
           "largeIconId":"e94128ab-d32d-4241-8820-bd2c69a64a87",
           "bannerIconId":"ecf79771-79a0-4884-a36d-5820c79c6d72",
           "featuredBannerIconId":"c3e6a369-4773-485e-b369-5cebaa331b69",
           "changeLogs":[

           ],
           "screenshots":[
              {
                 "largeImageId":"80957d25-f34b-48bc-b860-b353cfd9e101",
                 "smallImageId":"0b8db892-b669-4e86-af23-d899cb4d4d91"
              }
           ]
        }
        """
        # logger.debug('inside ListingViewSet.update', extra={'request': request})
        instance = self.get_queryset().get(pk=pk)
        serializer = serializers.ListingSerializer(instance, data=request.data, context={'request': request}, partial=True)

        # logger.debug('created ListingSerializer', extra={'request': request})

        if not serializer.is_valid():
            logger.error('{0!s}'.format(serializer.errors), extra={'request': request})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        """
        TODO: Probably don't use this (PATCH)
        """
        pass


class ListingUserViewSet(viewsets.ModelViewSet):
    """
    Listing Types

    Get all listings owned by this user

    ModelViewSet for getting all ListingUserViewSets

    Access Control
    ===============
    - All users can view

    URIs
    ======
    GET /api/self/listing
    Summary:
        Get a list of all system-wide Listing User entries
    Response:
        200 - Successful operation - [ListingSerializer]

    GET /api/self/listing/{pk}
    Summary:
        Find a ListingUserViewSet Entry by ID
    Response:
        200 - Successful operation - ListingSerializer
    """
    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.ListingSerializer

    def get_queryset(self):
        return model_access.get_self_listings(self.request.user.username)

    def list(self, request):
        return super(ListingUserViewSet, self).list(self, request)


class ListingSearchViewSet(viewsets.ModelViewSet):
    """
    Search for listings

    ModelViewSet for getting all Listing Searches

    Access Control
    ===============
    - All users can view

    URIs
    ======
    GET /api/listings/search
    Summary:
        Get a list of all system-wide Listing Search entries
    Response:
        200 - Successful operation - [ListingSerializer]

    GET /api/listings/search/{pk}
    Summary:
        Find a ListingSearchViewSet Entry by ID
    Response:
        200 - Successful operation - ListingSerializer
    """

    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.ListingSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('title', 'description', 'description_short', 'tags__name')

    def get_queryset(self):
        filter_params = {}
        categories = self.request.query_params.getlist('category', False)
        agencies = self.request.query_params.getlist('agency', False)
        listing_types = self.request.query_params.getlist('type', False)
        if categories:
            filter_params['categories'] = categories
        if agencies:
            filter_params['agencies'] = agencies
        if listing_types:
            filter_params['listing_types'] = listing_types

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


class ElasticsearchListingSearchViewSet(viewsets.ViewSet):
    """
    Elasticsearch Listing Search Viewset

    It must support pagination. offset, limit

    GET /api/listings/essearch/?search=6&offset=0&limit=24 HTTP/1.1
    GET /api/listings/essearch/?search=6&offset=0&limit=24 HTTP/1.1

    GET api/listings/essearch/?search=6&offset=0&category=Education&limit=24&type=web+application&agency=Minitrue&agency=Miniluv&minscore=0.4

    ModelViewSet for searching all Listings with Elasticsearch

    Access Control
    ===============
    - All users can view

    URIs
    ======
    GET /api/listings/essearch
    """
    permission_classes = (permissions.IsUser,)

    def list(self, request):
        current_request_username = request.user.username
        params_obj = model_access_es.SearchParamParser(request)

        results = model_access_es.search(current_request_username, params_obj)
        return Response(results, status=status.HTTP_200_OK)

    @list_route(methods=['get'], permission_classes=[permissions.IsUser])
    def suggest(self, request):
        current_request_username = request.user.username
        params_obj = model_access_es.SearchParamParser(self.request)

        results = model_access_es.suggest(current_request_username, params_obj)
        return Response(results, status=status.HTTP_200_OK)

    def create(self, request):
        """
        This method is not supported
        """
        return Response({'detail': 'HTTP Verb Not Supported'}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def retrieve(self, request, pk=None):
        """
        This method is not supported
        """
        return Response({'detail': 'HTTP Verb Not Supported'}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def update(self, request, pk=None):
        """
        This method is not supported
        """
        return Response({'detail': 'HTTP Verb Not Supported'}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def partial_update(self, request, pk=None):
        """
        This method is not supported
        """
        return Response({'detail': 'HTTP Verb Not Supported'}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def destroy(self, request, pk=None):
        """
        This method is not supported
        """
        return Response({'detail': 'HTTP Verb Not Supported'}, status=status.HTTP_501_NOT_IMPLEMENTED)
