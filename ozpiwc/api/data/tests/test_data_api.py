"""
Tests for data.api endpoints
"""
import json

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from ozpcenter import model_access as generic_model_access
from ozpcenter.scripts import sample_data_generator as data_gen


@override_settings(ES_ENABLED=False)
class DataApiTest(APITestCase):

    def setUp(self):
        """
        setUp is invoked before each test method
        """
        self

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the whole TestCase (only run once for the TestCase)
        """
        data_gen.run()

    def test_data_api(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        key = '/transportation/car'
        url = '/iwc-api/self/data' + key

        # Trying to get a non-existent key should produce a 404
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Create a new entry
        entity = {"details": {"color": "black", "year": 2000}}
        content_type = "vnd.acme-corp-car-v1+json.json"
        version = "1.0.2"
        pattern = "/something/else"
        permissions = {"id": 1, "name": "secure policy"}
        data = {
            "entity": entity,
            "content_type": content_type,
            "version": version,
            "pattern": pattern,
            "permissions": permissions
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'wsmith')
        self.assertEqual(response.data['key'], key)
        self.assertEqual(response.data['version'], version)
        self.assertEqual(response.data['pattern'], pattern)
        self.assertEqual(response.data['permissions'], str(permissions))

        entity_resp = json.loads(response.data['entity'])
        self.assertEqual(
            entity_resp['details']['color'], entity['details']['color'])

        # now retrieve that entry
        response = self.client.get(url, format='json')
        # and ensure the data is the same as that returned via the PUT request
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'wsmith')
        self.assertEqual(response.data['key'], key)
        self.assertEqual(response.data['version'], version)
        self.assertEqual(response.data['pattern'], pattern)
        self.assertEqual(response.data['permissions'], str(permissions))

        entity_resp = json.loads(response.data['entity'])
        self.assertEqual(
            entity_resp['details']['color'], entity['details']['color'])

        # test the list endpoint
        url = '/iwc-api/self/data/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(key in response.data['_links']['item'][0]['href'])

        # update an existing entry
        new_pattern = '/new/pattern'
        data['pattern'] = new_pattern
        url = '/iwc-api/self/data' + key
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.data['pattern'], new_pattern)

        # delete an entry
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # it should be gone now
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
