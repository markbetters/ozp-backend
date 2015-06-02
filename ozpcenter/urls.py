"""
url routers
"""
from django.conf.urls import url, include
from rest_framework import routers

import ozpcenter.views as views

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

router.register(r'profile', views.ProfileViewSet)
router.register(r'category', views.CategoryViewSet)
router.register(r'contactType', views.ContactTypeViewSet)
router.register(r'contact', views.ContactViewSet)
router.register(r'agency', views.AgencyViewSet)

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^metadata/$', views.metadataView),
    url(r'^self/$', views.current_user)
]