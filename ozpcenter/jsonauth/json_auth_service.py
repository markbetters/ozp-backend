"""
Test authorization service using a static JSON file

This service reads a JSON file as the source of authorization data. The user's
DN (models.Profile.dn) is the link between the profile in the database and the
entry in the JSON file
"""
import json
from pprint import pprint

from django.conf import settings

import ozpcenter.auth.base_authorization as base_authorization
import ozpcenter.model_access as model_access

class JsonAuthService(base_authorization.BaseAuthorization):
    def get_auth_data(self, username):
        """
        Get updated authorization data from a JSON file
        """
        # get auth data (read from json file)
        with open(settings.OZP['DUMMY_AUTH_SERVICE']['JSON_FILE']) as json_data:
            auth_data = json.load(json_data)
            # pprint(auth_data)

        # get dn for user
        profile = model_access.get_profile(username)
        user_auth_data = auth_data['users'][profile.dn]
        pprint(user_auth_data)
        return user_auth_data