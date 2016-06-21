"""
Category Serializers
"""
import logging

from rest_framework import serializers

from ozpcenter import models

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
