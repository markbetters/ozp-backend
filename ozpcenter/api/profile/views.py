"""
Views

TODO: GET api/profile?role=ORG_STEWARD for view (shown on create/edit listing page)



TODO: POST api/profile/self/library - add listing to library (bookmark)
  params: listing id

TODO: DELETE api/profile/self/library/<id> - unbookmark a listing
"""
import logging

import django.contrib.auth
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework import generics, status
from rest_framework.response import Response

import ozpcenter.errors as errors
import ozpcenter.api.profile.serializers as serializers
import ozpcenter.models as models
import ozpcenter.permissions as permissions
import ozpcenter.api.profile.model_access as model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class ProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsOrgStewardOrReadOnly,)
    serializer_class = serializers.ProfileSerializer

    def get_queryset(self):
        queryset = models.Profile.objects.all()
        role = self.request.query_params.get('role', None)
        if role:
            queryset = models.Profile.objects.filter(
                user__groups__name__exact=role)
        # support starts-with matching for finding users in the
        # Submit/Edit Listing form
        username_starts_with = self.request.query_params.get(
            'username_starts_with', None)
        if username_starts_with:
            queryset = queryset.filter(
                user__username__startswith=username_starts_with)
        return queryset

    def update(self, request, pk=None):
        try:
            profile = model_access.get_self(request.user.username)
            if profile.highest_role() != 'APPS_MALL_STEWARD':
                raise errors.PermissionDenied
            instance = self.get_queryset().get(pk=pk)
            serializer = serializers.ProfileSerializer(instance,
                data=request.data, context={'request': request}, partial=True)
            if not serializer.is_valid():
                logger.error('%s' % serializer.errors)
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        except errors.PermissionDenied:
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            raise e

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsOrgSteward,)
    queryset = django.contrib.auth.models.User.objects.all()
    serializer_class = serializers.UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset = django.contrib.auth.models.Group.objects.all()
    serializer_class = serializers.GroupSerializer

@api_view(['GET'])
@permission_classes((permissions.IsUser, ))
def CurrentUserView(request):
    """
    ---
    serializer: ozpcenter.api.profile.serializers.ProfileSerializer
    """
    profile = model_access.get_self(request.user.username)
    serializer = serializers.ProfileSerializer(profile,
        context={'request': request})
    return Response(serializer.data)