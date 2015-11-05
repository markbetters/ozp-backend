"""
Serializers

Some of these serializers use the HyperlinkedModelSerializer base class, as that
provides the 'url' field, which makes it easier for the front-end to consume
"""
import logging

from rest_framework import serializers

from PIL import Image

import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class ImageTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ImageType
        fields = ('name',)

class ImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Image
        fields = ('url', 'id', 'security_marking')


class ShortImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Image
        fields = ('url', 'id', 'security_marking')

        extra_kwargs = {
            'security_marking': {
                'validators': [],
                'required': False},
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

