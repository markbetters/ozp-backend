"""
Views
"""
from rest_framework import viewsets

import ozpcenter.serializers as serializers
import ozpcenter.models as models

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer