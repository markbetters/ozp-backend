"""
URLs for all resources - will be placed under /iwc-api route by the project
level urls.py
"""
from django.conf.urls import url, include

import ozpiwc.views as views

# Wire up our API using automatic URL routing.
urlpatterns = [
    # url(r'', include('ozpiwc.api.data.urls')),
    # url(r'', include('ozpiwc.api.intent.urls')),
    # url(r'', include('ozpiwc.api.system.urls')),
    # url(r'', include('ozpiwc.api.names.urls')),
    url(r'', views.RootApiView)
]