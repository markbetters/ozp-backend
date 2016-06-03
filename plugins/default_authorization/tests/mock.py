import inspect
import json
import os
import re

from ozp.tests.helper import MockResponse
from ozp.tests.helper import Route

TEST_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_json_file():
    with open('{0!s}/{1!s}'.format(TEST_BASE_DIR, 'tests/auth_data.json')) as json_data:
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


class DemoAuthView(object):

    def user_info(self, dn):
        user_data = get_auth_data(dn)
        if not user_data:
            return MockResponse('User not found', 404)

        # remove groups, since this doesn't come back in this HTTP endpoint in the
        # actual authorization service
        user_data.pop('groups', None)
        return MockResponse(user_data, 200)

    def user_groups(self, dn, project):
        user_data = {"groups": get_auth_data(dn)['groups']}
        if not user_data:
            return MockResponse('User not found', 404)
        return MockResponse(user_data, 200)

urls = [
    Route(r'^/demo-auth/users/(?P<dn>[0-9a-zA-Z_=,\.@ ]+)/info.json[\d\D\W\w]*$', DemoAuthView, 'user_info'),
    Route(r'^/demo-auth/users/(?P<dn>[0-9a-zA-Z_,=\.@ %]+)/groups/(?P<project>[a-zA-Z0-9_]+)/$', DemoAuthView, 'user_groups')
]
