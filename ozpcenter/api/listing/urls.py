"""
Listing URLs

Unlike most (maybe all) of the other resources, the Listing resource has several
nested resources - reviews and activity, for example. To help generate
nested URLs for these resources, the drf-nested-routers package is used.
"""
from django.conf.urls import url, include
# use drf-nested-routers extension
from rest_framework_nested import routers

import ozpcenter.api.listing.views as views

# Create a 'root level' router and urls
router = routers.SimpleRouter()
router.register(r'listing', views.ListingViewSet, base_name="listing")
# Ideally this route would be listing/search, but that conflicts with the
# nested router
router.register(r'listings/search', views.ListingSearchViewSet,
    base_name='listingssearch')
# Ideally this route would be listing/activity, but that conflicts with the
# nested router
router.register(r'listings/activity', views.ListingActivitiesViewSet,
    base_name='listingsactivity')
router.register(r'self/listing', views.ListingUserViewSet,
    base_name='selflisting')
router.register(r'self/listings/activity', views.ListingUserActivitiesViewSet,
    base_name='selflistingsactivity')
router.register(r'listingtype', views.ListingTypeViewSet)

# nested routes
nested_router = routers.NestedSimpleRouter(router, r'listing',
    lookup='listing')
nested_router.register(r'review', views.ReviewViewSet,
    base_name='review')
nested_router.register(r'activity', views.ListingActivityViewSet,
    base_name='activity')
nested_router.register(r'rejection', views.ListingRejectionViewSet,
    base_name='rejection')
# TODO: nest these
router.register(r'screenshot', views.ScreenshotViewSet)
router.register(r'tag', views.TagViewSet)
router.register(r'contact', views.ContactViewSet)

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(nested_router.urls)),
]
