"""
Serializers
"""
import logging

from rest_framework import serializers

import ozpiwc.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-iwc')

class DataResourceSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=128, read_only=True)
    key = serializers.CharField(max_length=1024, read_only=True)
    entity = serializers.CharField(max_length=1048576, required=False)
    content_type = serializers.CharField(max_length=512, required=False)
    version = serializers.CharField(max_length=128, required=False)
    pattern = serializers.CharField(max_length=1024, required=False)
    collection = serializers.CharField(max_length=8192, required=False)
    permissions = serializers.CharField(max_length=8192, required=False)

    class Meta:
        model = models.DataResource

    def validate(self, data):
        return data

    def create(self, validated_data):
        username = self.context['request'].user.username
        data_resource = models.DataResource(
            username=username,
            key=self.context['key'],
            entity=validated_data['entity'],
            content_type=validated_data['content_type'],
            version=validated_data['version'],
            pattern=validated_data['pattern'],
            collection=validated_data['collection'],
            permissions=validated_data['permissions'])
        data_resource.save()
        return data_resource

    def update(self, instance, validated_data):
        instance.entity = validated_data['entity']
        instance.content_type = validated_data['content_type']
        instance.version = validated_data['version']
        instance.pattern = validated_data['pattern']
        instance.collection = validated_data['collection']
        instance.permissions = validated_data['permissions']
        instance.save()
        return instance
