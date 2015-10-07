"""
Urls
"""
from django.conf.urls import url, include
from rest_framework import routers

import ozpcenter.api.notification.views as views

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

router.register(r'notification', views.NotificationViewSet,
    base_name='notification')
router.register(r'self/notification', views.UserNotificationViewSet,
    base_name='notification')

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^notifications/pending/$', views.PendingNotificationView.as_view()),
    url(r'^notifications/expired/$', views.ExpiredNotificationView.as_view())
]