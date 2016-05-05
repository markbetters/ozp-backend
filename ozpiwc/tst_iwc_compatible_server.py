"""
Run this test against a service to determine if the service is IWC compliant

Change IWC_ROOT to point to the API entry point before running this test
"""
import json
import requests
import unittest

IWC_ROOT = 'http://localhost:8000/iwc-api'

TOP_LEVEL_LINKS = ['ozp:user-data', 'ozp:application', 'ozp:user',
'ozp:system', 'ozp:intent']


class TestIwcBackend(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def make_get_request(self, url, expected_status=200):
        r = requests.get(url, auth=('wsmith', 'password'))
        self.assertEqual(r.status_code, expected_status)
        if expected_status == 200:
            return r.json()

    def make_put_request(self, url, data, expected_status=201):
        headers = {'content-type': 'application/vnd.ozp-iwc-data-object+json'}
        r = requests.put(url, data=json.dumps(data), auth=('wsmith', 'password'),
            headers=headers)
        self.assertEqual(r.status_code, expected_status)
        return r.json()

    def make_delete_request(self, url, ignore_status_code=False, expected_status=204):
        r = requests.delete(url, auth=('wsmith', 'password'))
        if not ignore_status_code:
            self.assertEqual(r.status_code, expected_status)

    def test_top_level(self):
        r = self.make_get_request(IWC_ROOT)
        # check for embedded system details
        self.assertTrue(r['_embedded']['ozp:system'])
        self.assertTrue(r['_embedded']['ozp:system']['version'])
        self.assertTrue(r['_embedded']['ozp:system']['name'])
        self.assertEqual(r['_embedded']['ozp:system']['_links']['self']['href'], '%s/system/' % IWC_ROOT)

        # check for embedded user details
        self.assertTrue(r['_embedded']['ozp:user'])
        self.assertTrue(r['_embedded']['ozp:user']['username'])
        self.assertTrue(r['_embedded']['ozp:user']['name'])
        self.assertTrue(r['_embedded']['ozp:user']['_links']['self'])

    def test_data_api(self):
        key = '/transportation/car7'
        url = '%s/self/data%s/' % (IWC_ROOT, key)
        # delete this entry, in case it already exists
        r = self.make_delete_request(url, True)

        # put some data
        data = {}
        data['entity'] = {
            "details": {
                "color": "red"
            }
        }
        data['version'] = '1.0'
        data['pattern'] = '/transportation/car'
        data['permissions'] = {'name': 'security'}

        r = self.make_put_request(url, data)

        # check response
        self.assertTrue(r['username'])
        self.assertEqual(r['key'], key)
        self.assertEqual(r['entity'], str(data['entity']))
        self.assertEqual(r['version'], data['version'])
        self.assertEqual(r['pattern'], data['pattern'])
        self.assertEqual(r['permissions'], str(data['permissions']))

        # now get the same data using the HAL self link and ensure it matches
        url = r['_links']['self']['href']
        r = self.make_get_request(url)
        self.assertTrue(r['username'])
        self.assertEqual(r['key'], key)
        self.assertEqual(r['entity'], str(data['entity']))
        self.assertEqual(r['version'], data['version'])
        self.assertEqual(r['pattern'], data['pattern'])
        self.assertEqual(r['permissions'], str(data['permissions']))

        # update the data
        data['version'] = '2.0'
        # (should get a 200 OK response instead of 201 CREATED)
        r = self.make_put_request(url, data, 200)
        self.assertEqual(r['version'], data['version'])

        # adding data with only a key and value (entity) should be fine
        data = {}
        data['entity'] = {
            "details": {
                "age": 11
            }
        }

        key = '/transportation/truck3'
        url = '%s/self/data%s/' % (IWC_ROOT, key)
        # delete this entry, in case it already exists
        r = self.make_delete_request(url, True)
        r = self.make_put_request(url, data, 201)
        self.assertEqual(r['key'], key)
        self.assertEqual(r['entity'], str(data['entity']))

        # root data endpoint should list all data entries
        r = self.make_get_request(IWC_ROOT)
        url = r['_links']['ozp:user-data']['href']
        r = self.make_get_request(url)
        self.assertTrue(len(r['_links']['item']) > 1)
        self.assertTrue(len(r['_links']['item'][0]['href']))

        # test deleting a key
        url = '%s/self/data%s/' % (IWC_ROOT, key)
        r = self.make_delete_request(url, 204)
        # should now get a 404 trying to get this key
        r = self.make_get_request(url, 404)

    def test_system_api(self):
        # test system api root
        r = self.make_get_request(IWC_ROOT)
        url = r['_links']['ozp:system']['href']
        r = self.make_get_request(url)
        self.assertTrue(r['version'])
        self.assertTrue(r['name'])
        self.assertEqual(r['_links']['self']['href'], url)

        # test the application root
        r = self.make_get_request(IWC_ROOT)
        url = r['_links']['ozp:application']['href']
        r = self.make_get_request(url)
        self.assertTrue(r['_links']['item'])
        self.assertEqual(r['_links']['self']['href'], url)

        # test the first application
        url = r['_links']['item'][0]['href']
        r = self.make_get_request(url)
        self.assertTrue(r['id'])
        self.assertTrue(r['unique_name'])
        self.assertEqual(r['_links']['self']['href'], url)

    def test_intent_api(self):
        # test intent api root
        r = self.make_get_request(IWC_ROOT)
        url = r['_links']['ozp:intent']['href']
        r = self.make_get_request(url)
        self.assertTrue(len(r['_links']['item']) > 1)
        self.assertEqual(r['_links']['self']['href'], url)

        # test the first intent
        url = r['_links']['item'][0]['href']
        r = self.make_get_request(url)
        self.assertTrue(r['id'])
        self.assertTrue(r['media_type'])
        self.assertTrue(r['action'])
        self.assertTrue(r['label'])
        self.assertTrue(r['icon'])
        self.assertEqual(r['_links']['self']['href'], url)

    def test_names_api(self):
        pass


if __name__ == "__main__":
    unittest.main()
