"""
This is the plugin that accesses the Authorization Server

Authorization for OZP using the DemoAuth service

Checks models.Profile.auth_expires. If auth is expired, refresh it.

- models.Profile.user.groups (User, Org Steward, or Apps Mall Steward)
- models.Profile.stewarded_organizations (clear all if user is not an Org Steward)
- models.Profile.organizations
- models.Profile.access_control
- models.Profile.display_name (use CN)
"""
import logging

logger = logging.getLogger('ozp-center.' + str(__name__))


class PluginMain(object):
    plugin_name = 'plugin1'
    description = 'plugin 1'
    plugin_type = 'authorization'

    def __init__(self, settings=None, requests=None):
        '''
        Settings: Object reference to ozp settings
        '''
        self.settings = settings
        self.requests = requests

    def fakemethod1(self, input):
        return input
