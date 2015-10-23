"""
Renderers
"""
from rest_framework import renderers

class RootResourceRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.ozp-iwc;version=2'

class UserResourceRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.ozp-iwc-user+json;version=2'

class SystemResourceRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.ozp-iwc-system+json;version=2'

class DataObjectResourceRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.ozp-iwc-data-object+json;version=2'

class DataObjectListResourceRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.ozp-iwc-data-objects+json;version=2'

class ApplicationResourceRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.ozp-iwc-application+json;version=2'

class ApplicationListResourceRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.ozp-iwc-applications+json;version=2'

class IntentResourceRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.ozp-iwc-intent+json;version=2'

class IntentListResourceRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.ozp-iwc-intents+json;version=2'