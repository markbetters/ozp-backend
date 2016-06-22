"""
Agency Serializers
"""
import logging

from rest_framework import serializers

from ozpcenter import models


# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class AgencySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Agency
        depth = 2
        fields = ('title', 'short_name', 'id')


class MinimalAgencySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Agency
        fields = ('short_name',)
