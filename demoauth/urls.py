"""
URLs
"""
from django.conf.urls import url, include

import demoauth.views as views

urlpatterns = [
    # in real service, url is <root_url>/users/<DN>.json
    url(r'^users/dn/(?P<dn>[0-9a-zA-Z,. ]+)/$', views.UserDnView),
    # in real service, url is <root_url>/users/<DN>/groups/<PROJECT>.json
    url(r'^users/dn/(?P<dn>[0-9a-zA-Z,. ]+)/groups/(?P<project>[a-zA-Z0-9_]+)/$', views.UserGroupsView),
]