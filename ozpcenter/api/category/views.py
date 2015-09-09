"""
Views
"""
import logging

from rest_framework import viewsets

import ozpcenter.permissions as permissions
import ozpcenter.api.category.serializers as serializers
import ozpcenter.models as models
import ozpcenter.api.category.model_access as model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = model_access.get_all_categories()
    serializer_class = serializers.CategorySerializer
    filter_fields = ('title',)
    permission_classes = (permissions.IsAppsMallStewardOrReadOnly,)
