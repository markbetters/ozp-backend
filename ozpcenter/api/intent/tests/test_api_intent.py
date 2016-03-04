"""
Tests for intent endpoints
"""
import unittest

from django.db import transaction
from django.db.utils import IntegrityError
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ozpcenter.scripts import sample_data_generator as data_gen
import ozpcenter.api.contact_type.views as views
from ozpcenter import models as models
from ozpcenter import model_access as generic_model_access


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
        self.assertTrue(response.data[0]['icon'] != None)
        self.assertTrue(response.data[0]['media_type'] != None)
        self.assertTrue(response.data[0]['label'] != None)

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
        action = response.data['action']

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
