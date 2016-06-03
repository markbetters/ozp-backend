"""
Tests for storefront endpoints
"""
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate

from ozpcenter import model_access as generic_model_access
from ozpcenter import models
from ozpcenter.scripts import sample_data_generator as data_gen
import ozpcenter.api.storefront.views as views


class StorefrontApiTest(APITestCase):

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

    def test_metadata(self):
        url = '/api/metadata/'
        # test unauthorized user
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 401)

        # test authorized user
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertIn('agencies', response.data)
        self.assertIn('categories', response.data)
        self.assertIn('contact_types', response.data)
        self.assertIn('listing_types', response.data)
        self.assertIn('intents', response.data)
        for i in response.data['agencies']:
            self.assertTrue('listing_count' in i)

    def test_storefront(self):
        url = '/api/storefront/'
        # test unauthorized user
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 401)

        # test authorized user
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertIn('featured', response.data)
        self.assertIn('recent', response.data)
        self.assertIn('most_popular', response.data)
