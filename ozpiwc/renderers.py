"""
Renderers
"""
from rest_framework import renderers

class RootResourceRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.ozp-iwc+json'

class UserResourceRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.ozp-iwc-user+json'

class SystemResourceRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.ozp-iwc-system+json'

class DataObjectResourceRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.ozp-iwc-data-object+json'

class DataObjectListResourceRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.ozp-iwc-data-objects+json'

class ApplicationResourceRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.ozp-iwc-application+json'

class ApplicationListResourceRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.ozp-iwc-applications+json'

class IntentResourceRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.ozp-iwc-intent+json'

class IntentListResourceRenderer(renderers.JSONRenderer):
    media_type = 'application/vnd.ozp-iwc-intents+json'