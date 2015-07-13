"""
Urls
"""
from django.conf.urls import url, include
from rest_framework import routers

import ozpcenter.api.profile.views as views

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

router.register(r'profile', views.ProfileViewSet)
router.register(r'user', views.UserViewSet)
router.register(r'group', views.GroupViewSet)

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^self/profile/$', views.CurrentUserView)
]