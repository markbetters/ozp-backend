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
logger = logging.getLogger('ozp-iwc')

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
@renderer_classes((renderers.RootResourceRenderer, rf_renderers.JSONRenderer))
def RootApiView(request):
    """
    IWC Root
    """
    root_url = request.build_absolute_uri('/')
    profile = model_access.get_profile(request.user.username)
    data = hal.create_base_structure(request)
    data['_links'][hal.APPLICATION_REL] = {
        "href": '%sself/application/' % (hal.get_abs_url_for_iwc(request))
    }
    data['_links'][hal.INTENT_REL] = {
        "href": '%sself/intent/' % (hal.get_abs_url_for_iwc(request))
    }
    data['_links'][hal.SYSTEM_REL] = {
        "href": '%siwc-api/system/' % (root_url)
    }
    data['_links'][hal.USER_REL] = {
        "href": '%sself/' % (hal.get_abs_url_for_iwc(request))
    }
    data['_links'][hal.USER_DATA_REL] = {
        "href": '%sself/data/' % (hal.get_abs_url_for_iwc(request))
    }

    # add embedded data
    data["_embedded"][hal.USER_REL] = {
        "username": profile.user.username,
        "name": profile.display_name,
        "_links": {
            "self": {
                "href": '%sself/' % (hal.get_abs_url_for_iwc(request))
            }
        }
    }

    data["_embedded"][hal.SYSTEM_REL] = {
        "version": '1.0',
        "name": 'TBD',
        "_links": {
            "self": {
                "href": '%ssystem/' % (hal.get_abs_url_for_iwc(request))
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
    profile = model_access.get_profile(request.user.username)
    data = {'username': profile.user.username, 'id': profile.id,
        'display_name': profile.display_name}
    data = hal.add_hal_structure(data, request)
    return Response(data)