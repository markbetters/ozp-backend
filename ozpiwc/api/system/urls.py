from django.conf.urls import url

import ozpiwc.api.system.views as views

urlpatterns = [
    url(r'^self/application/$', views.ApplicationListView),
    url(r'^listing/(?P<id>\d+)/$', views.ApplicationView),
    url(r'^system/$', views.SystemView)
]
