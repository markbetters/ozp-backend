"""
Views
"""
import datetime
import logging

from rest_framework import viewsets

import ozpcenter.api.notification.serializers as serializers
import ozpcenter.permissions as permissions
import ozpcenter.models as models
import ozpcenter.api.notification.model_access as model_access

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
            expires_date__gt=datetime.datetime.now())

class UserNotificationViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.NotificationSerializer

    def get_queryset(self):
        """
        Get current user's notifications
        """
        return model_access.get_self_notifications(self.request.user.username)
