"""
Views
"""
import logging

from rest_framework import viewsets

import ozpcenter.image.serializers as serializers
import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class IconViewSet(viewsets.ModelViewSet):
    queryset = models.Icon.objects.all()
    serializer_class = serializers.IconSerializer