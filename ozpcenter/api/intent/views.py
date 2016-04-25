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
logger = logging.getLogger('ozp-center.'+str(__name__))


class IntentViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for getting all Intent entries for all users

    Access Control
    ===============
    - All users can read
    - AppMallSteward can view

    URIs
    ======
    GET /api/intent
    Summary:
        Get a list of all system-wide categories

    Response:
        200 - Successful operation - [IntentSerializer]

    POST /api/intent/
    Summary:
        Add an intent
    Request:
        data: IntentSerializer Schema
    Response:
        200 - Successful operation - IntentSerializer

    GET /api/intent/{pk}
    Summary:
        Find an intent Entry by ID
    Response:
        200 - Successful operation - IntentSerializer

    PUT /api/intent/{pk}
    Summary:
        Update an intent Entry by ID

    PATCH /api/intent/{pk}
    Summary:
        Update (Partial) an intent Entry by ID

    DELETE /api/intent/{pk}
    Summary:
        Delete an intent Entry by ID
    """
    queryset = model_access.get_all_intents()
    serializer_class = serializers.IntentSerializer
    permission_classes = (permissions.IsAppsMallStewardOrReadOnly,)
