"""
Library views

GET /self/library
return the id and unique name of each listing in the user's library

"""
import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

import ozpcenter.api.library.serializers as serializers
import ozpcenter.models as models
import ozpcenter.permissions as permissions

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class LibraryViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for getting all library entries for all users

    Must be an Org Steward to access this endpoint

    GET api/library - return a list of all user's libraries
    POST, PUT, PATCH, DELETE api/library/<id> - unallowed (for now)
    """
    permission_classes = (permissions.IsOrgSteward,)
    queryset = models.ApplicationLibraryEntry.objects.all()
    serializer_class = serializers.LibrarySerializer

class UserLibraryViewSet(viewsets.ViewSet):
    """
    ViewSet for api/self/library

    GET api/self/library - return a list of this user's library (full listing info)
    POST api/self/library - add a listing to user's library
        data = {'listing_id': id}
    DELETE api/self/library/<id> - remove an entry from user's library
    PUT, PATCH api/library/<id> - unallowed (library entries can only be created
        or deleted, not updated)
    """
    permission_classes = (permissions.IsUser,)

    def get_queryset(self):
        return  models.ApplicationLibraryEntry.objects.filter(
            owner__user__username=self.request.user.username)

    def create(self, request):
        """
        ---
        parameters:
            - name: listing_id
              description: listing id
              required: true
            - name: folder
              description: folder
              type: string
        parameters_strategy:
            form: replace
            query: replace
        omit_serializer: true
        """
        data = {
            'listing': {
                'id': request.data['listing_id']
            },
            'folder': request.data.get('folder', '')
        }

        serializer = serializers.UserLibrarySerializer(data=data,
            context={'request': request})
        if not serializer.is_valid():
            logger.error('%s' % serializer.errors)
            return Response(serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        """
        ---
        serializer: ozpcenter.api.library.serializers.UserLibrarySerializer
        """
        queryset = self.get_queryset()
        serializer = serializers.UserLibrarySerializer(queryset,
            many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        library_entry = get_object_or_404(queryset, pk=pk)
        serializer = serializers.UserLibrarySerializer(library_entry,
            context={'request': request})
        return Response(serializer.data)

    # def update(self, request, pk=None):
    #     pass

    # def partial_update(self, request, pk=None):
    #     pass

    def destroy(self, request, pk=None):
        queryset = self.get_queryset()
        library_entry = get_object_or_404(queryset, pk=pk)
        library_entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)