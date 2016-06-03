"""
Views
"""
import logging

from rest_framework import viewsets

from ozpcenter import models
from ozpcenter import permissions
import ozpcenter.api.category.model_access as model_access
import ozpcenter.api.category.serializers as serializers

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for getting all category entries for all users

    Access Control
    ===============
    - All users can read
    - AppMallSteward can view

    URIs
    ======
    GET /api/category
    Summary:
        Get a list of all system-wide categories

    Response:
        200 - Successful operation - [CategorySerializer]

    POST /api/category/
    Summary:
        Add an category
    Request:
        data: CategorySerializer Schema
    Response:
        200 - Successful operation - CategorySerializer

    GET /api/category/{pk}
    Summary:
        Find an category Entry by ID
    Response:
        200 - Successful operation - CategorySerializer

    PUT /api/category/{pk}
    Summary:
        Update an category Entry by ID

    PATCH /api/category/{pk}
    Summary:
        Update (Partial) an category Entry by ID

    DELETE /api/category/{pk}
    Summary:
        Delete an category Entry by ID
    """
    queryset = model_access.get_all_categories()
    serializer_class = serializers.CategorySerializer
    filter_fields = ('title',)
    permission_classes = (permissions.IsAppsMallStewardOrReadOnly,)
