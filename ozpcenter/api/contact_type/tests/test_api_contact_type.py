"""
Tests for ContactType endpoints
"""
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from ozpcenter import model_access as generic_model_access
from ozpcenter.scripts import sample_data_generator as data_gen


@override_settings(ES_ENABLED=False)
class ContactTypeApiTest(APITestCase):

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

    def test_get_contact_type_list(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/contact_type/'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [i['name'] for i in response.data]
        self.assertTrue('Civilian' in names)
        self.assertTrue('Government' in names)
        self.assertTrue(len(names) > 2)

    def test_get_contact_type(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/contact_type/1/'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        name = response.data['name']
        self.assertEqual(name, 'Civilian')

    def test_create_contact_type(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        url = '/api/contact_type/'
        data = {'name': 'New Contact Type'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        name = response.data['name']
        self.assertEqual(name, 'New Contact Type')

    # TODO def test_create_contact_type(self): test different user groups access control

    def test_update_contact_type(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        url = '/api/contact_type/1/'
        data = {'name': 'Updated Type', 'required': True}
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        name = response.data['name']
        required = response.data['required']
        self.assertEqual(name, 'Updated Type')
        self.assertEqual(required, True)

    # TODO def test_update_contact_type(self): test different user groups access control

    def test_delete_contact_type(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        url = '/api/contact_type/1/'
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # TODO def test_delete_contact_type(self): test different user groups access control
