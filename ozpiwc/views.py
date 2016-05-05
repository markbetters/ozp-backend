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

import ozpcenter.model_access as model_access
import ozpiwc.renderers as renderers
import ozpiwc.hal as hal

# Get an instance of a logger
logger = logging.getLogger('ozp-iwc.' + str(__name__))


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
@renderer_classes((renderers.RootResourceRenderer, rf_renderers.JSONRenderer))
def RootApiView(request):
    """
    IWC Root
    """
    if not hal.validate_version(request.META.get('HTTP_ACCEPT')):
        return Response('Invalid version requested',
            status=status.HTTP_406_NOT_ACCEPTABLE)

    root_url = request.build_absolute_uri('/')
    profile = model_access.get_profile(request.user.username)
    data = hal.create_base_structure(request,
        hal.generate_content_type(request.accepted_media_type))
    data['_links'][hal.APPLICATION_REL] = {
        "href": '%sself/application/' % (hal.get_abs_url_for_iwc(request)),
        "type": hal.generate_content_type(
            renderers.ApplicationListResourceRenderer.media_type)
    }
    data['_links'][hal.INTENT_REL] = {
        "href": '%sself/intent/' % (hal.get_abs_url_for_iwc(request)),
        "type": hal.generate_content_type(
            renderers.IntentListResourceRenderer.media_type)
    }
    data['_links'][hal.SYSTEM_REL] = {
        "href": '%siwc-api/system/' % (root_url),
        "type": hal.generate_content_type(
            renderers.SystemResourceRenderer.media_type)
    }
    data['_links'][hal.USER_REL] = {
        "href": '%sself/' % (hal.get_abs_url_for_iwc(request)),
        "type": hal.generate_content_type(
            renderers.UserResourceRenderer.media_type)
    }
    data['_links'][hal.USER_DATA_REL] = {
        "href": '%sself/data/' % (hal.get_abs_url_for_iwc(request)),
        "type": hal.generate_content_type(
            renderers.DataObjectListResourceRenderer.media_type)
    }

    data['_links'][hal.DATA_ITEM_REL] = {
        "href": '%sself/data/{+resource}' % (hal.get_abs_url_for_iwc(request)),
        "type": hal.generate_content_type(renderers.DataObjectResourceRenderer.media_type),
        "templated": True
    }

    data['_links'][hal.APPLICATION_ITEM_REL] = {
        "href": '%slisting/{+resource}/' % (hal.get_abs_url_for_iwc(request)),
        "type": hal.generate_content_type(renderers.ApplicationResourceRenderer.media_type),
        "templated": True
    }

    # add embedded data
    data["_embedded"][hal.USER_REL] = {
        "username": profile.user.username,
        "name": profile.display_name,
        "_links": {
            "self": {
                "href": '%sself/' % (hal.get_abs_url_for_iwc(request)),
                "type": hal.generate_content_type(
                    renderers.UserResourceRenderer.media_type)
            }
        }
    }

    data["_embedded"][hal.SYSTEM_REL] = {
        "version": '1.0',
        "name": 'TBD',
        "_links": {
            "self": {
                "href": '%ssystem/' % (hal.get_abs_url_for_iwc(request)),
                "type": hal.generate_content_type(
                    renderers.SystemResourceRenderer.media_type)
            }
        }
    }
    return Response(data)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
@renderer_classes((renderers.UserResourceRenderer, rf_renderers.JSONRenderer))
def UserView(request):
    """
    User info
    """
    if not hal.validate_version(request.META.get('HTTP_ACCEPT')):
        return Response('Invalid version requested',
            status=status.HTTP_406_NOT_ACCEPTABLE)

    profile = model_access.get_profile(request.user.username)
    data = {'username': profile.user.username, 'id': profile.id,
        'display_name': profile.display_name}
    data = hal.add_hal_structure(data, request,
        hal.generate_content_type(
            request.accepted_media_type))
    return Response(data)
