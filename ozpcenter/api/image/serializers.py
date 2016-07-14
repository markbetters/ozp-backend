"""
Image Serializers

Some of these serializers use the HyperlinkedModelSerializer base class, as that
provides the 'url' field, which makes it easier for the front-end to consume
"""
from PIL import Image
import logging

from rest_framework import serializers

from ozpcenter import models
from plugins_util.plugin_manager import system_has_access_control
import ozpcenter.model_access as generic_model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class ImageTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.ImageType
        fields = ('name',)


class ImageSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Image
        fields = ('url', 'id', 'security_marking')

    def validate_security_marking(self, value):
        # don't allow user to select a security marking that is above
        # their own access level
        profile = generic_model_access.get_profile(
            self.context['request'].user.username)

        if value:
            if not system_has_access_control(profile.user.username, value):
                raise serializers.ValidationError(
                    'Security marking too high for current user')
        else:
            raise serializers.ValidationError(
                'Security marking is required')

        return value


class ShortImageSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Image
        fields = ('url', 'id', 'security_marking')

        extra_kwargs = {
            "id": {
                "read_only": False,
                "required": False,
            }
        }


class ImageCreateSerializer(serializers.Serializer):
    # image_type.name
    image_type = serializers.CharField(max_length=200)
    image = serializers.ImageField()
    file_extension = serializers.CharField(max_length=10)
    security_marking = serializers.CharField(max_length=1024)

    def validate_security_marking(self, value):
        # don't allow user to select a security marking that is above
        # their own access level
        profile = generic_model_access.get_profile(
            self.context['request'].user.username)

        if value:
            if not system_has_access_control(profile.user.username, value):
                raise serializers.ValidationError(
                    'Security marking too high for current user')
        else:
            raise serializers.ValidationError(
                'Security marking is required')

        return value

    def create(self, validated_data):
        img = Image.open(validated_data['image'])
        created_image = models.Image.create_image(img,
            image_type=validated_data['image_type'],
            security_marking=validated_data['security_marking'],
            file_extension=validated_data['file_extension'])
        return created_image

    def to_representation(self, obj):
        """
        Since this serializer's fields don't map identically to that of
        models.Image, explicity set the output (read) representation
        """
        return {
            'id': obj.id,
            'security_marking': obj.security_marking
        }
