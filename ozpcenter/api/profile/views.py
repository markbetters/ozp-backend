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

import ozpcenter.api.profile.serializers as serializers
import ozpcenter.models as models
import ozpcenter.permissions as permissions
import ozpcenter.api.profile.model_access as model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class ProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsUser,)
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    filter_fields = ('highest_role',)

class DjangoUserViewSet(viewsets.ModelViewSet):
    queryset = django.contrib.auth.models.User.objects.all()
    serializer_class = serializers.DjangoUserSerializer

@api_view(['GET'])
@permission_classes((permissions.IsUser, ))
def current_user(request):
    data = model_access.get_profile(request.user.username)
    serializer = serializers.ProfileSerializer(data,
        context={'request': request})
    return Response(serializer.data)