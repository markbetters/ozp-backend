"""
Views
"""
import logging

from rest_framework import viewsets

import ozpcenter.permissions as permissions
import ozpcenter.api.intent.serializers as serializers
import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class IntentViewSet(viewsets.ModelViewSet):
    queryset = models.Intent.objects.all()
    serializer_class = serializers.IntentSerializer
    permission_classes = (permissions.IsAppsMallStewardOrReadOnly,)