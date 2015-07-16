"""
Serializers
"""
import logging

import django.contrib.auth
from rest_framework import serializers

import ozpcenter.models as models
import ozpcenter.api.access_control.serializers as access_control_serializers
import ozpcenter.api.category.serializers as category_serializers

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class ImageSerializer(serializers.HyperlinkedModelSerializer):
    access_control = access_control_serializers.AccessControlSerializer()
    class Meta:
        model = models.Image
        fields = ('image_url', 'access_control')

class AgencySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Agency
        fields = ('short_name',)

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = django.contrib.auth.models.Group
        fields = ('name',)

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        # TODO: not supposed to reference Django's User model directly, but
        # using settings.AUTH_USER_MODEL here doesn't not work
        # model = settings.AUTH_USER_MODEL
        model = django.contrib.auth.models.User
        fields = ('username', 'email')

class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer()
    class Meta:
        model = models.Profile
        fields = ('user',)

class ContactSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Contact
        fields = ('name', 'email')

class ListingTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ListingType
        fields = ('title', 'description')

class DocUrlSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.DocUrl
        fields = ('name', 'url')

class ItemCommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ItemComment
        fields = ('text', 'rate')

class ListingActivitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ListingActivity
        fields = ('action', 'activity_date')

class RejectionListingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.RejectionListing
        fields = ('description')

class ScreenshotSerializer(serializers.HyperlinkedModelSerializer):
    small_image = ImageSerializer()
    large_image = ImageSerializer()
    class Meta:
        model = models.Screenshot
        fields = ('small_image', 'large_image')

class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Tag
        fields = ('name',)

class ListingSerializer(serializers.HyperlinkedModelSerializer):
    screenshots = ScreenshotSerializer(many=True)
    doc_urls = DocUrlSerializer(many=True)
    owners = ProfileSerializer(many=True)
    categories = category_serializers.CategorySerializer(many=True)
    tags = TagSerializer(many=True)
    agency = AgencySerializer()
    contacts = ContactSerializer(many=True)
    small_icon = ImageSerializer()
    large_icon = ImageSerializer()
    banner_icon = ImageSerializer()
    large_banner_icon = ImageSerializer()
    class Meta:
        model = models.Listing
        depth = 2

class StorefrontSerializer(serializers.Serializer):
    featured = ListingSerializer(many=True)
    recent = ListingSerializer(many=True)
    most_popular = ListingSerializer(many=True)