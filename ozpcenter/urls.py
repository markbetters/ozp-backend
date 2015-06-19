"""
url routers
"""
from django.conf.urls import url, include
from rest_framework import routers

import ozpcenter.views as views
import ozpcenter.auth_test_views as auth_test_views

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

router.register(r'profile', views.ProfileViewSet)
router.register(r'category', views.CategoryViewSet)
router.register(r'contactType', views.ContactTypeViewSet)
router.register(r'contact', views.ContactViewSet)
router.register(r'agency', views.AgencyViewSet)
router.register(r'intent', views.IntentViewSet)
router.register(r'docUrl', views.DocUrlViewSet)
router.register(r'listingActivity', views.ListingActivityViewSet)
router.register(r'rejectionListing', views.RejectionListingViewSet)
router.register(r'screenshot', views.ScreenshotViewSet)
router.register(r'self/library', views.ApplicationLibraryEntryViewSet,
	base_name='applicationlibraryentry')
router.register(r'itemComment', views.ItemCommentViewSet)
router.register(r'listing', views.ListingViewSet, base_name='listing')
router.register(r'type', views.ListingTypeViewSet)
router.register(r'accessControl', views.AccessControlViewSet)
router.register(r'tag', views.TagViewSet)
router.register(r'notification', views.NotificationViewSet)
router.register(r'self/notification', views.NotificationSelfViewSet,
	base_name='notification')
router.register(r'djangoUser', views.DjangoUserViewSet)


# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^self/$', views.current_user),
    url(r'^storefront/$', views.storefrontView),
    url(r'^metadata/$', views.metadataView),
    url(r'^authtest/$', auth_test_views.test)
]