"""
Utils
"""
import json
from pprint import pprint

from django.conf import settings

def _load_json_file():
    with open(settings.OZP['DEMO_AUTH_SERVICE']['JSON_FILE']) as json_data:
        auth_data = json.load(json_data)
        return auth_data

def get_auth_data(dn):
    """
    Get updated authorization data from a JSON file
    """
    auth_data = _load_json_file()
        # pprint(auth_data)
    user_auth_data = auth_data['users']
    for u in user_auth_data:
        if u['dn'] == dn:
            return u
    return None

def is_user_in_group(dn, group):
    auth_data = _load_json_file()
    for g in auth_data['groups']:
        if g['name'] == group:
            for i in g['members']:
                if i == dn:
                    return True
    return False
