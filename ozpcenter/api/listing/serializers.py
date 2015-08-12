"""
Serializers
"""
import logging

import django.contrib.auth
from rest_framework import serializers

import ozpcenter.models as models

import ozpcenter.api.image.serializers as image_serializers
import ozpcenter.api.category.serializers as category_serializers
import ozpcenter.api.profile.serializers as profile_serializers
import ozpcenter.model_access as generic_model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

# contacts are only used in conjunction with Listings
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contact


class ListingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ListingType


class DocUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DocUrl

# class RejectionListingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.RejectionListing

class ScreenshotSerializer(serializers.ModelSerializer):
    small_image = image_serializers.ImageSerializer()
    large_image = image_serializers.ImageSerializer()
    class Meta:
        model = models.Screenshot


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag

class ChangeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ChangeDetail


class ListingSerializer(serializers.ModelSerializer):
    screenshots = ScreenshotSerializer(many=True)
    doc_urls  = DocUrlSerializer(many=True)
    owners  = profile_serializers.ProfileSerializer(many=True)
    categories  = category_serializers.CategorySerializer(many=True)
    tags = TagSerializer(many=True)
    class Meta:
        model = models.Listing
        depth = 2


class ItemCommentSerializer(serializers.ModelSerializer):
    author = profile_serializers.ShortProfileSerializer()
    class Meta:
        model = models.ItemComment
        fields = ('author', 'listing', 'rate', 'text', 'id')


class ShortListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Listing
        fields = ('unique_name', 'title')


class ListingActivitySerializer(serializers.ModelSerializer):
    author = profile_serializers.ShortProfileSerializer()
    listing = ShortListingSerializer()
    change_details = ChangeDetailSerializer(many=True)
    class Meta:
        model = models.ListingActivity
        fields = ('action', 'activity_date', 'description', 'author', 'listing',
            'change_details')