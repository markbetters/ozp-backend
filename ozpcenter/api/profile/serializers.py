"""
Serializers
"""
import logging

import django.contrib.auth

from rest_framework import serializers

import ozpcenter.models as models
import ozpcenter.api.agency.model_access as agency_model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Agency
        fields = ('short_name', 'title')

        extra_kwargs = {
            'title': {'validators': []}
        }

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = django.contrib.auth.models.Group
        fields = ('name',)

class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
    class Meta:
        # TODO: not supposed to reference Django's User model directly, but
        # using settings.AUTH_USER_MODEL here doesn't not work
        # model = settings.AUTH_USER_MODEL
        model = django.contrib.auth.models.User
        fields = ('username', 'email', 'groups')

class ShortUserSerializer(serializers.ModelSerializer):
    class Meta:
        # TODO: not supposed to reference Django's User model directly, but
        # using settings.AUTH_USER_MODEL here doesn't not work
        # model = settings.AUTH_USER_MODEL
        model = django.contrib.auth.models.User
        fields = ('username', 'email')

class ProfileSerializer(serializers.ModelSerializer):
    organizations = AgencySerializer(many=True)
    stewarded_organizations = AgencySerializer(many=True)
    user = UserSerializer()
    class Meta:
        model = models.Profile
        fields = ('id', 'display_name', 'bio', 'organizations',
            'stewarded_organizations', 'user', 'highest_role', 'dn')
        read_only_fields = ('id', 'bio', 'organizations', 'user',
            'highest_role')

    def validate(self, data):
        stewarded_organizations = []

        if 'stewarded_organizations' in data:
            for org in data['stewarded_organizations']:
                stewarded_organizations.append(agency_model_access.get_agency_by_title(
                    org['title']))
        data['stewarded_organizations'] = stewarded_organizations
        return data

    def update(self, instance, validated_data):
        if validated_data['stewarded_organizations']:
            instance.stewarded_organizations.clear()
            for org in validated_data['stewarded_organizations']:
                instance.stewarded_organizations.add(org)
        return instance

class ShortProfileSerializer(serializers.ModelSerializer):
    user = ShortUserSerializer()
    class Meta:
        model = models.Profile
        fields = ('user', 'display_name', 'id', 'dn')