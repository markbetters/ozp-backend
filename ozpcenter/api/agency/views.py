"""
Views
"""
import logging

from rest_framework import viewsets

import ozpcenter.permissions as permissions
import ozpcenter.api.agency.serializers as serializers
import ozpcenter.models as models
import ozpcenter.api.agency.model_access as model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class AgencyViewSet(viewsets.ModelViewSet):
    queryset = model_access.get_all_agencies()
    serializer_class = serializers.AgencySerializer
    permission_classes = (permissions.IsAppsMallStewardOrReadOnly,)