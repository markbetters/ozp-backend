"""
Views

TODO: POST on api/image (create/edit listing) w/ contentType and id fields
"""
import logging

from rest_framework import viewsets

import ozpcenter.api.image.serializers as serializers
import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class IconViewSet(viewsets.ModelViewSet):
    queryset = models.Image.objects.all()
    serializer_class = serializers.IconSerializer