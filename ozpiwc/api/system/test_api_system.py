"""
Tests for agency endpoints
"""
import unittest

from django.db import transaction
from django.db.utils import IntegrityError
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

import ozpcenter.model_access as generic_model_access
from ozpcenter.scripts import sample_data_generator as data_gen


class SystemApiTest(APITestCase):

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

    def test_listings(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/iwc-api/profile/%s/application/' % user.id
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('_links' in response.data)
        self.assertTrue('_embedded' in response.data)
        self.assertTrue('item' in response.data)
        self.assertTrue(len(response.data['item']) > 3)

    def test_listing(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/iwc-api/listing/1/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('_links' in response.data)
        self.assertTrue('_embedded' in response.data)
        self.assertTrue('id' in response.data)
        self.assertTrue('title' in response.data)
        self.assertTrue('unique_name' in response.data)
        self.assertTrue('intents' in response.data)

    def test_system(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/iwc-api/system/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('_links' in response.data)
        self.assertTrue('_embedded' in response.data)
        self.assertTrue('version' in response.data)
        self.assertTrue('name' in response.data)
