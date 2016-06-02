"""
Views
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
import ozpcenter.errors as errors
import ozpcenter.pagination as pagination
import ozpcenter.api.listing.model_access as model_access
import ozpcenter.model_access as generic_model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class ContactViewSet(viewsets.ModelViewSet):
    queryset = model_access.get_all_contacts()
    serializer_class = serializers.ContactSerializer


class DocUrlViewSet(viewsets.ModelViewSet):
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
    """
    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.ReviewSerializer
    # pagination_class = pagination.StandardPagination

    def get_queryset(self):
        return model_access.get_reviews(self.request.user.username)

    def list(self, request, listing_pk=None):
        queryset = self.get_queryset().filter(listing=listing_pk).order_by('-edited_date')
        # it appears that because we override the queryset here, we must
        # manually invoke the pagination methods
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ReviewSerializer(page,
                context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.ReviewSerializer(queryset, many=True,
            context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None, listing_pk=None):
        queryset = self.get_queryset().get(pk=pk, listing=listing_pk)
        serializer = serializers.ReviewSerializer(queryset,
            context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, pk=None, listing_pk=None):
        queryset = self.get_queryset()
        review = get_object_or_404(queryset, pk=pk)
        try:
            model_access.delete_listing_review(request.user.username, review)
        except errors.PermissionDenied:
            return Response('Cannot update another user\'s review',
                status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, listing_pk=None):
        """
        Create a new review
        """
        try:
            listing = model_access.get_listing_by_id(request.user.username,
                listing_pk)
            if listing is None:
                raise Exception
        except Exception:
            return Response('Invalid listing',
                status=status.HTTP_400_BAD_REQUEST)

        try:
            rate = int(request.data['rate'])
            text = request.data.get('text', None)
        except Exception:
            return Response('Invalid input data',
                status=status.HTTP_400_BAD_REQUEST)

        try:
            resp = model_access.create_listing_review(request.user.username,
                listing, rate, text)
            return Response(resp, status=status.HTTP_201_CREATED)
        except Exception as e:
            raise e
            return Response('Bad request to create new review',
                status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, listing_pk=None):
        """
        Update an existing review
        """
        try:
            review = model_access.get_review_by_id(pk)
        except models.Review.DoesNotExist:
            return Response('Invalid review',
                status=status.HTTP_400_BAD_REQUEST)

        try:
            rate = request.data.get('rate', review.rate)
            text = request.data.get('text', None)
        except:
            return Response('Bad request to create new review',
                status=status.HTTP_400_BAD_REQUEST)

        try:
            review = model_access.edit_listing_review(request.user.username,
                review, rate, text)
            output = {"rate": review.rate, "text": review.text,
                "author": review.author.id,
                "listing": review.listing.id, "id": review.id}
            return Response(output, status=status.HTTP_200_OK)
        except errors.PermissionDenied:
            return Response('Cannot update another user\'s review',
                 status=status.HTTP_403_FORBIDDEN)


class ListingTypeViewSet(viewsets.ModelViewSet):
    queryset = model_access.get_all_listing_types()
    serializer_class = serializers.ListingTypeSerializer


class ListingUserActivitiesViewSet(viewsets.ModelViewSet):
    """
    ListingUserActivitiesViewSet endpoints are read-only
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
    queryset = model_access.get_all_screenshots()
    serializer_class = serializers.ScreenshotSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = model_access.get_all_tags()
    serializer_class = serializers.TagSerializer


class ListingViewSet(viewsets.ModelViewSet):
    """
    Get all listings this user can see
    """
    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.ListingSerializer

    def get_queryset(self):
        approval_status = self.request.query_params.get('approval_status', None)
        # org = self.request.query_params.get('org', None)
        orgs = self.request.query_params.getlist('org', False)
        enabled = self.request.query_params.get('enabled', None)
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

        return listings

    def list(self, request):
        queryset = self.get_queryset()
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
        try:
            # logger.debug('inside ListingViewSet.create', extra={'request': request})
            serializer = serializers.ListingSerializer(data=request.data,
                context={'request': request}, partial=True)
            if not serializer.is_valid():
                logger.error('{0!s}'.format(serializer.errors), extra={'request': request})
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except errors.PermissionDenied:
            return Response({'detail': 'Permission Denied'}, status=status.HTTP_403_FORBIDDEN)
        except errors.InvalidInput as err:
            return Response({'detail': '{}'.format(err)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise e

    def retrieve(self, request, pk=None):
        """
        Get a Listing by id
        """
        queryset = self.get_queryset().get(pk=pk)
        serializer = serializers.ListingSerializer(queryset,
            context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """
        Delete a listing
        """
        queryset = self.get_queryset()
        listing = get_object_or_404(queryset, pk=pk)
        try:
            model_access.delete_listing(request.user.username, listing)
        except errors.PermissionDenied as e:
            return Response({'detail': 'Permission Denied', 'reason': str(e)}, status=status.HTTP_403_FORBIDDEN)
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
        try:
            # logger.debug('inside ListingViewSet.update', extra={'request': request})

            instance = self.get_queryset().get(pk=pk)
            serializer = serializers.ListingSerializer(instance,
                data=request.data, context={'request': request}, partial=True)

            # logger.debug('created ListingSerializer', extra={'request': request})

            if not serializer.is_valid():
                logger.error('{0!s}'.format(serializer.errors), extra={'request': request})
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except errors.PermissionDenied:
            return Response({'detail': 'Permission Denied'}, status=status.HTTP_403_FORBIDDEN)
        except errors.InvalidInput as err:
            return Response({'detail': '{}'.format(err)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise e

    def partial_update(self, request, pk=None):
        """
        TODO: Probably don't use this (PATCH)
        """
        pass


class ListingUserViewSet(viewsets.ModelViewSet):
    """
    Get all listings owned by this user
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
