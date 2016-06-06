"""
Views
"""
import logging

from rest_framework import viewsets

from ozpcenter import permissions
import ozpcenter.api.contact_type.model_access as model_access
import ozpcenter.api.contact_type.serializers as serializers

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class ContactTypeViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for getting all ContactType entries for all users

    Access Control
    ===============
    - All users can read
    - AppMallSteward can view

    URIs
    ======
    GET /api/contact_type
    Summary:
        Get a list of all system-wide ContactType

    Response:
        200 - Successful operation - [ContactTypeSerializer]

    POST /api/contact_type/
    Summary:
        Add an ContactType
    Request:
        data: ContactTypeSerializer Schema
    Response:
        200 - Successful operation - ContactTypeSerializer

    GET /api/contact_type/{pk}
    Summary:
        Find an ContactType Entry by ID
    Response:
        200 - Successful operation - ContactTypeSerializer

    PUT /api/contact_type/{pk}
    Summary:
        Update an ContactType Entry by ID

    PATCH /api/contact_type/{pk}
    Summary:
        Update (Partial) an ContactType Entry by ID

    DELETE /api/contact_type/{pk}
    Summary:
        Delete an ContactType Entry by ID
    """
    queryset = model_access.get_all_contact_types()
    serializer_class = serializers.ContactTypeSerializer
    permission_classes = (permissions.IsAppsMallStewardOrReadOnly,)
