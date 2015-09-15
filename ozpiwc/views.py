"""
"""
import logging

from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework import permissions
from rest_framework import generics, status
from rest_framework.response import Response

import ozpcenter.model_access as model_access
import ozpiwc.hal as hal

# Get an instance of a logger
logger = logging.getLogger('ozp-iwc')

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
def RootApiView(request):
    """
    IWC Root
    """
    root_url = request.build_absolute_uri('/')
    profile = model_access.get_profile(request.user.username)
    data = hal.create_base_structure(request)
    data[hal.APPLICATION_REL] = {
        "href": '%sapplication/' % (hal.get_abs_url_for_profile(request, profile.id))
    }
    data[hal.INTENT_REL] = {
        "href": '%sintent/' % (hal.get_abs_url_for_profile(request, profile.id))
    }
    data[hal.SYSTEM_REL] = {
        "href": '%siwc-api/system/' % (root_url)
    }
    data[hal.USER_REL] = {
        "href": '%s' % (hal.get_abs_url_for_profile(request, profile.id))
    }
    data[hal.USER_DATA_REL] = {
        "href": '%sdata/' % (hal.get_abs_url_for_profile(request, profile.id))
    }

    # add embedded data
    data["_embedded"][hal.USER_REL] = {
        "username": profile.user.username,
        "name": profile.display_name,
        "_links": {
            "self": {
                "href": '%s' % (hal.get_abs_url_for_profile(request, profile.id))
            }
        }
    }
    return Response(data)