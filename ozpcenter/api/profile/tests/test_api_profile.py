"""
Tests for Profile endpoints
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


class ProfileApiTest(APITestCase):

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

    def test_get_org_stewards(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/?role=ORG_STEWARD'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [i['user']['username'] for i in response.data]
        self.assertTrue('wsmith' in usernames)
        self.assertTrue('julia' in usernames)
        self.assertTrue('jones' not in usernames)
        self.assertTrue('bigbrother' not in usernames)

    def test_get_apps_mall_stewards(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/?role=APPS_MALL_STEWARD'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [i['user']['username'] for i in response.data]
        self.assertTrue('bigbrother' in usernames)
        self.assertTrue('julia' not in usernames)
        self.assertTrue('jones' not in usernames)

    def test_update_stewarded_orgs(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/1/'
        data = {'display_name': 'Winston Smith', 'stewarded_organizations': [
            {'title': 'Ministry of Truth'}, {'title': 'Ministry of Love'}]}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/1/'
        data = {'display_name': 'Winston Smith', 'stewarded_organizations': [
            {'title': 'Ministry of Truth'}, {'title': 'Ministry of Love'}]}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        orgs = [i['title'] for i in response.data['stewarded_organizations']]
        self.assertTrue('Ministry of Truth' in orgs)
        self.assertTrue('Ministry of Love' in orgs)
        self.assertEqual(len(orgs), 2)

    def test_username_starts_with(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/?username_starts_with=ws'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user']['username'], 'wsmith')

        url = '/api/profile/?username_starts_with=asdf'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)



