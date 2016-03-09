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

    def test_get_apps_mall_stewards_for_apps_mall_steward_level(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/?role=APPS_MALL_STEWARD'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [i['user']['username'] for i in response.data]
        self.assertTrue('bigbrother' in usernames)
        self.assertTrue('julia' not in usernames)
        self.assertTrue('jones' not in usernames)

    def test_get_apps_mall_stewards_for_org_steward_level(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/?role=APPS_MALL_STEWARD'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [i['user']['username'] for i in response.data]
        self.assertTrue('bigbrother' in usernames)
        self.assertTrue('julia' not in usernames)
        self.assertTrue('jones' not in usernames)

    def test_get_apps_mall_stewards_for_user_level(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/?role=APPS_MALL_STEWARD'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [i['user']['username'] for i in response.data]
        self.assertTrue('bigbrother' in usernames)
        self.assertTrue('julia' not in usernames)
        self.assertTrue('jones' not in usernames)

    def test_get_org_stewards_for_apps_mall_steward_level(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/?role=ORG_STEWARD'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [i['user']['username'] for i in response.data]
        self.assertTrue('wsmith' in usernames)
        self.assertTrue('julia' in usernames)
        self.assertTrue('jones' not in usernames)
        self.assertTrue('bigbrother' not in usernames)

    def test_get_org_stewards_for_org_steward_level(self):
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

    def test_get_org_stewards_for_user_level(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/?role=ORG_STEWARD'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [i['user']['username'] for i in response.data]
        self.assertTrue('wsmith' in usernames)
        self.assertTrue('julia' in usernames)
        self.assertTrue('jones' not in usernames)
        self.assertTrue('bigbrother' not in usernames)

    def test_get_users_for_apps_mall_steward_level(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/?role=USER'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [i['user']['username'] for i in response.data]
        self.assertTrue('wsmith' not in usernames)
        self.assertTrue('aaronson' in usernames)
        self.assertTrue('julia' not in usernames)
        self.assertTrue('jones' in usernames)
        self.assertTrue('bigbrother' not in usernames)

    def test_get_users_for_org_steward_level(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/?role=USER'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [i['user']['username'] for i in response.data]
        self.assertTrue('wsmith' not in usernames)
        self.assertTrue('aaronson' in usernames)
        self.assertTrue('julia' not in usernames)
        self.assertTrue('jones' in usernames)
        self.assertTrue('bigbrother' not in usernames)

    def test_get_users_for_user_level(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/?role=USER'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [i['user']['username'] for i in response.data]
        self.assertTrue('wsmith' not in usernames)
        self.assertTrue('aaronson' in usernames)
        self.assertTrue('julia' not in usernames)
        self.assertTrue('jones' in usernames)
        self.assertTrue('bigbrother' not in usernames)

    '''
    Testing /api/self/profile endpoint
    '''
    def test_get_update_self_for_apps_mall_steward_level(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        url = '/api/self/profile/'

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), 4)
        self.assertEqual(response.data.get('display_name'), 'Big Brother')
        self.assertEqual(response.data.get('organizations'), [{'short_name':'Minipax','title':'Ministry of Peace'}])
        self.assertEqual(response.data.get('stewarded_organizations'), [])
        self.assertEqual(response.data.get('user').get('username'), 'bigbrother')
        self.assertEqual(response.data.get('user').get('groups'), [{'name':'APPS_MALL_STEWARD'}])
        self.assertEqual(response.data.get('highest_role'), 'APPS_MALL_STEWARD')
        self.assertEqual(response.data.get('center_tour_flag'), True)
        self.assertEqual(response.data.get('hud_tour_flag'), True)
        self.assertEqual(response.data.get('webtop_tour_flag'), True)

        combinations = [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1],
                        [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]]

        for combination in combinations:
            center_tour_flag = bool(combination[0])
            webtop_tour_flag = bool(combination[1])
            stewarded_organizations = bool(combination[2])

            data = {'id':5,'center_tour_flag':center_tour_flag, 'hud_tour_flag':webtop_tour_flag,
                    'webtop_tour_flag':stewarded_organizations}
            response = self.client.put(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data.get('id'), 4)
            self.assertEqual(response.data.get('display_name'), 'Big Brother')
            self.assertEqual(response.data.get('organizations'), [{'short_name':'Minipax','title':'Ministry of Peace'}])
            self.assertEqual(response.data.get('stewarded_organizations'), [])
            self.assertEqual(response.data.get('user').get('username'), 'bigbrother')
            self.assertEqual(response.data.get('user').get('groups'), [{'name':'APPS_MALL_STEWARD'}])
            self.assertEqual(response.data.get('highest_role'), 'APPS_MALL_STEWARD')
            self.assertEqual(response.data.get('center_tour_flag'), center_tour_flag)
            self.assertEqual(response.data.get('hud_tour_flag'), webtop_tour_flag)
            self.assertEqual(response.data.get('webtop_tour_flag'), stewarded_organizations)

            response = self.client.get(url, format='json')
            self.assertEqual(response.data.get('center_tour_flag'), center_tour_flag)
            self.assertEqual(response.data.get('hud_tour_flag'), webtop_tour_flag)
            self.assertEqual(response.data.get('webtop_tour_flag'), stewarded_organizations)

    def test_update_self_for_apps_mall_steward_level_serializer_exception(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        url = '/api/self/profile/'
        data = {'id':5,'center_tour_flag':4}
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_data = {'center_tour_flag': ['"4" is not a valid boolean.']}
        self.assertEqual(response.data, expected_data)

    def test_update_self_for_apps_mall_steward_level_invalid_user(self):
        self.client.login(username='invalid', password='invalid')
        url = '/api/self/profile/'
        data = {'id':5,'center_tour_flag': False}
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        expected_data = {'detail': 'Authentication credentials were not provided.'}
        self.assertEqual(response.data, expected_data)

    def test_get_update_self_for_org_steward_level(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/self/profile/'

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), 1)
        self.assertEqual(response.data.get('display_name'), 'Winston Smith')
        self.assertEqual(response.data.get('organizations'), [{"short_name":"Minitrue","title":"Ministry of Truth"}])
        self.assertEqual(response.data.get('stewarded_organizations'), [{"short_name":"Minitrue","title":"Ministry of Truth"}])
        self.assertEqual(response.data.get('user').get('username'), 'wsmith')
        self.assertEqual(response.data.get('user').get('groups'), [{"name":"ORG_STEWARD"}])
        self.assertEqual(response.data.get('highest_role'), 'ORG_STEWARD')
        self.assertEqual(response.data.get('center_tour_flag'), True)
        self.assertEqual(response.data.get('hud_tour_flag'), True)
        self.assertEqual(response.data.get('webtop_tour_flag'), True)

        combinations = [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1],
                        [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]]

        for combination in combinations:
            center_tour_flag = bool(combination[0])
            webtop_tour_flag = bool(combination[1])
            stewarded_organizations = bool(combination[2])

            data = {'id':5,'center_tour_flag':center_tour_flag, 'hud_tour_flag':webtop_tour_flag,
                    'webtop_tour_flag':stewarded_organizations,
                    'stewarded_organizations': [{'title': 'Ministry of Truth'},
                                                {'title': 'Ministry of Love'}]}
            response = self.client.put(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data.get('id'), 1)
            self.assertEqual(response.data.get('display_name'), 'Winston Smith')
            self.assertEqual(response.data.get('organizations'), [{"short_name":"Minitrue","title":"Ministry of Truth"}])
            self.assertEqual(response.data.get('stewarded_organizations'), [{"short_name":"Minitrue","title":"Ministry of Truth"}])
            self.assertEqual(response.data.get('user').get('username'), 'wsmith')
            self.assertEqual(response.data.get('user').get('groups'), [{"name":"ORG_STEWARD"}])
            self.assertEqual(response.data.get('highest_role'), 'ORG_STEWARD')
            self.assertEqual(response.data.get('center_tour_flag'), center_tour_flag)
            self.assertEqual(response.data.get('hud_tour_flag'), webtop_tour_flag)
            self.assertEqual(response.data.get('webtop_tour_flag'), stewarded_organizations)

            response = self.client.get(url, format='json')
            self.assertEqual(response.data.get('center_tour_flag'), center_tour_flag)
            self.assertEqual(response.data.get('hud_tour_flag'), webtop_tour_flag)
            self.assertEqual(response.data.get('webtop_tour_flag'), stewarded_organizations)

    def test_update_self_for_user_level(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = '/api/self/profile/'

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), 7)
        self.assertEqual(response.data.get('display_name'), 'Jones')
        self.assertEqual(response.data.get('organizations'), [{"short_name":"Minitrue","title":"Ministry of Truth"}])
        self.assertEqual(response.data.get('stewarded_organizations'), [])
        self.assertEqual(response.data.get('user').get('username'), 'jones')
        self.assertEqual(response.data.get('user').get('groups'), [{'name':'USER'}])
        self.assertEqual(response.data.get('highest_role'), 'USER')
        self.assertEqual(response.data.get('center_tour_flag'), True)
        self.assertEqual(response.data.get('hud_tour_flag'), True)
        self.assertEqual(response.data.get('webtop_tour_flag'), True)

        combinations = [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1],
                        [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]]

        for combination in combinations:
            center_tour_flag = bool(combination[0])
            webtop_tour_flag = bool(combination[1])
            stewarded_organizations = bool(combination[2])

            data = {'id':5,'center_tour_flag':center_tour_flag, 'hud_tour_flag':webtop_tour_flag,
                    'webtop_tour_flag':stewarded_organizations,
                    'stewarded_organizations': [{'title': 'Ministry of Truth'},
                                                {'title': 'Ministry of Love'}]}
            response = self.client.put(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data.get('id'), 7)
            self.assertEqual(response.data.get('display_name'), 'Jones')
            self.assertEqual(response.data.get('organizations'), [{"short_name":"Minitrue","title":"Ministry of Truth"}])
            self.assertEqual(response.data.get('stewarded_organizations'), [])
            self.assertEqual(response.data.get('user').get('username'), 'jones')
            self.assertEqual(response.data.get('user').get('groups'), [{'name':'USER'}])
            self.assertEqual(response.data.get('highest_role'), 'USER')
            self.assertEqual(response.data.get('center_tour_flag'), center_tour_flag)
            self.assertEqual(response.data.get('hud_tour_flag'), webtop_tour_flag)
            self.assertEqual(response.data.get('webtop_tour_flag'), stewarded_organizations)

            response = self.client.get(url, format='json')
            self.assertEqual(response.data.get('center_tour_flag'), center_tour_flag)
            self.assertEqual(response.data.get('hud_tour_flag'), webtop_tour_flag)
            self.assertEqual(response.data.get('webtop_tour_flag'), stewarded_organizations)

    def test_update_stewarded_orgs_for_apps_mall_steward_level(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/1/'
        data = {'display_name': 'Winston Smith', 'stewarded_organizations': [
            {'title': 'Ministry of Truth'}, {'title': 'Ministry of Love'}]}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        orgs = [i['title'] for i in response.data.get('stewarded_organizations')]
        self.assertTrue('Ministry of Truth' in orgs)
        self.assertTrue('Ministry of Love' in orgs)
        self.assertEqual(len(orgs), 2)

    def test_update_stewarded_orgs_for_apps_mall_steward_level_serializer_exception(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/1/'
        data = {'display_name': 'Winston Smith', 'stewarded_organizations': False}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        expected_data = {'stewarded_organizations': {'non_field_errors': ['Expected a list of items but got type "bool".']}}
        self.assertEqual(response.data, expected_data)

    def test_update_stewarded_orgs_for_org_steward_level(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/1/'
        data = {'display_name': 'Winston Smith', 'stewarded_organizations': [
            {'title': 'Ministry of Truth'}, {'title': 'Ministry of Love'}]}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_stewarded_orgs_for_user_level(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = '/api/profile/1/'
        data = {'display_name': 'Winston Smith', 'stewarded_organizations': [
            {'title': 'Ministry of Truth'}, {'title': 'Ministry of Love'}]}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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
