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

    # remove groups, since this doesn't come back in this HTTP endpoint in the
    # actual authorization service
    user_data.pop('groups', None)
    return Response(user_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((permissions.AllowAny, ))
def UserGroupsView(request, dn, project):
    user_data = {"groups": utils.get_auth_data(dn)['groups']}
    if not user_data:
        return Response('User not found', status=status.HTTP_404_NOT_FOUND)
    return Response(user_data, status=status.HTTP_200_OK)
