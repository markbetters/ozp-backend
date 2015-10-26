"""
"""
import logging

from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.decorators import renderer_classes
from rest_framework import permissions
from rest_framework import renderers as rf_renderers
from rest_framework import generics, status
from rest_framework.response import Response

import ozpcenter.api.intent.model_access as intent_model_access
import ozpcenter.api.intent.serializers as intent_serializers
import ozpcenter.model_access as model_access
import ozpiwc.hal as hal
import ozpiwc.renderers as renderers

# Get an instance of a logger
logger = logging.getLogger('ozp-iwc')

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
@renderer_classes((renderers.IntentListResourceRenderer, rf_renderers.JSONRenderer))
def IntentListView(request):
    """
    List of intents
    """
    if not hal.validate_version(request.META.get('HTTP_ACCEPT')):
        return Response('Invalid version requested',
            status=status.HTTP_406_NOT_ACCEPTABLE)

    root_url = hal.get_abs_url_for_iwc(request)
    profile = model_access.get_profile(request.user.username)
    data = hal.create_base_structure(request,
        hal.generate_content_type(request.accepted_media_type))
    intents = intent_model_access.get_all_intents()
    items = []
    for i in intents:
        item = {"href": '%sintent/%s/' % (root_url, i.id)}
        items.append(item)
    data['_links']['item'] = items

    return Response(data)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
@renderer_classes((renderers.IntentResourceRenderer, rf_renderers.JSONRenderer))
def IntentView(request, id='0'):
    """
    Single intent
    """
    if not hal.validate_version(request.META.get('HTTP_ACCEPT')):
        return Response('Invalid version requested',
            status=status.HTTP_406_NOT_ACCEPTABLE)

    root_url = hal.get_abs_url_for_iwc(request)
    profile = model_access.get_profile(request.user.username)

    queryset = intent_model_access.get_intent_by_id(id)
    if not queryset:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = intent_serializers.IntentSerializer(queryset,
            context={'request': request})
    data = serializer.data
    data = hal.add_hal_structure(data, request,
        hal.generate_content_type(request.accepted_media_type))

    return Response(data)
