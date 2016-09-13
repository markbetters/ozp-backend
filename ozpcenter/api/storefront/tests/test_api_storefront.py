"""
Tests for storefront endpoints
"""
from rest_framework.test import APITestCase

from ozpcenter import model_access as generic_model_access
from ozpcenter.scripts import sample_data_generator as data_gen


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

    def test_metadata_authorized(self):
        url = '/api/metadata/'
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertIn('agencies', response.data)
        self.assertIn('categories', response.data)
        self.assertIn('contact_types', response.data)
        self.assertIn('listing_types', response.data)
        self.assertIn('intents', response.data)
        self.assertIn('listing_titles', response.data)

        for i in response.data['agencies']:
            self.assertTrue('listing_count' in i)

    def test_metadata_unauthorized(self):
        url = '/api/metadata/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 401)

    def test_storefront_authorized(self):
        url = '/api/storefront/'
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertIn('featured', response.data)
        self.assertIn('recent', response.data)
        self.assertIn('most_popular', response.data)

    def test_storefront_unauthorized(self):
        url = '/api/storefront/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 401)
