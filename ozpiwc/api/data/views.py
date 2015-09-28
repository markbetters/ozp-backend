"""
"""
import logging

from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework import permissions
from rest_framework import generics, status
from rest_framework.response import Response

import ozpiwc.hal as hal
import ozpiwc.api.data.serializers as serializers
import ozpiwc.api.data.model_access as model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-iwc')

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
def ListDataApiView(request):
    """
    Data API
    """
    listing_root_url = hal.get_abs_url_for_iwc(request)

    data = hal.create_base_structure(request)


    logger.debug('DataApiView request to GET all items')

    return Response(data)

@api_view(['GET', 'PUT'])
@permission_classes((permissions.IsAuthenticated, ))
def DataApiView(request, key=None):
    """
    Data API

    ---
    request_serializer: serializers.DataResourceSerializer
    """
    # ensure key starts with a / and does not end with one
    if not key.startswith('/'):
        key = '/' + key
    if key.endswith('/'):
        key = key[:-1]

    listing_root_url = hal.get_abs_url_for_iwc(request)
    data = hal.create_base_structure(request)

    if request.method == 'PUT':
        try:
            logger.debug('request.data: %s' % request.data)
            instance = model_access.get_data_resource(request.user.username,
                key)
            if instance:
                serializer = serializers.DataResourceSerializer(instance,
                    data=request.data, context={'request': request, 'key': key},
                    partial=True)
                if not serializer.is_valid():
                    logger.error('%s' % serializer.errors)
                    return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
                serializer.save()
                resp = serializer.data
                resp = hal.add_hal_structure(resp, request)
                return Response(resp, status=status.HTTP_200_OK)
            else:
                serializer = serializers.DataResourceSerializer(
                    data=request.data, context={'request': request, 'key': key},
                    partial=True)

                if not serializer.is_valid():
                    logger.error('%s' % serializer.errors)
                    return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
                serializer.save()
                resp = serializer.data
                resp = hal.add_hal_structure(resp, request)
                return Response(resp, status=status.HTTP_201_CREATED)

            # data = model_access.set_data(request.user.username, key,
            #     request.data)
            # return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            raise e
            return Response(str(e),
                status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        try:
            instance = model_access.get_data_resource(request.user.username,
                key)
            serializer = serializers.DataResourceSerializer(instance,
                data=request.data, context={'request': request, 'key': key},
                partial=True)
            if not serializer.is_valid():
                logger.error('%s' % serializer.errors)
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)
            resp = serializer.data
            resp = hal.add_hal_structure(resp, request)
            return Response(resp, status=status.HTTP_200_OK)

            # data = model_access.get_data(request.user.username, key)
            # return Response(data)
        except Exception as e:
            raise e
            return Response(str(e),
                status=status.HTTP_400_BAD_REQUEST)



