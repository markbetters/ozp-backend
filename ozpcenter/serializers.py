"""
Serializers for the API

Serialization = Python obj -> JSON
Deserialization = JSON -> Python obj

DRF does not have a built-in, defacto way of specifying different serializers
for handling input on a request vs output on a Response. Sometimes this is
acceptable, but often times the two structures are not the same. For instance,
some fields may be auto-generated on the server when a POST is made (so they
shouldn't be part of the POST Request data that will be deserialized), but a
GET request should return a Response that includes this information. For
simple cases like this, Serializer fields can be marked as read_only or
write_only (read_only fields will not become part of the serializer's
validated_data). If more control than this is needed (e.g. very different input
and output formats), the get_serializer_class() method can be overridden
in the View and selected dynamically based on request.method (POST, GET, etc).

For details regarding input vs output serializers:
https://github.com/tomchristie/django-rest-framework/issues/1563
http://stackoverflow.com/questions/17551380/python-rest-framwork-different-serializers-for-input-and-output-of-service

"""
import logging

import django.contrib.auth
from rest_framework import serializers

import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

################################################################################
#       Simple Serializers - no nested relationships, reusable between
#   read and write operations
################################################################################

class AccessControlSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.AccessControl
        fields = ('title',)

class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Category

class ContactTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ContactType

class ContactSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Contact

################################################################################
#       Basic Serializers
################################################################################

class IconSerializer(serializers.HyperlinkedModelSerializer):
    access_control = AccessControlSerializer()
    class Meta:
        model = models.Icon

class AgencySerializer(serializers.HyperlinkedModelSerializer):
    icon = IconSerializer()
    class Meta:
        model = models.Agency
        depth = 2

class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    organizations = AgencySerializer(many=True)
    stewarded_organizations = AgencySerializer(many=True)
    class Meta:
        model = models.Profile

class ListingTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ListingType

class DocUrlSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.DocUrl

class IntentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Intent
        depth = 1

class ItemCommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ItemComment

class ListingActivitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ListingActivity

class RejectionListingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.RejectionListing

class ScreenshotSerializer(serializers.HyperlinkedModelSerializer):
    small_image = IconSerializer()
    large_image = IconSerializer()
    class Meta:
        model = models.Screenshot

class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Tag

class ListingSerializer(serializers.HyperlinkedModelSerializer):
    screenshots = ScreenshotSerializer(many=True)
    doc_urls  = DocUrlSerializer(many=True)
    owners  = ProfileSerializer(many=True)
    categories  = CategorySerializer(many=True)
    tags = TagSerializer(many=True)
    class Meta:
        model = models.Listing
        depth = 2

class LibraryListingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Listing
        fields = ('title', 'unique_name', 'launch_url', 'small_icon',
            'large_icon', 'banner_icon', 'large_banner_icon')

class NotificationListingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Listing
        fields = ('title', 'unique_name')

################################################################################
#       Self Serializers
################################################################################
# class ListingLibrarySerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = models.Listing
#         depth = 1
#         fields = ('id', 'title', 'unique_name')
#         read_only_fields = ('title', 'unique_name')
#         # fields = ('title', 'unique_name', 'small_icon', 'large_icon',
#         #     'banner_icon', 'large_banner_icon')
#         validators = []

#     def validate(self, data):
#         """
#         TODO
#         """
#         logger.info('validate invoked for ListingLibrarySerializer: %s' % data)
#         return data

class LibraryEntrySerializer(serializers.Serializer):
    """
    Serializer for create self/library
    """
    listing_id = serializers.IntegerField(max_value=None, min_value=0)
    title = serializers.CharField(max_length=255, read_only=True)
    unique_name = serializers.CharField(max_length=255, read_only=True)
    folder = serializers.CharField(max_length=255, required=False,
        allow_blank=True)

    def validate(self, data):
        """
        TODO
        """
        logger.info('validate invoked for LibraryEntrySerializer: %s' % data)
        return data


    def create(self, validated_data):
        logger.info('inside LibraryEntryWriteSerializer.create - validated data: %s' % validated_data)
        listing = models.Listing.objects.get(id=validated_data['listing_id'])
        owner = models.Profile.objects.get(username=self.context['request'].user.username)
        entry = models.ApplicationLibraryEntry(listing=listing, owner=owner,folder=validated_data['folder'])
        entry.save()
        unique_name = 'something'
        return entry

class ApplicationLibraryEntrySerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for self/library - owner is always current user
    """
    listing = LibraryListingSerializer()
    owner = ProfileSerializer()
    class Meta:
        model = models.ApplicationLibraryEntry
        fields = ('listing', 'folder', 'owner')


class StorefrontSerializer(serializers.Serializer):
    featured = ListingSerializer(many=True)
    recent = ListingSerializer(many=True)
    most_popular = ListingSerializer(many=True)

class ShortProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Profile
        fields = ('username',)

class NotificationSerializer(serializers.HyperlinkedModelSerializer):
    author = ShortProfileSerializer()
    listing = NotificationListingSerializer()
    class Meta:
        model = models.Notification

class DjangoUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        # TODO: not supposed to reference Django's User model directly, but
        # using settings.AUTH_USER_MODEL here doesn't not work
        # model = settings.AUTH_USER_MODEL
        model = django.contrib.auth.models.User

