"""
Views
"""
import logging

from rest_framework import viewsets

import ozpcenter.permissions as permissions
import ozpcenter.api.contact_type.serializers as serializers
import ozpcenter.models as models
import ozpcenter.api.contact_type.model_access as model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center')


class ContactTypeViewSet(viewsets.ModelViewSet):
    queryset = model_access.get_all_contact_types()
    serializer_class = serializers.ContactTypeSerializer
    permission_classes = (permissions.IsAppsMallStewardOrReadOnly,)
