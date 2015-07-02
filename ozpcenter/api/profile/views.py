"""
Views
"""
import logging

from rest_framework import viewsets

import ozpcenter.api.profile.serializers as serializers
import ozpcenter.models as models
import ozpcenter.permissions as permissions

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class ProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsUser,)
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    filter_fields = ('highest_role',)