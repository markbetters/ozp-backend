"""
Views
"""
import logging

from rest_framework import viewsets

import ozpcenter.permissions as permissions
import ozpcenter.api.intent.serializers as serializers
import ozpcenter.models as models
import ozpcenter.api.intent.model_access as model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class IntentViewSet(viewsets.ModelViewSet):
    queryset = model_access.get_all_intents()
    serializer_class = serializers.IntentSerializer
    permission_classes = (permissions.IsAppsMallStewardOrReadOnly,)