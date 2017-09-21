"""
Tests for agency endpoints
"""
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from ozpcenter import model_access as generic_model_access
from ozpcenter.scripts import sample_data_generator as data_gen


@override_settings(ES_ENABLED=False)
class AgencyApiTest(APITestCase):

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

    def test_get_agencies_list(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/agency/'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [i['title'] for i in response.data]
        self.assertTrue('Ministry of Truth' in titles)
        self.assertTrue(len(titles) > 3)

    def test_get_agency(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/agency/1/'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        title = response.data['title']
        short_name = response.data['short_name']
        self.assertEqual(title, 'Ministry of Truth')
        self.assertEqual(short_name, 'Minitrue')

    def test_create_agency(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        url = '/api/agency/'
        data = {'title': 'new agency', 'short_name': 'orgname'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        title = response.data['title']
        short_name = response.data['short_name']
        self.assertEqual(title, 'new agency')
        self.assertEqual(short_name, 'orgname')

    # TODO def test_create_agency(self): test different user groups access control

    def test_update_agency(self):
        """
        Update Agency /api/agency/1/
        """
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        url = '/api/agency/1/'
        data = {'title': 'updated agency', 'short_name': 'uporg'}
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        title = response.data['title']
        short_name = response.data['short_name']
        self.assertEqual(title, 'updated agency')
        self.assertEqual(short_name, 'uporg')

    # TODO def test_update_agency(self): test different user groups access control

    def test_delete_agency(self):
        """
        Delete /api/agency/1/
        """
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        url = '/api/agency/1/'
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # TODO def test_delete_agency(self): test different user groups access control
