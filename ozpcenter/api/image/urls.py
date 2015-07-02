"""
Urls
"""
from django.conf.urls import url, include
from rest_framework import routers

import ozpcenter.api.image.views as views

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

router.register(r'icon', views.IconViewSet)

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
]