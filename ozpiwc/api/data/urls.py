"""
urls
"""
from django.conf.urls import url, include

import ozpiwc.api.data.views as views

urlpatterns = [
    url(r'^self/data/$', views.DataApiView)
]