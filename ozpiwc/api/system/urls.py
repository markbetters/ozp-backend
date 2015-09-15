from django.conf.urls import url, include

import ozpiwc.api.system.views as views

urlpatterns = [
    url(r'profile/(?P<profile_id>\d+)/application/$', views.ApplicationListView),
    url(r'listing/(?P<app_id>\d+)/$', views.ApplicationView),
    url(r'system/$', views.SystemView)
]