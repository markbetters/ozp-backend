"""
Urls
"""
from django.conf.urls import url, include
# use drf-nested-routers extension
from rest_framework_nested import routers

import ozpcenter.api.listing.views as views

# Routers provide an easy way of automatically determining the URL conf.
router = routers.SimpleRouter()
router.register(r'listing', views.ListingViewSet, base_name="listing")
router.register(r'listing/search', views.ListingSearchViewSet,
    base_name='listingsearch')
router.register(r'self/listing', views.ListingUserViewSet,
    base_name='selflisting')
router.register(r'listingtype', views.ListingTypeViewSet)

# nested routes
comment_router = routers.NestedSimpleRouter(router, r'listing',
    lookup='listing')
comment_router.register(r'itemComment', views.ItemCommentViewSet,
    base_name='itemcomment')
# TODO: nest these
router.register(r'screenshot', views.ScreenshotViewSet)
router.register(r'tag', views.TagViewSet)
router.register(r'contact', views.ContactViewSet)

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(comment_router.urls)),
]