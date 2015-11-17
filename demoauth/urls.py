"""
URLs
"""
from django.conf.urls import url, include

import demoauth.views as views

urlpatterns = [
    # in real service, url is <root_url>/users/<DN>.json
    url(r'^users/(?P<dn>[0-9a-zA-Z_=,\. ]+)/info.json/$', views.UserDnView),
    # in real service, url is <root_url>/users/<DN>/groups/<PROJECT>.json
    url(r'^users/(?P<dn>[0-9a-zA-Z_,=\. ]+)/groups/(?P<project>[a-zA-Z0-9_]+)/$', views.UserGroupsView),
]