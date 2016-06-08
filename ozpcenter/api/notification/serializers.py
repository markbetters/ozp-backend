"""
Serializers
"""
import logging

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from ozpcenter import errors
from ozpcenter import models
import ozpcenter.api.listing.model_access as listing_model_access
import ozpcenter.model_access as generic_model_access
import ozpcenter.api.notification.model_access as model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


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
        fields = ('id', 'title')

        extra_kwargs = {
            'title': {'validators': []}
        }


class NotificationSerializer(serializers.ModelSerializer):
    author = ShortProfileSerializer(required=False)
    listing = NotificationListingSerializer(required=False)

    class Meta:
        model = models.Notification
        fields = ('id', 'created_date', 'message', 'expires_date', 'author',
            'listing')

    def validate(self, validated_data):
        """ Responsible of cleaning and validating user input data """
        initial_data = self.initial_data
        username = self.context['request'].user.username

        if 'message' not in validated_data and self.context['request'].method == 'POST':
            raise serializers.ValidationError('Messsage field is required for POST Request')

        # TODO: Figure how to get listing data using validated data
        listing = initial_data.get('listing')
        if listing and listing.get('id'):
            try:
                validated_data['listing'] = listing_model_access.get_listing_by_id(
                    username, initial_data['listing']['id'], True)
            except ObjectDoesNotExist:
                raise serializers.ValidationError('Valid Listing ID is required, Could not find listing')
        else:
            validated_data['listing'] = None

        return validated_data

    def _check_permissions(self, validated_data):
        """
        Check Permission of who can make and update Notifications

        Args:
            validated_data
        """
        username = self.context['request'].user.username
        user = generic_model_access.get_profile(username)
        listing = validated_data['listing']

        if user.highest_role() in ['ORG_STEWARD', 'APPS_MALL_STEWARD']:
            return True
        elif not listing:
            raise errors.PermissionDenied('Only stewards can send system notifications')
        elif user not in listing.owners.all():
            raise errors.PermissionDenied('Cannot create a notification for a listing you do not own')
        return True

    def create(self, validated_data):
        """
        Used to create notifications
        """
        if self._check_permissions(validated_data):
            username = self.context['request'].user.username
            notification = model_access.create_notification(validated_data['expires_date'],
                                                            username,
                                                            validated_data['message'],
                                                            validated_data['listing'])
            return notification
        else:
            raise errors.PermissionDenied('Current user does not have permission')

    def update(self, instance, validated_data):
        """
        This is only used to update the expired_date field (effectively
        deleting a notification while still leaving a record of it)
        """
        if self._check_permissions(validated_data):
            notification = model_access.update_notification(instance,
                                                            validated_data['expires_date'])
            return notification
        else:
            raise errors.PermissionDenied('Current User does not have permission')
