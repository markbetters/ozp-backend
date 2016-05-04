import re
import inspect
import json
import os

from plugins_util.plugin_manager import plugin_manager_instance


TEST_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Route(object):

    def __init__(self, url, view, method):
        self.url = url
        self.view = view
        self.method = method


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


class Router(object):

    def __init__(self, urls=None):
        if urls:
            self.urls = urls
        else:
            self.urls = []

    def add_urls(self, url_list):
        for url in url_list:
            self.urls.append(url)

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

            return MockResponse({'message':'Mock Service - URL Not found', "URL": url}, 404)
        except RuntimeError as e:
            return MockResponse({'message':'Mock Service - %s' % str(e), "URL": url}, 404)

router = Router()
plugin_manager_instance.load_mock_services(router)


def mocked_requests_get(*args, **kwargs):
    url = args[0]
    return router.execute(url)
