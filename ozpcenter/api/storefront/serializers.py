"""
Storefront and Metadata Serializers
"""
import logging

from django.contrib import auth
from rest_framework import serializers

from ozpcenter import models
import ozpcenter.api.category.serializers as category_serializers
import ozpcenter.api.image.serializers as image_serializers

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class AgencySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Agency
        fields = ('short_name', 'title')


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = auth.models.Group
        fields = ('name',)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        # TODO: not supposed to reference Django's User model directly, but
        # using settings.AUTH_USER_MODEL here doesn't not work
        # model = settings.AUTH_USER_MODEL
        model = auth.models.User
        fields = ('username', 'email')


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = models.Profile
        fields = ('user', 'display_name', 'id')


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

    @staticmethod
    def setup_eager_loading(queryset):
        # select_related foreign keys
        queryset = queryset.select_related('agency')
        queryset = queryset.select_related('small_icon')
        queryset = queryset.select_related('large_icon')
        queryset = queryset.select_related('banner_icon')
        queryset = queryset.select_related('large_banner_icon')
        queryset = queryset.select_related('required_listings')

        # prefetch_related many-to-many relationships
        queryset = queryset.prefetch_related('agency__icon')
        queryset = queryset.prefetch_related('screenshots')
        queryset = queryset.prefetch_related('screenshots__small_image')
        queryset = queryset.prefetch_related('screenshots__large_image')
        queryset = queryset.prefetch_related('doc_urls')
        queryset = queryset.prefetch_related('owners')
        queryset = queryset.prefetch_related('owners__user')
        queryset = queryset.prefetch_related('owners__organizations')
        queryset = queryset.prefetch_related('owners__stewarded_organizations')
        queryset = queryset.prefetch_related('categories')
        queryset = queryset.prefetch_related('tags')
        queryset = queryset.prefetch_related('contacts')
        queryset = queryset.prefetch_related('contacts__contact_type')
        queryset = queryset.prefetch_related('listing_type')
        queryset = queryset.prefetch_related('last_activity')
        queryset = queryset.prefetch_related('last_activity__change_details')
        queryset = queryset.prefetch_related('last_activity__author')
        queryset = queryset.prefetch_related('last_activity__author__organizations')
        queryset = queryset.prefetch_related('last_activity__author__stewarded_organizations')
        queryset = queryset.prefetch_related('last_activity__listing')
        queryset = queryset.prefetch_related('last_activity__listing__contacts')
        queryset = queryset.prefetch_related('last_activity__listing__owners')
        queryset = queryset.prefetch_related('last_activity__listing__owners__user')
        queryset = queryset.prefetch_related('last_activity__listing__categories')
        queryset = queryset.prefetch_related('last_activity__listing__tags')
        queryset = queryset.prefetch_related('last_activity__listing__intents')
        queryset = queryset.prefetch_related('current_rejection')
        queryset = queryset.prefetch_related('intents')
        queryset = queryset.prefetch_related('intents__icon')

        return queryset


class StorefrontSerializer(serializers.Serializer):
    featured = ListingSerializer(many=True)
    recent = ListingSerializer(many=True)
    most_popular = ListingSerializer(many=True)
