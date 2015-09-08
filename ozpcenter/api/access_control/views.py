"""
Views
"""
import logging

from rest_framework import viewsets

import ozpcenter.permissions as permissions
import ozpcenter.api.access_control.serializers as serializers
import ozpcenter.api.access_control.model_access as model_access
import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class AccessControlViewSet(viewsets.ModelViewSet):
    queryset = model_access.get_all_access_controls()
    serializer_class = serializers.AccessControlSerializer
    permission_classes = (permissions.IsAppsMallStewardOrReadOnly,)