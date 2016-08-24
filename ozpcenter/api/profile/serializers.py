"""
Profile Serializers
"""
import logging

from django.contrib import auth


from rest_framework import serializers

from ozpcenter import models
from plugins_util import plugin_manager
from plugins_util.plugin_manager import system_anonymize_identifiable_data
import ozpcenter.model_access as generic_model_access
import ozpcenter.api.agency.model_access as agency_model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class AgencySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Agency
        fields = ('short_name', 'title')

        extra_kwargs = {
            'title': {'validators': []}
        }


class GroupSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = auth.models.Group
        fields = ('name',)


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)

    class Meta:
        # TODO: Not supposed to reference Django's User model directly, but
        # using settings.AUTH_USER_MODEL here doesn't not work
        # model = settings.AUTH_USER_MODEL
        model = auth.models.User
        fields = ('id', 'username', 'email', 'groups')

    def to_internal_value(self, data):
        ret = super(UserSerializer, self).to_internal_value(data)
        return ret

    def to_representation(self, data):
        access_control_instance = plugin_manager.get_system_access_control_plugin()
        ret = super(UserSerializer, self).to_representation(data)

        # Used to anonymize usernames
        anonymize_identifiable_data = system_anonymize_identifiable_data(self.context['request'].user.username)

        check_request_self = False
        if self.context['request'].user.id == ret['id']:
            check_request_self = True

        del ret['id']

        if anonymize_identifiable_data and not check_request_self:
            ret['username'] = access_control_instance.anonymize_value('username')
            ret['email'] = access_control_instance.anonymize_value('email')

        return ret


class ShortUserSerializer(serializers.ModelSerializer):

    class Meta:
        # TODO: not supposed to reference Django's User model directly, but
        # using settings.AUTH_USER_MODEL here doesn't not work
        # model = settings.AUTH_USER_MODEL
        model = auth.models.User
        fields = ('id', 'username', 'email')

    def to_representation(self, data):
        access_control_instance = plugin_manager.get_system_access_control_plugin()
        ret = super(ShortUserSerializer, self).to_representation(data)

        # Used to anonymize usernames
        anonymize_identifiable_data = system_anonymize_identifiable_data(self.context['request'].user.username)

        check_request_self = False
        if self.context['request'].user.id == ret['id']:
            check_request_self = True

        del ret['id']

        if anonymize_identifiable_data and not check_request_self:
            ret['username'] = access_control_instance.anonymize_value('username')
            ret['email'] = access_control_instance.anonymize_value('email')

        return ret


class ProfileSerializer(serializers.ModelSerializer):
    organizations = AgencySerializer(many=True)
    stewarded_organizations = AgencySerializer(many=True)
    user = UserSerializer()

    class Meta:
        model = models.Profile
        fields = ('id', 'display_name', 'bio', 'organizations',
            'stewarded_organizations', 'user', 'highest_role', 'dn',
            'center_tour_flag', 'hud_tour_flag', 'webtop_tour_flag')

        read_only_fields = ('id', 'bio', 'organizations', 'user',
            'highest_role')

    def to_representation(self, data):
        access_control_instance = plugin_manager.get_system_access_control_plugin()
        ret = super(ProfileSerializer, self).to_representation(data)

        # Used to anonymize usernames
        anonymize_identifiable_data = system_anonymize_identifiable_data(self.context['request'].user.username)

        check_request_self = False
        if self.context['request'].user.id == ret['id']:
            check_request_self = True

        if anonymize_identifiable_data and not check_request_self:
            ret['display_name'] = access_control_instance.anonymize_value('display_name')
            ret['bio'] = access_control_instance.anonymize_value('bio')
            ret['dn'] = access_control_instance.anonymize_value('dn')

        return ret

    def validate(self, data):
        stewarded_organizations = []

        if 'stewarded_organizations' in data:
            for org in data['stewarded_organizations']:
                stewarded_organizations.append(agency_model_access.get_agency_by_title(
                    org['title']))
        data['stewarded_organizations'] = stewarded_organizations
        return data

    def update(self, profile_instance, validated_data):
        if 'center_tour_flag' in validated_data:
            profile_instance.center_tour_flag = validated_data['center_tour_flag']

        if 'hud_tour_flag' in validated_data:
            profile_instance.hud_tour_flag = validated_data['hud_tour_flag']

        if 'webtop_tour_flag' in validated_data:
            profile_instance.webtop_tour_flag = validated_data['webtop_tour_flag']

        current_request_profile = generic_model_access.get_profile(self.context['request'].user.username)

        if current_request_profile.highest_role() == 'APPS_MALL_STEWARD':
            if validated_data['stewarded_organizations']:
                profile_instance.stewarded_organizations.clear()
                for org in validated_data['stewarded_organizations']:
                    profile_instance.stewarded_organizations.add(org)
        profile_instance.save()
        return profile_instance


class ShortProfileSerializer(serializers.ModelSerializer):
    user = ShortUserSerializer()

    class Meta:
        model = models.Profile
        fields = ('id', 'user', 'display_name', 'dn')

    def to_representation(self, data):
        access_control_instance = plugin_manager.get_system_access_control_plugin()
        ret = super(ShortProfileSerializer, self).to_representation(data)

        # Used to anonymize usernames
        anonymize_identifiable_data = system_anonymize_identifiable_data(self.context['request'].user.username)

        check_request_self = False
        if self.context['request'].user.id == ret['id']:
            check_request_self = True

        if anonymize_identifiable_data and not check_request_self:
            ret['display_name'] = access_control_instance.anonymize_value('display_name')
            ret['dn'] = access_control_instance.anonymize_value('dn')

        return ret
