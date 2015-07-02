"""
Serializers
"""
import logging

from rest_framework import serializers

import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class IntentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Intent
        depth = 1