"""
Permissions

Rest Conversion
-----------------
VIEW = GET
CREATE = POST
UPDATE = PUT/PATCH
DELETE = DELETE

View and Permissions
-----------------
AgencyViewSet - IsAppsMallStewardOrReadOnly
CategoryViewSet - IsAppsMallStewardOrReadOnly
ContactTypeViewSet - IsAppsMallStewardOrReadOnly
ImageTypeViewSet - IsAppsMallStewardOrReadOnly
ImageViewSet - IsUser  # AccessControl
IntentViewSet - IsAppsMallStewardOrReadOnly
LibraryViewSet - IsOrgSteward
UserLibraryViewSet - IsUser
ContactViewSet - IsUser - Correct Permissions?
DocUrlViewSet - - IsUser - Correct Permissions?
ReviewViewSet - IsUser - Results Filtered for user
ListingTypeViewSet - IsUser -  Correct Permissions?
ListingUserActivitiesViewSet - IsUser - Results Filtered for user
ListingActivitiesViewSet - IsOrgSteward - Results Filtered for user
ListingActivityViewSet - IsUser - Results Filtered for user
ListingRejectionViewSet - IsOrgStewardOrReadOnly - Results Filtered for user
ScreenshotViewSet - IsUser - Correct Permissions?
TagViewSet - IsUser - Correct Permissions?
ListingViewSet - IsUser - Results Filtered for user
ListingUserViewSet - IsUser - Results Filtered for user
NotificationViewSet - IsUser
UserNotificationViewSet - IsUser - Results Filtered for user
PendingNotificationView - IsOrgSteward
ExpiredNotificationView - IsOrgSteward
ProfileViewSet - IsOrgStewardOrReadOnly
ProfileListingViewSet - IsUser - Results Filtered for user
UserViewSet - IsOrgSteward
GroupViewSet - IsUser - Correct Permissions?
CurrentUserViewSet - IsUser -  Results Filtered for user
MetadataView - IsUser - Results Filtered for user
StorefrontView - IsUser - Results Filtered for user
"""


class ViewToEntityConverter(object):

    @staticmethod
    def get_entity_from_instance(viewset):
        return ViewToEntityConverter.get_entity(viewset.__class__.__name__)

    @staticmethod
    def get_entity(viewset_name):
        data = {
            'AgencyViewSet': 'agency'
        }
        return data.get(viewset_name)


class AppsMallStewardRole(object):
    permissions = [
        'view|create|update|delete.agency',
        'view|create|update|delete.category',
        'view|create|update|delete.contact_type',
        'view|create|update|delete.image',  # Image has additional access control for retrieve
        'view|create|update|delete.intent',
        'view|create|update|delete.listing',
        'view|create|update|delete.profile',

        'view|create|update|delete.notification'
        # Notification Object-Level
        'view|create|update|delete.notification.system',  # AppsMallStewards can view/create/update/delete System-wide Notifications
        'view|create|update|delete.notification.peer',
        'view|create|update|delete.notification.agency',
        'view|create|update|delete.notification.listing',
        'view|create|update|delete.notification.category',
    ]


class OrgStewardRole(object):
    permissions = [
        'view.agency',
        'view.category',
        'view.contact_type',
        'view.image',  # Image has additional access control for retrieve
        'view.intent'

        'view|create|update|delete.listing',
        'view|create|update|delete.profile',

        'view|create|update|delete.notification'
        # Notification Object-Level
        'view.notification.system',  # Org Stewards can only view System-wide Notifications
        'view|create|update|delete.notification.peer',
        'view|create|update|delete.notification.agency',
        'view|create|update|delete.notification.listing',
        'view|create|update|delete.notification.category',

    ]


class UserRole(object):
    permissions = [
        'view_agency',
        'view_category',
        'view_contact_type',
        'view_image',
        'view_intent',
        'view_listing',
        'view_profile'
    ]
