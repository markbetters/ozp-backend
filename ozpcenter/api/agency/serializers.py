"""
Serializers
"""
import logging

from rest_framework import serializers

import ozpcenter.api.image.serializers as icon_serializers
import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class AgencySerializer(serializers.HyperlinkedModelSerializer):
    icon = icon_serializers.IconSerializer()
    class Meta:
        model = models.Agency
        depth = 2