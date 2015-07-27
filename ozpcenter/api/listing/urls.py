"""
Urls
"""
from django.conf.urls import url, include
from rest_framework import routers

import ozpcenter.api.listing.views as views

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

router.register(r'listing/search', views.ListingSearchViewSet, base_name='listing')
router.register(r'screenshot', views.ScreenshotViewSet)
router.register(r'tag', views.TagViewSet)
router.register(r'listingtype', views.ListingTypeViewSet)
router.register(r'contact', views.ContactViewSet)

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),

]