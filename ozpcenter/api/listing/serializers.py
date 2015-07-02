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

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class ListingTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ListingType

class DocUrlSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.DocUrl

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
    small_image = image_serializers.IconSerializer()
    large_image = image_serializers.IconSerializer()
    class Meta:
        model = models.Screenshot

class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Tag

class ListingSerializer(serializers.HyperlinkedModelSerializer):
    screenshots = ScreenshotSerializer(many=True)
    doc_urls  = DocUrlSerializer(many=True)
    owners  = profile_serializers.ProfileSerializer(many=True)
    categories  = category_serializers.CategorySerializer(many=True)
    tags = TagSerializer(many=True)
    class Meta:
        model = models.Listing
        depth = 2