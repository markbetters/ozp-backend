"""
Serializers
"""
import logging

from rest_framework import serializers

import ozpcenter.api.image.serializers as image_serializers
import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class AgencySerializer(serializers.HyperlinkedModelSerializer):
    icon = image_serializers.ImageSerializer()
    class Meta:
        model = models.Agency
        depth = 2

class MinimalAgencySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Agency
        fields = ('short_name',)