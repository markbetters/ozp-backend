"""
Serializers
"""
import logging

from rest_framework import serializers

import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class ShortProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Profile
        fields = ('username',)

class NotificationListingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Listing
        fields = ('title',)

class NotificationSerializer(serializers.HyperlinkedModelSerializer):
    author = ShortProfileSerializer()
    listing = NotificationListingSerializer()
    class Meta:
        model = models.Notification