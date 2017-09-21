"""
Image Views
"""
import logging

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response

from ozpcenter import permissions
from plugins_util.plugin_manager import system_has_access_control
import ozpcenter.api.image.model_access as model_access
import ozpcenter.api.image.serializers as serializers
from ozpcenter import errors
import ozpcenter.model_access as generic_model_access
from ozp.storage import media_storage

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class ImageTypeViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for getting all ImageType entries for all users

    Access Control
    ===============
    - All users can read
    - AppMallSteward can view

    URIs
    ======
    GET /api/imagetype
    Summary:
        Get a list of all system-wide ImageType

    Response:
        200 - Successful operation - [ImageTypeSerializer]

    POST /api/imagetype/
    Summary:
        Add an ImageType
    Request:
        data: ImageTypeSerializer Schema
    Response:
        200 - Successful operation - ImageTypeSerializer

    GET /api/imagetype/{pk}
    Summary:
        Find an ImageType Entry by ID
    Response:
        200 - Successful operation - ImageTypeSerializer

    PUT /api/imagetype/{pk}
    Summary:
        Update an ImageType Entry by ID

    PATCH /api/imagetype/{pk}
    Summary:
        Update (Partial) an ImageType Entry by ID

    DELETE /api/imagetype/{pk}
    Summary:
        Delete an ImageType Entry by ID
    """
    queryset = model_access.get_all_image_types()
    serializer_class = serializers.ImageTypeSerializer
    permission_classes = (permissions.IsAppsMallStewardOrReadOnly,)
    fields = ('name',)


class ImageViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for getting all Image entries for all users

    Access Control
    ===============
    - All users can read
    - AppMallSteward can view

    URIs
    ======
    GET,POST /api/image
    GET, DELETE /api/image/{pk}
    """

    def get_queryset(self):
        return model_access.get_all_images(self.request.user.username)

    serializer_class = serializers.ImageSerializer
    permission_classes = (permissions.IsUser,)
    parser_classes = (MultiPartParser, JSONParser)

    def create(self, request):
        """
        Upload an image

        Use content_type = `application/form-data`
        Data (key = value) example:
        ```
        security_marking = UNCLASSIFIED
        image_type = listing_small_screenshot
        file_extension = jpg
        image = <file>
        ```
        """
        # This is a long story. The short version is that, when using HTTP
        # Basic Auth, the client makes a request w/o auth credentials, and the
        # server returns a 401, instructing the client to make the request with
        # auth credentials. This usually works just fine under the covers, but
        # in this particular case (using multipart/form-data with a file
        # attachement), IE croaks. This dummy endpoint is used to 'prep' the
        # client so that when it makes the real request to this endpoint, it
        # already knows to set the necessary authentication header
        if 'cuz_ie' in request.data:
            return Response('IE made me do this', status=status.HTTP_200_OK)

        serializer = serializers.ImageCreateSerializer(data=request.data,
            context={'request': request})
        if not serializer.is_valid():
            logger.error('{0!s}'.format(serializer.errors))
            return Response(serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = serializers.ImageSerializer(queryset,
            many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Return an image, enforcing access control
        """
        queryset = self.get_queryset()
        image = get_object_or_404(queryset, pk=pk)
        image_path = str(image.id) + '_' + image.image_type.name + '.' + image.file_extension
        # enforce access control
        profile = generic_model_access.get_profile(self.request.user.username)

        if not system_has_access_control(profile.user.username, image.security_marking):
            raise errors.PermissionDenied()

        content_type = 'image/' + image.file_extension
        try:
            with media_storage.open(image_path) as f:
                return HttpResponse(f.read(), content_type=content_type)
        except IOError:
            logger.error('No image found for pk {}'.format(pk))
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        queryset = self.get_queryset()
        image = get_object_or_404(queryset, pk=pk)
        # TODO: remove image from file system
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
