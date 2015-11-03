"""
URLs
"""
from django.conf.urls import url, include

import demoauth.views as views

urlpatterns = [
    url(r'^dn/(?P<dn>[0-9a-zA-Z,. ]+)/$', views.UserDnView),
    url(r'^groups/(?P<project>[0-9a-zA-Z\-_ ]+)!(?P<group>[0-9a-zA-Z\-_ ]+)/members/(?P<dn>[0-9a-zA-Z,. ]+)/$', views.UserInGroupView),
]