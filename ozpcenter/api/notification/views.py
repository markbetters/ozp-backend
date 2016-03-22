"""
Views
"""
import datetime
import logging
import pytz

from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

import ozpcenter.errors as errors
import ozpcenter.api.notification.serializers as serializers
import ozpcenter.permissions as permissions
import ozpcenter.models as models
import ozpcenter.api.notification.model_access as model_access
import ozpcenter.model_access as generic_model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center')


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.NotificationSerializer
    permission_classes = (permissions.IsUser,)

    def get_queryset(self):
        return model_access.get_all_notifications()

    def create(self, request):
        try:
            serializer = serializers.NotificationSerializer(data=request.data,
                context={'request': request}, partial=True)
            if not serializer.is_valid():
                logger.error('%s' % serializer.errors)
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except errors.PermissionDenied:
            return Response({'detail':'Permission Denied'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error('Exception: {}'.format(e.message))
            raise e

    def update(self, request, pk=None):
        """
        update is used only change the expiration date of the message
        """
        try:
            instance = self.get_queryset().get(pk=pk)
            serializer = serializers.NotificationSerializer(instance,
                data=request.data, context={'request': request}, partial=True)

            if not serializer.is_valid():
                logger.error('%s' % serializer.errors)
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        except errors.PermissionDenied:
            return Response({'detail':'Permission Denied'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error('Exception: {}'.format(e.message))
            raise e

    def destroy(self, request, pk=None):
        try:
            current_request_profile = model_access.get_self(request.user.username)

            if current_request_profile.highest_role() not in ['APPS_MALL_STEWARD', 'ORG_STEWARD']:
                raise errors.PermissionDenied

            queryset = self.get_queryset()
            notification_instance = get_object_or_404(queryset, pk=pk)
            notification_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except errors.PermissionDenied:
                return Response({'detail':'Permission Denied'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error('Exception: {}'.format(e.message))
            raise e



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


class PendingNotificationView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsOrgSteward,)
    serializer_class = serializers.NotificationSerializer

    def get_queryset(self):
        return model_access.get_all_pending_notifications()

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
    permission_classes = (permissions.IsOrgSteward,)
    serializer_class = serializers.NotificationSerializer

    def get_queryset(self):
        return model_access.get_all_expired_notifications()

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
