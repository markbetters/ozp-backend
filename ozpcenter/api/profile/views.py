"""
Profile Views
TODO: GET api/profile?role=ORG_STEWARD for view (shown on create/edit listing page)
TODO: POST api/profile/self/library - add listing to library (bookmark)
    params: listing id
TODO: DELETE api/profile/self/library/<id> - unbookmark a listing
"""


import logging

from rest_framework import filters
from rest_framework import viewsets
# from rest_framework.decorators import permission_classes
from rest_framework import status
from rest_framework.response import Response

from plugins_util.plugin_manager import system_anonymize_identifiable_data
from ozpcenter import errors
from ozpcenter import permissions
import ozpcenter.api.profile.serializers as serializers
import ozpcenter.api.listing.serializers as listing_serializers
# from ozpcenter import pagination
import ozpcenter.api.profile.model_access as model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class ProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsOrgStewardOrReadOnly,)
    serializer_class = serializers.ProfileSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('dn',)

    def get_queryset(self):
        role = self.request.query_params.get('role', None)
        if role:
            queryset = model_access.get_profiles_by_role(role)
        else:
            queryset = model_access.get_all_profiles()
        # support starts-with matching for finding users in the
        # Submit/Edit Listing form
        username_starts_with = self.request.query_params.get(
            'username_starts_with', None)
        if username_starts_with:
            queryset = model_access.filter_queryset_by_username_starts_with(
                queryset, username_starts_with)
        return queryset

    def update(self, request, pk=None):
        current_request_profile = model_access.get_self(request.user.username)
        if current_request_profile.highest_role() != 'APPS_MALL_STEWARD':
            raise errors.PermissionDenied
        profile_instance = self.get_queryset().get(pk=pk)
        serializer = serializers.ProfileSerializer(profile_instance,
            data=request.data, context={'request': request}, partial=True)
        if not serializer.is_valid():
            logger.error('{0!s}'.format(serializer.errors))
            return Response(serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileListingViewSet(viewsets.ModelViewSet):
    """
    Get all listings owned by a specific user
    """
    permission_classes = (permissions.IsUser,)
    serializer_class = listing_serializers.ListingSerializer

    def get_queryset(self, current_request_username, profile_pk=None, listing_pk=None):
        if listing_pk:
            queryset = model_access.get_all_listings_for_profile_by_id(current_request_username, profile_pk, listing_pk)
        else:
            queryset = model_access.get_all_listings_for_profile_by_id(current_request_username, profile_pk)
        return queryset

    def list(self, request, profile_pk=None):
        """
        Retrieves all listings for a specific profile that they own
        """

        current_request_username = request.user.username
        queryset = self.get_queryset(current_request_username, profile_pk)

        # Used to anonymize usernames
        anonymize_identifiable_data = system_anonymize_identifiable_data(current_request_username)

        if anonymize_identifiable_data:
            return Response([])

        if queryset:
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = listing_serializers.ListingSerializer(page,
                    context={'request': request}, many=True)
                response = self.get_paginated_response(serializer.data)
                return response

            serializer = listing_serializers.ListingSerializer(queryset,
                context={'request': request}, many=True)
            return Response(serializer.data)
        else:
            return Response({'detail': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk, profile_pk=None):
        """
        Retrieves a specific listing for a specific profile that they own
        """
        current_request_username = request.user.username
        queryset = self.get_queryset(current_request_username, profile_pk, pk)
        if queryset:
            serializer = listing_serializers.ListingSerializer(queryset,
                context={'request': request})
            return Response(serializer.data)
        else:
            return Response({'detail': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, profile_pk=None):
        """
        This method is not supported
        """
        return Response({'detail': 'HTTP Verb(POST) Not Supported'}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def update(self, request, pk=None, profile_pk=None):
        """
        This method is not supported
        """
        return Response({'detail': 'HTTP Verb(PUT) Not Supported'}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def partial_update(self, request, pk=None, profile_pk=None):
        """
        This method is not supported
        """
        return Response({'detail': 'HTTP Verb(PATCH) Not Supported'}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def destroy(self, request, pk=None, profile_pk=None):
        """
        This method is not supported
        """
        return Response({'detail': 'HTTP Verb(DELETE) Not Supported'}, status=status.HTTP_501_NOT_IMPLEMENTED)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsOrgSteward,)
    queryset = model_access.get_all_users()
    serializer_class = serializers.UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsUser,)
    queryset = model_access.get_all_groups()
    serializer_class = serializers.GroupSerializer


class CurrentUserViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """
    permission_classes = (permissions.IsUser,)

    def retrieve(self, request):
        current_request_profile = model_access.get_self(request.user.username)
        serializer = serializers.ProfileSerializer(current_request_profile,
            context={'request': request, 'self': True})
        return Response(serializer.data)

    def update(self, request):
        current_request_profile = model_access.get_self(request.user.username)
        serializer = serializers.ProfileSerializer(current_request_profile,
            data=request.data, context={'request': request}, partial=True)
        if not serializer.is_valid():
            logger.error('{0!s}'.format(serializer.errors))
            return Response(serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
