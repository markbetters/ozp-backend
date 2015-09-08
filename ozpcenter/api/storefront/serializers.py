"""
Serializers
"""
import logging

import django.contrib.auth
from rest_framework import serializers

import ozpcenter.models as models
import ozpcenter.api.access_control.serializers as access_control_serializers
import ozpcenter.api.category.serializers as category_serializers
import ozpcenter.api.image.serializers as image_serializers

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Agency
        fields = ('short_name', 'title')

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = django.contrib.auth.models.Group
        fields = ('name',)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        # TODO: not supposed to reference Django's User model directly, but
        # using settings.AUTH_USER_MODEL here doesn't not work
        # model = settings.AUTH_USER_MODEL
        model = django.contrib.auth.models.User
        fields = ('username', 'email')

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = models.Profile
        fields = ('user',)

class ContactTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ContactType
        fields = ('name',)

class ContactSerializer(serializers.ModelSerializer):
    contact_type = ContactTypeSerializer()
    class Meta:
        model = models.Contact

class ListingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ListingType
        fields = ('title', 'description')

class DocUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DocUrl
        fields = ('name', 'url')

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = ('text', 'rate')

class ListingActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ListingActivity
        fields = ('action', 'activity_date')

# class RejectionListingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.RejectionListing
#         fields = ('description')

class ScreenshotSerializer(serializers.ModelSerializer):
    small_image = image_serializers.ImageSerializer()
    large_image = image_serializers.ImageSerializer()
    class Meta:
        model = models.Screenshot
        fields = ('small_image', 'large_image')

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ('name',)

class ListingSerializer(serializers.ModelSerializer):
    screenshots = ScreenshotSerializer(many=True)
    doc_urls = DocUrlSerializer(many=True)
    owners = ProfileSerializer(many=True)
    categories = category_serializers.CategorySerializer(many=True)
    tags = TagSerializer(many=True)
    agency = AgencySerializer()
    contacts = ContactSerializer(many=True)
    small_icon = image_serializers.ImageSerializer()
    large_icon = image_serializers.ImageSerializer()
    banner_icon = image_serializers.ImageSerializer()
    large_banner_icon = image_serializers.ImageSerializer()
    class Meta:
        model = models.Listing
        depth = 2


class StorefrontSerializer(serializers.Serializer):
    featured = ListingSerializer(many=True)
    recent = ListingSerializer(many=True)
    most_popular = ListingSerializer(many=True)