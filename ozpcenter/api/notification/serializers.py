"""
Serializers
"""
import logging

from rest_framework import serializers
from django.contrib.auth.models import User

import ozpcenter.models as models
import ozpcenter.errors as errors
import ozpcenter.model_access as generic_model_access
import ozpcenter.api.listing.model_access as listing_model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class ShortUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)

class ShortProfileSerializer(serializers.ModelSerializer):
    user = ShortUserSerializer()
    class Meta:
        model = models.Profile
        fields = ('user',)

class NotificationListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Listing
        fields = ('title',)

        extra_kwargs = {
            'title': {'validators': []}
        }

class NotificationSerializer(serializers.ModelSerializer):
    author = ShortProfileSerializer(required=False)
    listing = NotificationListingSerializer(required=False)
    dismissed_by = ShortProfileSerializer(required=False, many=True)
    class Meta:
        model = models.Notification
        fields = ('id', 'created_date', 'message', 'expires_date', 'author',
            'listing', 'dismissed_by')

    def validate(self, data):
        username = self.context['request'].user.username
        listing = data.get('listing', None)
        if listing:
            # TODO: title not guaranteed to be unique
            data['listing'] = listing_model_access.get_listing_by_title(
                username, data['listing']['title'])
        else:
            data['listing'] = None
        return data

    def create(self, validated_data):
        user = generic_model_access.get_profile(
            self.context['request'].user.username)
        if user.highest_role() in ['ORG_STEWARD', 'APPS_MALL_STEWARD']:
            pass
        elif not validated_data['listing']:
            raise errors.PermissionDenied('Only stewards can send system notifications')
        elif user not in validated_data['listing'].owners.all():
            raise errors.PermissionDenied('Cannot create a notification for a listing you do not own')

        notification = models.Notification(
            expires_date=validated_data['expires_date'],
            author=user,
            message=validated_data['message'],
            listing=validated_data['listing'])
        notification.save()
        return notification

    def update(self, instance, validated_data):
        """
        This is only used to update the expired_date field (effectively
        deleting a notification while still leaving a record of it)
        """
        user = generic_model_access.get_profile(
            self.context['request'].user.username)
        if user.highest_role() in ['ORG_STEWARD', 'APPS_MALL_STEWARD']:
            pass
        elif not validated_data['listing']:
            raise errors.PermissionDenied('Only stewards can send system notifications')
        elif user not in validated_data['listing'].owners.all():
            raise errors.PermissionDenied('Cannot create a notification for a listing you do not own')

        instance.expires_date = validated_data['expires_date']
        instance.save()
        return instance