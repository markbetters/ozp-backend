"""
Tests for listing endpoints
"""
import json

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from ozpcenter import model_access as generic_model_access
from ozpcenter import models
from ozpcenter.scripts import sample_data_generator as data_gen
from ozpcenter.tests.helper import validate_listing_map_keys
from ozpcenter.tests.helper import unittest_request_helper


@override_settings(ES_ENABLED=False)
class ListingActivitiesApiTest(APITestCase):

    def setUp(self):
        """
        setUp is invoked before each test method
        """
        pass

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the whole TestCase (only run once for the TestCase)
        """
        data_gen.run()

    def test_listing_activities(self):
        action_log = []
        # CREATED
        url = '/api/listing/'

        data = {
            'title': 'mr jones app',
            'security_marking': 'UNCLASSIFIED'
        }

        response = unittest_request_helper(self, url, 'POST', data=data, username='jones', status_code=201)
        app_id = response.data['id']
        data = response.data

        # VERIFY that is was created
        url = '/api/listing/{0!s}/activity/'.format(app_id)
        response = unittest_request_helper(self, url, 'GET', username='jones', status_code=200)

        activity_actions = [i['action'] for i in response.data]
        self.assertEqual(len(activity_actions), 1)
        action_log.insert(0, models.ListingActivity.CREATED)
        self.assertEqual(activity_actions, action_log)
        activity_agency = [i['listing']['agency'] for i in response.data]
        self.assertEquals(json.dumps(activity_agency[0]), '{"title": "Ministry of Truth", "short_name": "Minitrue"}')

        # MODIFIED
        data['title'] = "mr jones mod app"
        url = '/api/listing/{0!s}/'.format(app_id)
        response = unittest_request_helper(self, url, 'PUT', data=data, username='jones', status_code=200)
        data = response.data

        # VERIFY that is was modified
        url = '/api/listing/{0!s}/activity/'.format(app_id)
        response = unittest_request_helper(self, url, 'GET', username='jones', status_code=200)

        activity_actions = [i['action'] for i in response.data]
        self.assertEqual(len(activity_actions), 2)
        action_log.insert(0, models.ListingActivity.MODIFIED)
        self.assertEqual(activity_actions, action_log)
        activity_agency = [i['listing']['agency'] for i in response.data]
        self.assertEquals(json.dumps(activity_agency[0]), '{"title": "Ministry of Truth", "short_name": "Minitrue"}')

        # SUBMITTED
        data['approval_status'] = models.Listing.PENDING
        url = '/api/listing/{0!s}/'.format(app_id)
        response = unittest_request_helper(self, url, 'PUT', data=data, username='jones', status_code=200)

        # Verify that is was submitted
        url = '/api/listing/{0!s}/activity/'.format(app_id)
        response = unittest_request_helper(self, url, 'GET', username='jones', status_code=200)

        activity_actions = [i['action'] for i in response.data]
        self.assertEquals(len(activity_actions), 3)
        action_log.insert(0, models.ListingActivity.SUBMITTED)
        self.assertEqual(activity_actions, action_log)
        self.assertTrue(models.ListingActivity.SUBMITTED in activity_actions)
        activity_agency = [i['listing']['agency'] for i in response.data]
        self.assertEquals(json.dumps(activity_agency[0]), '{"title": "Ministry of Truth", "short_name": "Minitrue"}')

        # APPROVED_ORG

        # APPROVED

        # DISABLE
        data['is_enabled'] = False
        url = '/api/listing/{0!s}/'.format(app_id)
        response = unittest_request_helper(self, url, 'PUT', data=data, username='jones', status_code=200)

        # Verify that it was disabled
        url = '/api/listing/{0!s}/activity/'.format(app_id)
        response = unittest_request_helper(self, url, 'GET', username='jones', status_code=200)
        activity_actions = [i['action'] for i in response.data]
        self.assertEquals(len(activity_actions), 4)
        action_log.insert(0, models.ListingActivity.DISABLED)
        self.assertEqual(activity_actions, action_log)
        activity_agency = [i['listing']['agency'] for i in response.data]
        self.assertEquals(json.dumps(activity_agency[0]), '{"title": "Ministry of Truth", "short_name": "Minitrue"}')

        # ENABLED
        data['is_enabled'] = True
        url = '/api/listing/{0!s}/'.format(app_id)
        response = unittest_request_helper(self, url, 'PUT', data=data, username='jones', status_code=200)

        # Verify that it was enabled
        url = '/api/listing/{0!s}/activity/'.format(app_id)
        response = unittest_request_helper(self, url, 'GET', username='jones', status_code=200)
        activity_actions = [i['action'] for i in response.data]
        self.assertEquals(len(activity_actions), 5)
        action_log.insert(0, models.ListingActivity.ENABLED)
        self.assertEqual(activity_actions, action_log)
        activity_agency = [i['listing']['agency'] for i in response.data]
        self.assertEquals(json.dumps(activity_agency[0]), '{"title": "Ministry of Truth", "short_name": "Minitrue"}')

    def test_get_all_listing_activities(self):
        """
        All stewards should be able to access this endpoint (not std users)

        Make sure org stewards of one org can't access activity for private
        listings of another org.
        """
        expected_titles = ['Air Mail', 'Bread Basket', 'Chart Course',
            'Chatter Box', 'Clipboard']
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/activity/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/activity/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [i['listing']['title'] for i in response.data]
        counter = 0
        for i in expected_titles:
            self.assertTrue(i in titles)
            counter += 1
        self.assertEqual(counter, len(expected_titles))

        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/activity/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [i['listing']['title'] for i in response.data]
        titles = list(set(titles))
        counter = 0
        for i in expected_titles:
            # Bread Basket is a private app, and bigbrother is not in that
            # organization
            if i != 'Bread Basket':
                self.assertTrue(i in titles)
                counter += 1
        self.assertEqual(counter, len(expected_titles) - 1)

    def test_get_self_listing_activities(self):
        """
        Returns activity for listings owned by current user
        """
        expected_titles = ['Bread Basket', 'Chatter Box']

        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/self/listings/activity/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [i['listing']['title'] for i in response.data]
        counter = 0
        for i in expected_titles:
            self.assertTrue(i in titles)
            counter += 1
        self.assertEqual(counter, len(expected_titles))

    def test_get_listing_activities_offset_limit(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/activity/?offset=0&limit=24'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue('count' in data)
        self.assertTrue('previous' in data)
        self.assertTrue('next' in data)
        self.assertTrue('results' in data)
        self.assertTrue('/api/listings/activity/?limit=24&offset=24' in data.get('next'))
        self.assertEqual(data.get('previous'), None)
        self.assertTrue(len(data.get('results')) >= 1)

    def test_get_self_listing_activities_offset_limit(self):
        user = generic_model_access.get_profile('aaronson').user
        self.client.force_authenticate(user=user)
        url = '/api/self/listings/activity/?offset=0&limit=24'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertTrue('count' in data)
        self.assertTrue('previous' in data)
        self.assertTrue('next' in data)
        self.assertTrue('results' in data)
        self.assertTrue('/api/self/listings/activity/?limit=24&offset=24' in data.get('next'))
        self.assertEqual(data.get('previous'), None)
        self.assertTrue(len(data.get('results')) >= 0)
