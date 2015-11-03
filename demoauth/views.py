"""
Endpoints similar to what is provided by our real external authorization
service
"""
import json
import logging
from pprint import pprint

from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.decorators import renderer_classes
from rest_framework import permissions
from rest_framework import renderers as rf_renderers
from rest_framework import generics, status
from rest_framework.response import Response

import demoauth.utils as utils

# Get an instance of a logger
logger = logging.getLogger('demo-auth')

@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def UserDnView(request, dn):
    logger.debug('looking for dn: %s' % dn)
    user_data = utils.get_auth_data(dn)
    if not user_data:
        return Response('User not found', status=status.HTTP_404_NOT_FOUND)
    return Response(user_data, status=status.HTTP_200_OK)

# TODO: groups
@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def UserInGroupView(request, project, group, dn):
    logger.debug('is user %s in project %s, group %s' % (dn, project, group))
    user_data = utils.get_auth_data(dn)
    if not user_data:
        return Response('User not found', status=status.HTTP_404_NOT_FOUND)

    if utils.is_user_in_group(dn, group):
        return Response({"is_member": True}, status=status.HTTP_200_OK)
    else:
        return Response({"is_member": False}, status=status.HTTP_200_OK)
