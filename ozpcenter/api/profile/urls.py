"""
Profile URLs
"""
from django.conf.urls import url, include
# from rest_framework import routers
# use drf-nested-routers extension
from rest_framework_nested import routers

import ozpcenter.api.profile.views as views

# Routers provide an easy way of automatically determining the URL conf.
router = routers.SimpleRouter()

router.register(r'profile', views.ProfileViewSet, base_name='profile')
router.register(r'user', views.UserViewSet)
router.register(r'group', views.GroupViewSet)

profile_router = routers.NestedSimpleRouter(router, r'profile', lookup='profile')
profile_router.register(r'listing', views.ProfileListingViewSet, base_name='listing')


# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(profile_router.urls)),
    url(r'^self/profile/$', views.CurrentUserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'update'}))
]
