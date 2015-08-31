"""
Views
"""
import logging

from rest_framework import viewsets

import ozpcenter.permissions as permissions
import ozpcenter.api.category.serializers as serializers
import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    filter_fields = ('title',)
    permission_classes = (permissions.IsAppsMallStewardOrReadOnly,)
