"""
Tests for intent endpoints
"""
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from ozpcenter import model_access as generic_model_access
from ozpcenter.scripts import sample_data_generator as data_gen


@override_settings(ES_ENABLED=False)
class IntentApiTest(APITestCase):

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

    def test_get_intent_list(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/intent/'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        actions = [i['action'] for i in response.data]
        self.assertTrue('/application/json/view' in actions)
        self.assertTrue(response.data[0]['icon'] is not None)
        self.assertTrue(response.data[0]['media_type'] is not None)
        self.assertTrue(response.data[0]['label'] is not None)

    def test_get_intent(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/intent/1/'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        action = response.data['action']
        self.assertEqual(action, '/application/json/view')

    def test_create_intent(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        url = '/api/intent/'
        data = {'action': '/application/test',
            'media_type': 'vnd.ozp-intent-v1+json.json', 'label': 'test',
                'icon': {'id': 1, 'security_marking': 'UNCLASSIFIED'}}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        action = response.data['action']  # flake8: noqa TODO: Is Necessary? - Variable not being used in method

    def test_update_intent(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        url = '/api/intent/1/'
        data = {'action': '/application/json/viewtest',
            'media_type': 'vnd.ozp-intent-v2+json.json', 'label': 'mylabel',
            'icon': {'id': 1, 'security_marking': 'UNCLASSIFIED'}}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        action = response.data['action']
        label = response.data['label']
        media_type = response.data['media_type']
        self.assertEqual(action, '/application/json/viewtest')
        self.assertEqual(label, 'mylabel')
        self.assertEqual(media_type, 'vnd.ozp-intent-v2+json.json')

    def test_delete_intent(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        url = '/api/intent/1/'
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
