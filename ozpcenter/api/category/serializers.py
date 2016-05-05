"""
Serializers
"""
import logging

from rest_framework import serializers

import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
