"""
Urls

Unlike most (maybe all) of the other resources, the Listing resource has several
nested resources - item comments and activity, for example. To help generate
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
router.register(r'self/listing', views.ListingUserViewSet,
    base_name='selflisting')
router.register(r'listingtype', views.ListingTypeViewSet)

# nested routes
nested_router = routers.NestedSimpleRouter(router, r'listing',
    lookup='listing')
nested_router.register(r'itemComment', views.ItemCommentViewSet,
    base_name='itemcomment')
nested_router.register(r'activity', views.ListingActivityViewSet,
    base_name='activity')
# TODO: nest these
router.register(r'screenshot', views.ScreenshotViewSet)
router.register(r'tag', views.TagViewSet)
router.register(r'contact', views.ContactViewSet)

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(nested_router.urls)),
]