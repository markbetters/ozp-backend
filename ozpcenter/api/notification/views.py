"""
Views
"""
import datetime
import logging

from rest_framework import viewsets

import ozpcenter.api.notification.serializers as serializers
import ozpcenter.permissions as permissions
import ozpcenter.models as models

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
        get all notifications that have not yet expired AND:
            * have not been dismissed by this user
            * are regarding a listing in this user's library (if the
                notification is listing-specific)
        """
        # get all notifications that have been dismissed by this user
        dismissed_notifications = models.Notification.objects.filter(
            dismissed_by__user__username=self.request.user.username)

        # get all unexpired notifications for listings in this user's library

        # get all unexpired system-wide notifications

        # return all_unexpired_notifications - dismissed_notifications

        return  models.Notification.objects.filter(
            expires_date__gt=datetime.datetime.now())