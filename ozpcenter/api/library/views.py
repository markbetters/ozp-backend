"""
Views
"""
import logging

from rest_framework import viewsets

import ozpcenter.api.library.serializers as serializers
import ozpcenter.models as models
import ozpcenter.permissions as permissions

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class LibraryViewSet(viewsets.ModelViewSet):
    queryset = models.ApplicationLibraryEntry.objects.all()
    serializer_class = serializers.LibrarySerializer

class UserLibraryViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsUser,)

    def get_queryset(self):
        return  models.ApplicationLibraryEntry.objects.filter(
            owner__username=self.request.user.username)

    def create(self, request):
        """
        Return:
        {
            "listing": {
                "title": x,
                "launch_url": x,
                "universal_name": x,
                "small_icon": x,
                "large_icon": x,
                "banner_icon": x,
                "large_banner_icon": x,
                "id": x,
            },
            "folder": null
        }
        ---
        parameters:
            - name: listing
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
        logger.info('creating library entry for user %s' % request.user)
        logger.info('got data: %s' % request.data)
        # data = {}
        # if not 'folder' in request.data:
        #     data['folder'] = ''
        # else:
        #     data['folder'] = request.data['folder']
        # data['listing'] = request.data['listing'][0]
        data = {
            'listing_id': '1',
            'folder': ''
        }


        serializer = serializers.LibraryEntrySerializer(data=data,
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
        serializer: ozpcenter.api.library.serializers.ApplicationLibraryEntrySerializer
        """
        queryset = self.get_queryset()
        serializer = serializers.ApplicationLibraryEntrySerializer(queryset,
            many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        pass

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass