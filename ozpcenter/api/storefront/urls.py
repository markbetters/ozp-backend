"""
urls
"""
from django.conf.urls import url, include

import ozpcenter.api.storefront.views as views

urlpatterns = [
    url(r'^storefront/$', views.StorefrontView),
    url(r'^metadata/$', views.MetadataView)
]
