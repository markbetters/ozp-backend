"""
Serializers for the API
"""
from rest_framework import serializers

import ozpcenter.models as models

class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Profile
