"""
URLs for all resources - will be placed under /api route by the project level
urls.py
"""
from django.conf.urls import url, include

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'', include('ozpcenter.api.agency.urls')),
    url(r'', include('ozpcenter.api.access_control.urls')),
    url(r'', include('ozpcenter.api.category.urls')),
    url(r'', include('ozpcenter.api.contact_type.urls')),
    url(r'', include('ozpcenter.api.image.urls')),
    url(r'', include('ozpcenter.api.intent.urls')),
    url(r'', include('ozpcenter.api.library.urls')),
    url(r'', include('ozpcenter.api.listing.urls')),
    url(r'', include('ozpcenter.api.notification.urls')),
    url(r'', include('ozpcenter.api.profile.urls')),
    url(r'', include('ozpcenter.api.storefront.urls'))
]