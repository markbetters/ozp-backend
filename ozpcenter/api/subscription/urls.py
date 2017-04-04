"""
Notifications URLs
"""
from django.conf.urls import url, include
from rest_framework import routers

import ozpcenter.api.subscription.views as views

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

router.register(r'subscription', views.SubscriptionViewSet,
    base_name='subscription')


router.register(r'self/subscription', views.UserSubscriptionViewSet,
    base_name='self_subscription')


# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
]
