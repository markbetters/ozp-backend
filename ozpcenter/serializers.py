"""
Serializers for the API
"""
import django.contrib.auth
from rest_framework import serializers

import ozpcenter.models as models


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Category

class ContactTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ContactType

class IconSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Icon

class AgencySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Agency
        depth=1

class ContactSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Contact

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

class ApplicationLibraryEntrySerializer(serializers.HyperlinkedModelSerializer):
    listing = LibraryListingSerializer()
    class Meta:
        model = models.ApplicationLibraryEntry
        fields = ('listing', 'folder')

class StorefrontSerializer(serializers.Serializer):
    featured = ListingSerializer(many=True)
    recent = ListingSerializer(many=True)
    most_popular = ListingSerializer(many=True)

class AccessControlSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.AccessControl

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
        # using settings.AUTH_USER_MODEL here doesn not work
        # model = settings.AUTH_USER_MODEL
        model = django.contrib.auth.models.User

