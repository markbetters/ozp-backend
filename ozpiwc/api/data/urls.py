"""
urls
"""
from django.conf.urls import url, include

import ozpiwc.api.data.views as views

urlpatterns = [
    url(r'^self/data/$', views.ListDataApiView),
    # this will capture things like food/pizza/cheese. In the view, the key
    # will be modified such that it always starts with a / and never ends
    # with one
    url(r'^self/data/(?P<key>[a-zA-Z0-9\-/]+)$', views.DataApiView)
]
