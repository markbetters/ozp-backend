"""
Serializers
"""
import logging

from rest_framework import serializers

import ozpcenter.api.image.serializers as image_serializers
import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class IntentSerializer(serializers.HyperlinkedModelSerializer):
    icon = image_serializers.ImageSerializer()
    class Meta:
        model = models.Intent
        depth = 1