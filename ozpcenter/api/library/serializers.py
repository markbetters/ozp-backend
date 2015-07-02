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
        depth = 1
        fields = ('id', 'title', 'unique_name')
        read_only_fields = ('title', 'unique_name')
        # fields = ('title', 'unique_name', 'small_icon', 'large_icon',
        #     'banner_icon', 'large_banner_icon')
        validators = []

    def validate(self, data):
        """
        TODO
        """
        logger.info('validate invoked for ListingLibrarySerializer: %s' % data)
        return data

class LibraryEntrySerializer(serializers.Serializer):
    """
    Serializer for create self/library
    """
    listing = LibraryListingSerializer()
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
        listing = models.Listing.objects.get(id=validated_data['listing'])
        owner = models.Profile.objects.get(username=self.context['request'].user.username)
        entry = models.ApplicationLibraryEntry(listing=listing, owner=owner,folder=validated_data['folder'])
        entry.save()
        return entry

class ApplicationLibraryEntrySerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for self/library - owner is always current user
    """
    listing = LibraryListingSerializer()
    owner = profile_serializers.ProfileSerializer()
    class Meta:
        model = models.ApplicationLibraryEntry
        fields = ('listing', 'folder', 'owner')