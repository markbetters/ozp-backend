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
import ozpcenter.api.listing.model_access as listing_model_access
import ozpcenter.api.listing.serializers as listing_serializers
import ozpiwc.hal as hal
import ozpiwc.renderers as renderers

# Get an instance of a logger
logger = logging.getLogger('ozp-iwc.'+str(__name__))

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
@renderer_classes((renderers.ApplicationListResourceRenderer, rf_renderers.JSONRenderer))
def ApplicationListView(request):
    """
    List of applications
    """
    if not hal.validate_version(request.META.get('HTTP_ACCEPT')):
        return Response('Invalid version requested',
            status=status.HTTP_406_NOT_ACCEPTABLE)

    listing_root_url = hal.get_abs_url_for_iwc(request)
    profile = model_access.get_profile(request.user.username)
    data = hal.create_base_structure(request, hal.generate_content_type(
        request.accepted_media_type))
    applications = listing_model_access.get_listings(profile.user.username)
    items = []
    embedded_items = []
    for i in applications:
        item = {"href": '%slisting/%s/' % (listing_root_url, i.id),
            "type": hal.generate_content_type(renderers.ApplicationResourceRenderer.media_type)}
        items.append(item)

        embedded = {'_links': {'self': item}}
        embedded['id'] = i.id
        embedded['title'] = i.title
        embedded['unique_name'] = i.unique_name

        intents = []
        for j in i.intents.all():
            intent = {'action': j.action, 'media_type': j.media_type,
            'label': j.label, 'icon_id': j.icon.id}
            intents.append(intent)

        embedded['intents'] = intents
        embedded_items.append(embedded)

    data['_links']['item'] = items
    data['_embedded']['item'] = embedded_items

    return Response(data)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
@renderer_classes((renderers.ApplicationResourceRenderer, rf_renderers.JSONRenderer))
def ApplicationView(request, id='0'):
    """
    Single application
    """
    if not hal.validate_version(request.META.get('HTTP_ACCEPT')):
        return Response('Invalid version requested',
            status=status.HTTP_406_NOT_ACCEPTABLE)

    listing_root_url = hal.get_abs_url_for_iwc(request)
    profile = model_access.get_profile(request.user.username)

    # TODO: only include the fields that are necessary for IWC. This will also
    # allow us to sever ties with ozpcenter.api.listing.serializers

    # This minimal definition of what a Listing object must have should be
    # advertised so that others can use IWC with their own systems
    queryset = listing_model_access.get_listing_by_id(profile.user.username, id)
    if not queryset:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = listing_serializers.ListingSerializer(queryset,
            context={'request': request})
    data = serializer.data
    data = hal.add_hal_structure(data, request, hal.generate_content_type(
        request.accepted_media_type))

    return Response(data)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
@renderer_classes((renderers.SystemResourceRenderer, rf_renderers.JSONRenderer))
def SystemView(request):
    """
    System view - TODO
    """
    if not hal.validate_version(request.META.get('HTTP_ACCEPT')):
        return Response('Invalid version requested',
            status=status.HTTP_406_NOT_ACCEPTABLE)

    listing_root_url = hal.get_abs_url_for_iwc(request)
    profile = model_access.get_profile(request.user.username)

    data = hal.create_base_structure(request, hal.generate_content_type(
        request.accepted_media_type))
    data["version"] = "1.0"
    data["name"] = "TBD"
    return Response(data)
