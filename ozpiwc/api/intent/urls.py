from django.conf.urls import url, include

import ozpiwc.api.intent.views as views

urlpatterns = [
    url(r'^self/intent/$', views.IntentListView),
    url(r'^intent/(?P<id>\d+)/$', views.IntentView)
]
