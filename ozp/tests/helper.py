import re
import inspect
import json
import os


TEST_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_json_file():
    with open('%s/%s'%(TEST_BASE_DIR,'tests/auth_data.json')) as json_data:
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


class MockResponse:
    """
    Mock Response for requests module
    """
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code
        self.text = 'Message: %s - Status: %s' % (self.json_data.get('message', 'N/A'),status_code)

    def json(self):
        return self.json_data


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


class Route(object):

    def __init__(self, url, view, method):
        self.url = url
        self.view = view
        self.method = method


class Router(object):

    def __init__(self, urls):
        self.urls = urls

    def execute(self, url):
        p = '(?P<protocol>http[s]?://)(?P<host>[^/ ]+)(?P<path>.*)'
        m = re.search(p,url)
        protocol = m.group('protocol')
        host = m.group('host')
        path = m.group('path')

        try:
            for route in self.urls:
                found = re.match(route.url, path)
                if found:
                    current_view = route.view()

                    if hasattr(current_view, route.method):
                        current_method = getattr(current_view, route.method)
                    else:
                        raise RuntimeError('Method [%s] does not exist on the view [%s]'%(route.method, current_view.__class__.__name__))

                    params = inspect.getargspec(current_method)

                    args = params.args[1::]

                    kargs = {}
                    for arg_key in args:
                        try:
                            kargs[arg_key] = found.group(arg_key)
                        except IndexError:
                            pass
                    return current_method(**kargs)

            return MockResponse({'message':'URL Not found', "URL": url}, 404)
        except RuntimeError as e:
            return MockResponse({'message':str(e), "URL": url}, 404)


urls = [
    Route(r'^/demo-auth/users/(?P<dn>[0-9a-zA-Z_=,\.@ ]+)/info.json[\d\D\W\w]*$', DemoAuthView, 'user_info'),
    Route(r'^/demo-auth/users/(?P<dn>[0-9a-zA-Z_,=\.@ %]+)/groups/(?P<project>[a-zA-Z0-9_]+)/$', DemoAuthView, 'user_groups')
]


router = Router(urls)


def mocked_requests_get(*args, **kwargs):
    url = args[0]
    return router.execute(url)
