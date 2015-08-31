"""
Views
"""
import logging

from rest_framework import viewsets

import ozpcenter.permissions as permissions
import ozpcenter.api.access_control.serializers as serializers
import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class AccessControlViewSet(viewsets.ModelViewSet):
    queryset = models.AccessControl.objects.all()
    serializer_class = serializers.AccessControlSerializer
    permission_classes = (permissions.IsAppsMallStewardOrReadOnly,)