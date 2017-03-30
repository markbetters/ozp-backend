"""
Subscription Serializers
"""
import logging

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from ozpcenter import models
from plugins_util import plugin_manager

import ozpcenter.api.subscription.model_access as model_access
import ozpcenter.api.listing.model_access as listing_model_access
import ozpcenter.api.category.model_access as category_model_access
import ozpcenter.model_access as generic_model_access
import ozpcenter.api.profile.serializers as profile_serializers

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class SubscriptionSerializer(serializers.ModelSerializer):
    target_profile = profile_serializers.ShortProfileSerializer(required=False)

    class Meta:
        model = models.Subscription
        fields = ('id', 'target_profile', 'entity_type', 'entity_id', )

    def to_representation(self, data):
        ret = super(SubscriptionSerializer, self).to_representation(data)
        try:
            if ret['entity_type'] == 'category':
                ret['entity_description'] = category_model_access.get_category_by_id(ret['entity_id'], True).title
            elif ret['entity_type']  == 'tag':
                ret['entity_description'] = listing_model_access.get_tag_by_id(ret['entity_id'], True).name
        except ObjectDoesNotExist:
            # Incase Category/Tag has been delete
            ret['entity_description'] = 'OBJECT NOT FOUND'

        return ret

    def validate(self, validated_data):
        """ Responsible of cleaning and validating user input data """
        validated_data['error'] = None
        username = self.context['request'].user.username

        if 'entity_type' not in validated_data or 'entity_id' not in validated_data:
            raise serializers.ValidationError('Subscriptions can only be one type.')

        entity_type = validated_data.get('entity_type')
        entity_id = validated_data.get('entity_id')
        if entity_type and entity_id:
            try:
                if entity_type == 'category':
                    validated_data['entity_id'] = category_model_access.get_category_by_id(entity_id, True).id
                elif entity_type == 'tag':
                    validated_data['entity_id'] = listing_model_access.get_tag_by_id(entity_id, True).id
                else:
                    raise serializers.ValidationError('entity_type is not valid')
            except ObjectDoesNotExist:
                raise serializers.ValidationError('Could not find object')
        else:
            raise serializers.ValidationError('entity_type or entity_id missing')

        return validated_data

    def create(self, validated_data):
        """
        Used to create subscriptions
        """
        if validated_data['error']:
            raise serializers.ValidationError('{0}'.format(validated_data['error']))

        username = self.context['request'].user.username
        subscription = model_access.create_subscription(username,
                                                        validated_data['entity_type'],
                                                        validated_data.get('entity_id'))
        return subscription

    def update(self, instance, validated_data):
        """
        This is only used to update the expired_date field (effectively
        deleting a subscription while still leaving a record of it)
        """
        if validated_data['error']:
            raise serializers.ValidationError('{0}'.format(validated_data['error']))

        username = self.context['request'].user.username
        subscription = model_access.update_subscription(username,
                                                        instance,
                                                        validated_data['expires_date'])
        return subscription
