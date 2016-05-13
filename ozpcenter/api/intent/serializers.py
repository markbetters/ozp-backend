"""
Serializers
"""
import logging

from rest_framework import serializers

import ozpcenter.models as models
import ozpcenter.api.image.serializers as image_serializers
import ozpcenter.api.image.model_access as image_model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class IntentSerializer(serializers.ModelSerializer):
    icon = image_serializers.ShortImageSerializer()

    class Meta:
        model = models.Intent
        depth = 1

    def validate(self, data):
        icon = data.get('icon', None)
        if icon:
            data['icon'] = image_model_access.get_image_by_id(
                data['icon']['id'])
        else:
            data['icon'] = None
        return data
