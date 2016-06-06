from django.conf.urls import url

import ozpiwc.api.intent.views as views

urlpatterns = [
    url(r'^self/intent/$', views.IntentListView),
    url(r'^intent/(?P<id>\d+)/$', views.IntentView)
]
