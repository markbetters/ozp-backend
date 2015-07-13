"""
Serializers
"""
import logging

import django.contrib.auth

from rest_framework import serializers

import ozpcenter.models as models
import ozpcenter.api.agency.serializers as agency_serializers

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = django.contrib.auth.models.Group
        fields = ('name',)

class UserSerializer(serializers.HyperlinkedModelSerializer):
    groups = GroupSerializer(many=True)
    class Meta:
        # TODO: not supposed to reference Django's User model directly, but
        # using settings.AUTH_USER_MODEL here doesn't not work
        # model = settings.AUTH_USER_MODEL
        model = django.contrib.auth.models.User
        fields = ('username', 'email', 'groups')

class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    organizations = agency_serializers.MinimalAgencySerializer(many=True)
    stewarded_organizations = agency_serializers.MinimalAgencySerializer(many=True)
    user = UserSerializer()
    class Meta:
        model = models.Profile