from django.conf.urls import url

from ajax_sample.views import *

urlpatterns = [
    url(r'status/$', status_view),
    url(r'', base_view),
]
