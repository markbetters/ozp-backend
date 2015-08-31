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

import ozpcenter.access_control as access_control

from ozpcenter.scripts import sample_data_generator as data_gen
import ozpcenter.api.agency.views as views
from ozpcenter import models as models
from ozpcenter import model_access as generic_model_access


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

    def test_update_agency(self):
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

    def test_delete_agency(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        url = '/api/agency/1/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

