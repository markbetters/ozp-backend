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

    The unique_together contraints on models.ItemComment make it difficult to
    use the standard Serializer classes (see the Note here:
        http://www.django-rest-framework.org/api-guide/serializers/#specifying-read-only-fields)

    Primarily for that reason, we forgo using Serializers for POST and PUT
    actions
    """
    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.ItemCommentSerializer

    def get_queryset(self):
        return model_access.get_item_comments(self.request.user.username)

    def list(self, request, listing_pk=None):
        queryset = self.get_queryset().filter(listing=listing_pk)
        serializer = serializers.ItemCommentSerializer(queryset, many=True,
            context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None, listing_pk=None):
        queryset = self.get_queryset().get(pk=pk, listing=listing_pk)
        serializer = serializers.ItemCommentSerializer(queryset,
            context={'request': request})
        return Response(serializer.data)

    def destroy(self, request, pk=None, listing_pk=None):
        # TODO: permission check. either the current user must be the
        #   author of this item_comment, or the user must be an Org Steward
        #   or higher
        queryset = self.get_queryset()
        instance = get_object_or_404(queryset, pk=pk)

        # if the author doesn't match the current user AND the current user
        # is not an org steward or higher, deny the request
        profile = generic_model_access.get_profile(request.user.username)
        priv_roles = ['APPS_MALL_STEWARD', 'ORG_STEWARD']
        if profile.highest_role() in priv_roles:
            pass
        elif instance.author.user.username != request.user.username:
            return Response('Cannot update another user\'s review',
                status=status.HTTP_403_FORBIDDEN)

        instance.delete()
        model_access.update_rating(request.user.username, listing_pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, listing_pk=None):
        """
        Create a new item_comment
        """
        author = generic_model_access.get_profile(
            request.user.username)
        try:
            listing = models.Listing.objects.for_user(
                request.user.username).get(id=listing_pk)
        except:
            return Response('Invalid listing',
                status=status.HTTP_400_BAD_REQUEST)

        try:
            rate = int(request.data['rate'])
            text = request.data.get('text', None)

            comment = models.ItemComment(listing=listing, author=author,
                rate=rate, text=text)
            comment.save()
            model_access.update_rating(request.user.username, listing_pk)

            output = {"rate": rate, "text": text, "author": author.id,
                "listing": listing.id, "id": comment.id}
            return Response(output, status=status.HTTP_201_CREATED)
        except Exception as e:
            raise e
            return Response('Bad request to create new item_comment',
                status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, pk=None, listing_pk=None):
        """
        Update an existing item_comment
        """
        try:
            instance = models.ItemComment.objects.get(id=pk)
        except models.ItemComment.DoesNotExist:
            return Response('Invalid item comment',
                status=status.HTTP_400_BAD_REQUEST)

        if instance.author.user.username != request.user.username:
            return Response('Cannot update another user\'s review',
                status=status.HTTP_403_FORBIDDEN)

        try:
            rate = request.data.get('rate', instance.rate)
            text = request.data.get('text', None)
        except:
            return Response('Bad request to create new item_comment',
                status=status.HTTP_400_BAD_REQUEST)

        change_details = [
            {
                'field_name': 'rate',
                'old_value': instance.rate,
                'new_value': rate
            },
            {
                'field_name': 'text',
                'old_value': instance.text,
                'new_value': text
            }
        ]
        instance.rate = rate
        instance.text = text
        instance.save()
        # update this listing's rating
        model_access.update_rating(request.user.username, listing_pk)
        # log this activity
        listing = models.Listing.objects.for_user(request.user.username).get(
          id=listing_pk)
        model_access.edit_listing_review(instance.author,
            listing, change_details)

        output = {"rate": instance.rate, "text": instance.text,
            "author": instance.author.id,
            "listing": instance.listing.id, "id": instance.id}
        return Response(output, status=status.HTTP_200_OK)


class ListingTypeViewSet(viewsets.ModelViewSet):
    queryset = models.ListingType.objects.all()
    serializer_class = serializers.ListingTypeSerializer

class ListingActivityViewSet(viewsets.ModelViewSet):
    """
    ListingActivity endpoints are read-only
    """
    serializer_class = serializers.ListingActivitySerializer

    def get_queryset(self):
        user = generic_model_access.get_profile(self.request.user.username)
        return models.ListingActivity.objects.for_user(
            self.request.user.username).all()

    def list(self, request, listing_pk=None):
        return super(ListingActivityViewSet, self).list(self, request)

    def retrieve(self, request, pk=None, listing_pk=None):
        queryset = self.get_queryset().get(pk=pk, listing=listing_pk)
        serializer = serializers.ListingActivitySerializer(queryset,
            context={'request': request})
        return Response(serializer.data)


# class RejectionListingViewSet(viewsets.ModelViewSet):
#     queryset = models.RejectionListing.objects.all()
#     serializer_class = serializers.RejectionListingSerializer

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
        pass

    def retrieve(self, request, pk=None):
        """
        Get a Listing by id
        """
        pass

    def destroy(self, request, pk=None):
        """
        Delete a listing
        """
        pass

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
           "totalComments":0,
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
           "singleton":false,
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
        pass

    def partial_update(self, request, pk=None):
        """
        TODO: probobly don't use this (PATCH)
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