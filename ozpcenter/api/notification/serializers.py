"""
Serializers
"""
import logging

from rest_framework import serializers
from django.contrib.auth.models import User

import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class ShortUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username',)

class ShortProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Profile
        fields = ('user',)

class NotificationListingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Listing
        fields = ('title',)

class NotificationSerializer(serializers.ModelSerializer):
    author = ShortProfileSerializer()
    listing = NotificationListingSerializer()
    class Meta:
        model = models.Notification