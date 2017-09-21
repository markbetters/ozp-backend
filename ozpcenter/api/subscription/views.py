"""
Subscription Views
"""
import logging

from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from ozpcenter import errors
from ozpcenter import permissions
import ozpcenter.api.subscription.model_access as model_access
import ozpcenter.api.subscription.serializers as serializers

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for getting all Subscription entries for all users

    URIs
    ======
    GET /api/subscription/
        Summary:
            Get a list of all system-wide Subscription entries
        Response:
            200 - Successful operation - [SubscriptionSerializer]

    POST /api/subscription/
        Summary:
            Add a Subscription
        Request:
            data: SubscriptionSerializer Schema
        Response:
            200 - Successful operation - SubscriptionSerializer

    DELETE /api/subscription/{pk}
    Summary:
        Delete a Subscription Entry by ID
    """

    serializer_class = serializers.SubscriptionSerializer
    permission_classes = (permissions.IsUser,)

    def get_queryset(self):
        queryset = model_access.get_all_subscriptions()

        # listing_id = self.request.query_params.get('listing', None)
        # if listing_id is not None:
        #     queryset = queryset.filter(subscription_type='listing', entity_id=listing_id)
        # Maybe filter by entity_type

        return queryset

    def create(self, request):
        serializer = serializers.SubscriptionSerializer(data=request.data,
            context={'request': request}, partial=True)

        if not serializer.is_valid():
            logger.error('{0!s}'.format(serializer.errors))
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def update(self, request, pk=None):
    #     """
    #     Update is used only change the expiration date of the message
    #     """
    #     instance = self.get_queryset().get(pk=pk)
    #     serializer = serializers.SubscriptionSerializer(instance,
    #         data=request.data, context={'request': request}, partial=True)
    #
    #     if not serializer.is_valid():
    #         logger.error('{0!s}'.format(serializer.errors))
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     serializer.save()
    #
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        current_request_profile = model_access.get_self(request.user.username)

        if not current_request_profile.is_steward():
            raise errors.PermissionDenied('Only Stewards can delete subscriptions')

        queryset = self.get_queryset()
        subscription_instance = get_object_or_404(queryset, pk=pk)
        subscription_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for getting all UserSubscription entries for all users

    URIs
    ======

    GET /api/self/subscription/
        Summary:
            Get a list of all user Subscription entries
        Response:
            200 - Successful operation - [SubscriptionSerializer]

    DELETE /api/self/subscription/{pk}
    Summary:
        Delete a user Subscription Entry by ID
    """

    permission_classes = (permissions.IsUser,)
    serializer_class = serializers.SubscriptionSerializer
    filter_backends = (filters.OrderingFilter,)

    def get_queryset(self):
        """
        Get current user's subscriptions
        """
        return model_access.get_self_subscriptions(self.request.user.username)

    def destroy(self, request, pk=None):
        """
        Dismiss subscription
        """
        queryset = self.get_queryset()
        subscription = get_object_or_404(queryset, pk=pk)
        model_access.delete_self_subscription(subscription, self.request.user.username)
        return Response(status=status.HTTP_204_NO_CONTENT)
