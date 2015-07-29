"""
Views
"""
import datetime
import logging
import pytz

from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

import ozpcenter.api.notification.serializers as serializers
import ozpcenter.permissions as permissions
import ozpcenter.models as models
import ozpcenter.api.notification.model_access as model_access
import ozpcenter.model_access as generic_model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class NotificationViewSet(viewsets.ModelViewSet):
    # queryset = models.Notification.objects.all()
    serializer_class = serializers.NotificationSerializer

    def get_queryset(self):
        """
        get all notifications that have not yet expired AND:
            * have not been dismissed by this user
            * are regarding a listing in this user's library (if the
                notification is listing-specific)
        """
        # TODO: add logic to ignore listing-specific notifications that are
        #   for listings not part of user's library
        return  models.Notification.objects.filter(
            expires_date__gt=datetime.datetime.now(pytz.utc))

class UserNotificationViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.NotificationSerializer

    def get_queryset(self):
        """
        Get current user's notifications
        """
        return model_access.get_self_notifications(self.request.user.username)

    def destroy(self, request, pk=None):
        """
        Dismiss notification
        """
        queryset = self.get_queryset()
        notification = get_object_or_404(queryset, pk=pk)
        user = generic_model_access.get_profile(self.request.user.username)
        notification.dismissed_by.add(user)
        return Response(status=status.HTTP_204_NO_CONTENT)
