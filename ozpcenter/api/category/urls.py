"""
Urls
"""
from django.conf.urls import url, include
from rest_framework import routers

import ozpcenter.api.category.views as views

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

router.register(r'category', views.CategoryViewSet)

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
]