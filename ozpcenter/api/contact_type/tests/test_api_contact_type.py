"""
Tests for ContactType endpoints
"""
import unittest

from django.db import transaction
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate

from ozpcenter import model_access as generic_model_access
from ozpcenter import models
from ozpcenter.scripts import sample_data_generator as data_gen
import ozpcenter.api.contact_type.views as views


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
        self.assertTrue('Civillian' in names)
        self.assertTrue('Government' in names)
        self.assertTrue(len(names) > 2)

    def test_get_contact_type(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/contact_type/1/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        name = response.data['name']
        self.assertEqual(name, 'Civillian')

    def test_create_contact_type(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        url = '/api/contact_type/'
        data = {'name': 'New Contact Type'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        name = response.data['name']
        self.assertEqual(name, 'New Contact Type')

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

    def test_delete_contact_type(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        url = '/api/contact_type/1/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
