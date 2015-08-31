"""
Views
"""
import logging

from rest_framework import viewsets

import ozpcenter.permissions as permissions
import ozpcenter.api.agency.serializers as serializers
import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class AgencyViewSet(viewsets.ModelViewSet):
    queryset = models.Agency.objects.all()
    serializer_class = serializers.AgencySerializer
    permission_classes = (permissions.IsAppsMallStewardOrReadOnly,)