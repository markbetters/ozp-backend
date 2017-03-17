"""
Notification Views
"""
import logging

from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_framework import generics
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from ozpcenter import errors
from ozpcenter import permissions
import ozpcenter.api.notification.model_access as model_access
import ozpcenter.api.notification.serializers as serializers

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for getting all Notification entries for all users

    URIs
    ======

    GET /api/notification/
        Summary:
            Get a list of all system-wide Notification entries
        Response:
            200 - Successful operation - [NotificationSerializer]

    POST /api/notification/
        Summary:
            Add a Notification
        Request:
            data: NotificationSerializer Schema
        Response:
            200 - Successful operation - NotificationSerializer

    PUT /api/notification/{pk}
        Summary:
            Update an Notification Entry by ID

    DELETE /api/notification/{pk}
    Summary:
        Delete a Notification Entry by ID
    """

    serializer_class = serializers.NotificationSerializer
    permission_classes = (permissions.IsUser,)

    def get_queryset(self):
        queryset = model_access.get_all_notifications()

        listing_id = self.request.query_params.get('listing', None)
        if listing_id is not None:
            queryset = queryset.filter(listing__id=listing_id)

        return queryset

    def create(self, request):
        serializer = serializers.NotificationSerializer(data=request.data,
            context={'request': request}, partial=True)

        if not serializer.is_valid():
            logger.error('{0!s}'.format(serializer.errors))
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """
        Update is used only change the expiration date of the message
        """
        instance = self.get_queryset().get(pk=pk)
        serializer = serializers.NotificationSerializer(instance,
            data=request.data, context={'request': request}, partial=True)

        if not serializer.is_valid():
            logger.error('{0!s}'.format(serializer.errors))
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        current_request_profile = model_access.get_self(request.user.username)

        if not current_request_profile.is_steward():
            raise errors.PermissionDenied('Only Stewards can delete notifications')

        queryset = self.get_queryset()
        notification_instance = get_object_or_404(queryset, pk=pk)
        notification_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserNotificationViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for getting all UserNotification entries for all users

    URIs
    ======

    GET /api/notification/
        Summary:
            Get a list of all user Notification entries
        Response:
            200 - Successful operation - [NotificationSerializer]

    DELETE /api/notification/{pk}
    Summary:
        Delete a user Notification Entry by ID
    """

    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.NotificationSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('created_date',)
    ordering = ('-created_date',)

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
        model_access.dismiss_notification(notification, self.request.user.username)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PendingNotificationView(generics.ListCreateAPIView):
    """
    APIView for getting all PendingNotification entries for all users

    URIs
    ======

    GET /api/notification/
        Summary:
            Get a list of all Pending Notification entries
        Response:
            200 - Successful operation - [NotificationSerializer]

    DELETE /api/notification/{pk}
    Summary:
        Delete a Pending Notification Entry by ID
    """

    permission_classes = (permissions.IsOrgSteward,)
    serializer_class = serializers.NotificationSerializer

    def get_queryset(self):
        queryset = model_access.get_all_pending_notifications()

        listing_id = self.request.query_params.get('listing', None)
        if listing_id is not None:
            queryset = queryset.filter(listing__id=listing_id)

        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.NotificationSerializer(page,
                context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.NotificationSerializer(queryset,
            context={'request': request}, many=True)
        return Response(serializer.data)


class ExpiredNotificationView(generics.ListCreateAPIView):
    """
    APIView for getting all PendingNotification entries for all users

    URIs
    ======

    GET /api/notification/
        Summary:
            Get a list of all Expired Notification entries
        Response:
            200 - Successful operation - [NotificationSerializer]
    """

    permission_classes = (permissions.IsOrgSteward,)
    serializer_class = serializers.NotificationSerializer

    def get_queryset(self):
        queryset = model_access.get_all_expired_notifications()

        listing_id = self.request.query_params.get('listing', None)
        if listing_id is not None:
            queryset = queryset.filter(listing__id=listing_id)

        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.NotificationSerializer(page,
                context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.NotificationSerializer(queryset,
            context={'request': request}, many=True)
        return Response(serializer.data)
