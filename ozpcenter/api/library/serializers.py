"""
Serializers
"""
import logging

from rest_framework import serializers

import ozpcenter.models as models
import ozpcenter.api.profile.serializers as profile_serializers

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class LibrarySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ApplicationLibraryEntry


class LibraryListingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Listing
        fields = ('id', 'title', 'unique_name')
        read_only_fields = ('title', 'unique_name')
        # Any AutoFields on your model (which is what the automatically
        # generated id key is) are set to read-only by default when Django
        # REST Framework is creating fields in the background. read-only fields
        # will not be part of validated_data. Override that behavior using the
        # extra_kwargs
        extra_kwargs = {
            "id": {
                "read_only": False,
                "required": False,
            },
        }


class UserLibrarySerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for self/library - owner is always current user
    """
    listing = LibraryListingSerializer()
    class Meta:
        model = models.ApplicationLibraryEntry
        fields = ('listing', 'folder')

    def validate(self, data):
        """
        Check for listing id (folder is optional)
        """
        if 'id' not in data['listing']:
            raise serializers.ValidationError('No listing id provided')
        return data

    def create(self, validated_data):
        folder = validated_data.get('folder', '')
        listing = models.Listing.objects.get(id=validated_data['listing']['id'])
        owner = models.Profile.objects.get(user__username=self.context['request'].user.username)
        entry = models.ApplicationLibraryEntry(listing=listing, owner=owner,
            folder=folder)
        entry.save()
        return entry