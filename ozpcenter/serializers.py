"""
Serializers for the API
"""
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
	class Meta:
	    model = models.Profile

class ListingTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ListingType

