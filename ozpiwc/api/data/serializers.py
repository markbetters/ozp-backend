"""
Serializers
"""
import json
import logging

from rest_framework import serializers

import ozpiwc.errors as errors
import ozpiwc.models as models
import ozpiwc.serializer_fields as serializer_fields

# Get an instance of a logger
logger = logging.getLogger('ozp-iwc.' + str(__name__))


class DataResourceSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=128, read_only=True)
    key = serializers.CharField(max_length=1024, read_only=True)
    entity = serializer_fields.JsonField(required=False)
    content_type = serializers.CharField(max_length=512, required=False)
    version = serializers.CharField(max_length=128, required=False)
    pattern = serializers.CharField(max_length=1024, required=False)
    permissions = serializers.CharField(max_length=8192, required=False)

    class Meta:
        model = models.DataResource

    def validate(self, data):
        data['version'] = data.get('version', None)
        data['pattern'] = data.get('pattern', None)
        data['permissions'] = data.get('permissions', None)
        data['entity'] = data.get('entity', None)

        return data

    def create(self, validated_data):
        username = self.context['request'].user.username
        content_type = self.context['request'].content_type
        data_resource = models.DataResource(
            username=username,
            key=self.context['key'],
            entity=validated_data['entity'],
            content_type=content_type,
            version=validated_data['version'],
            pattern=validated_data['pattern'],
            permissions=validated_data['permissions'])
        data_resource.save()
        logger.debug('saved NEW resource with key: {0!s}, entity: {1!s}'.format(self.context['key'], validated_data['entity']))
        return data_resource

    def update(self, instance, validated_data):
        instance.entity = validated_data['entity']
        instance.version = validated_data['version']
        instance.pattern = validated_data['pattern']
        instance.permissions = validated_data['permissions']
        instance.save()
        logger.debug('saved EXISTING resource with key: {0!s}, entity: {1!s}'.format(self.context['key'], validated_data['entity']))
        return instance
