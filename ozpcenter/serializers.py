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

class AgencySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Agency

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

class ItemCommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ItemComment

class ListingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Listing

class ApplicationLibraryEntrySerializer(serializers.HyperlinkedModelSerializer):
    listing = ListingSerializer()
    class Meta:
        model = models.ApplicationLibraryEntry

class ListingActivitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ListingActivity

class RejectionListingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.RejectionListing

class ScreenshotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Screenshot

class DjangoUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        # TODO: not supposed to reference Django's User model directly, but
        # using settings.AUTH_USER_MODEL here doesn not work
        # model = settings.AUTH_USER_MODEL
        model = django.contrib.auth.models.User

