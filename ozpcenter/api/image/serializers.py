"""
Serializers
"""
import logging

from rest_framework import serializers

from PIL import Image

import ozpcenter.models as models
import ozpcenter.api.access_control.serializers as access_control_serializers

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class ImageTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ImageType
        fields = ('name',)

class ImageSerializer(serializers.HyperlinkedModelSerializer):
    access_control = access_control_serializers.AccessControlSerializer()
    class Meta:
        model = models.Image
        fields = ('url', 'id', 'access_control')


class AccessControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AccessControl
        fields = ('title',)

        extra_kwargs = {
            'title': {'validators': []}
        }

class ShortImageSerializer(serializers.HyperlinkedModelSerializer):
    access_control = AccessControlSerializer(required=False)
    class Meta:
        model = models.Image
        fields = ('url', 'id', 'access_control')

        extra_kwargs = {
            'access_control': {'validators': []},
            "id": {
                "read_only": False,
                "required": False,
            }
        }


class ImageCreateSerializer(serializers.Serializer):
    # access_control.title
    access_control = serializers.CharField(max_length=200)
    # image_type.name
    image_type = serializers.CharField(max_length=200)
    image = serializers.ImageField()
    file_extension = serializers.CharField(max_length=10)

    def create(self, validated_data):
        img = Image.open(validated_data['image'])
        created_image = models.Image.create_image(img,
            image_type=validated_data['image_type'],
            access_control=validated_data['access_control'],
            file_extension=validated_data['file_extension'])
        return created_image

    def to_representation(self, obj):
        """
        Since this serializer's fields don't map identically to that of
        models.Image, explicity set the output (read) representation
        """
        return {
            'id': obj.id,
            'access_control': str(obj.access_control)
        }

