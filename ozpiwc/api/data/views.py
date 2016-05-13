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

import ozpiwc.hal as hal
import ozpiwc.renderers as renderers
import ozpiwc.api.data.serializers as serializers
import ozpiwc.api.data.model_access as model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-iwc.' + str(__name__))


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
@renderer_classes((renderers.DataObjectListResourceRenderer, rf_renderers.JSONRenderer))
def ListDataApiView(request):
    """
    List all data entries for the user
    """
    if not hal.validate_version(request.META.get('HTTP_ACCEPT')):
        return Response('Invalid version requested',
            status=status.HTTP_406_NOT_ACCEPTABLE)

    listing_root_url = hal.get_abs_url_for_iwc(request)

    data = hal.create_base_structure(request,
        hal.generate_content_type(request.accepted_media_type))

    keys = model_access.get_all_keys(request.user.username)
    embedded_items = []
    for k in keys:
        # remove the leading /
        k = k[1:]
        url = hal.get_abs_url_for_iwc(request) + 'self/data/' + k
        data = hal.add_link_item(url, data, hal.generate_content_type(
            renderers.DataObjectResourceRenderer.media_type))

        # add data items to _embedded
        key = '/' + k
        try:
            instance = model_access.get_data_resource(request.user.username,
                key)
            if not instance:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = serializers.DataResourceSerializer(instance,
                data=request.data, context={'request': request, 'key': key},
                partial=True)
            if not serializer.is_valid():
                logger.error('%s' % serializer.errors)
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)
            item = hal.add_hal_structure(serializer.data, request,
                hal.generate_content_type(
                    renderers.DataObjectResourceRenderer.media_type))
            item['_links']['self']['href'] += k
            embedded_items.append(item)
        except Exception as e:
            # TODO debug
            raise e

        data['_embedded']['item'] = embedded_items

    return Response(data)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes((permissions.IsAuthenticated, ))
@renderer_classes((renderers.DataObjectResourceRenderer, rf_renderers.JSONRenderer))
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

    logger.debug('Got IWC Data request for key %s' % key)

    if not hal.validate_version(request.META.get('HTTP_ACCEPT')):
        return Response('Invalid version requested',
            status=status.HTTP_406_NOT_ACCEPTABLE)

    listing_root_url = hal.get_abs_url_for_iwc(request)
    data = hal.create_base_structure(request,
        hal.generate_content_type(
            request.accepted_media_type))

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
                resp = hal.add_hal_structure(resp, request,
                    hal.generate_content_type(
                        request.accepted_media_type))
                return Response(resp, status=status.HTTP_200_OK)
            else:
                serializer = serializers.DataResourceSerializer(
                    data=request.data, context={'request': request, 'key': key},
                    partial=True)
                if not serializer.is_valid():
                    logger.error('ERROR: %s' % serializer.errors)
                    return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
                serializer.save()
                resp = serializer.data
                resp = hal.add_hal_structure(resp, request,
                    hal.generate_content_type(
                        request.accepted_media_type))
                return Response(resp, status=status.HTTP_201_CREATED)
        except Exception as e:
            # TODO debug
            # raise e
            return Response(str(e),
                status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        try:
            instance = model_access.get_data_resource(request.user.username,
                key)
            if not instance:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = serializers.DataResourceSerializer(instance,
                data=request.data, context={'request': request, 'key': key},
                partial=True)
            if not serializer.is_valid():
                logger.error('%s' % serializer.errors)
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)
            resp = serializer.data
            resp = hal.add_hal_structure(resp, request,
                hal.generate_content_type(
                    request.accepted_media_type))
            return Response(resp, status=status.HTTP_200_OK)
        except Exception as e:
            # TODO debug
            raise e
            return Response(str(e),
                status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        try:
            instance = model_access.get_data_resource(request.user.username,
                key)
            if instance:
                instance.delete()
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            # TODO debug
            raise e
            return Response(str(e),
                status=status.HTTP_400_BAD_REQUEST)
