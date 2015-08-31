"""
Serializers
"""
import logging

from rest_framework import serializers

import ozpcenter.models as models
import ozpcenter.api.image.serializers as image_serializers

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class IntentSerializer(serializers.ModelSerializer):
    icon = image_serializers.ShortImageSerializer()
    class Meta:
        model = models.Intent
        depth = 1

    def validate(self, data):
        icon = data.get('icon', None)
        if icon:
            data['icon'] = models.Image.objects.get(
                id=data['icon']['id'])
        else:
            data['icon'] = None
        return data

