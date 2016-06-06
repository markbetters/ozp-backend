"""
Tests for agency endpoints
"""
from rest_framework import status
from rest_framework.test import APITestCase

from ozpcenter.scripts import sample_data_generator as data_gen
import ozpcenter.model_access as generic_model_access


class RootViewApiTest(APITestCase):

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

    def test_hal_struct(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/iwc-api/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('_links' in response.data)
        self.assertTrue('_embedded' in response.data)

        self.assertTrue('ozp:application' in response.data['_links'])
        self.assertTrue('/self/application/' in response.data['_links']['ozp:application']['href'])

        self.assertTrue('ozp:system' in response.data['_links'])
        self.assertTrue('ozp:user' in response.data['_links'])
        self.assertTrue('ozp:intent' in response.data['_links'])
        self.assertTrue('ozp:user-data' in response.data['_links'])
