"""
Tests for listing endpoints
"""
import json

from rest_framework import status
from rest_framework.test import APITestCase

from ozpcenter import model_access as generic_model_access
from ozpcenter import models
from ozpcenter.scripts import sample_data_generator as data_gen


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

    def _validate_listing_map_keys(self, listing_map):
        """
        Used to validate the keys of a listing
        """
        if not isinstance(listing_map, dict):
            raise Exception('listing_map is not type dict, it is {0!s}'.format(type(listing_map)))

        listing_map_default_keys = ['id', 'is_bookmarked', 'screenshots',
                                    'doc_urls', 'owners', 'categories', 'tags', 'contacts', 'intents',
                                    'small_icon', 'large_icon', 'banner_icon', 'large_banner_icon',
                                    'agency', 'last_activity', 'current_rejection', 'listing_type',
                                    'title', 'approved_date', 'edited_date', 'description', 'launch_url',
                                    'version_name', 'unique_name', 'what_is_new', 'description_short',
                                    'requirements', 'approval_status', 'is_enabled', 'is_featured',
                                    'is_deleted', 'avg_rate', 'total_votes', 'total_rate5', 'total_rate4',
                                    'total_rate3', 'total_rate2', 'total_rate1', 'total_reviews',
                                    'iframe_compatible', 'security_marking', 'is_private',
                                    'required_listings']

        listing_keys = [k for k, v in listing_map.items()]

        invalid_key_list = []

        for current_key in listing_map_default_keys:
            if current_key not in listing_keys:
                invalid_key_list.append(current_key)

        return invalid_key_list

    def _request_helper(self, url, method, data=None, username='bigbrother', status_code=200):
        """
        Request Helper
        """
        user = generic_model_access.get_profile(username).user
        self.client.force_authenticate(user=user)

        response = None

        if method.upper() == 'GET':
            response = self.client.get(url, format='json')
        elif method.upper() == 'POST':
            response = self.client.post(url, data, format='json')
        elif method.upper() == 'PUT':
            response = self.client.put(url, data, format='json')
        elif method.upper() == 'DELETE':
            response = self.client.delete(url, format='json')
        else:
            raise Exception('method is not supported')

        if response:
            if status_code == 200:
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            elif status_code == 201:
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            elif status_code == 204:
                self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            else:
                raise Exception('status code is not supported')

        return response

    def test_listing_activities(self):
        action_log = []
        # CREATED
        url = '/api/listing/'

        data = {
            'title': 'mr jones app',
            'security_marking': 'UNCLASSIFIED'
        }

        response = self._request_helper(url, 'POST', data=data, username='jones', status_code=201)
        app_id = response.data['id']
        data = response.data

        # VERIFY that is was created
        url = '/api/listing/{0!s}/activity/'.format(app_id)
        response = self._request_helper(url, 'GET', username='jones', status_code=200)

        activity_actions = [i['action'] for i in response.data]
        self.assertEqual(len(activity_actions), 1)
        action_log.insert(0, models.ListingActivity.CREATED)
        self.assertEqual(activity_actions, action_log)
        activity_agency = [i['listing']['agency'] for i in response.data]
        self.assertEquals(json.dumps(activity_agency[0]), '{"title": "Ministry of Truth", "short_name": "Minitrue"}')

        # MODIFIED
        data['title'] = "mr jones mod app"
        url = '/api/listing/{0!s}/'.format(app_id)
        response = self._request_helper(url, 'PUT', data=data, username='jones', status_code=200)
        data = response.data

        # VERIFY that is was modified
        url = '/api/listing/{0!s}/activity/'.format(app_id)
        response = self._request_helper(url, 'GET', username='jones', status_code=200)

        activity_actions = [i['action'] for i in response.data]
        self.assertEqual(len(activity_actions), 2)
        action_log.insert(0, models.ListingActivity.MODIFIED)
        self.assertEqual(activity_actions, action_log)
        activity_agency = [i['listing']['agency'] for i in response.data]
        self.assertEquals(json.dumps(activity_agency[0]), '{"title": "Ministry of Truth", "short_name": "Minitrue"}')

        # SUBMITTED
        data['approval_status'] = models.Listing.PENDING
        url = '/api/listing/{0!s}/'.format(app_id)
        response = self._request_helper(url, 'PUT', data=data, username='jones', status_code=200)

        # Verify that is was submitted
        url = '/api/listing/{0!s}/activity/'.format(app_id)
        response = self._request_helper(url, 'GET', username='jones', status_code=200)

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
        response = self._request_helper(url, 'PUT', data=data, username='jones', status_code=200)

        # Verify that it was disabled
        url = '/api/listing/{0!s}/activity/'.format(app_id)
        response = self._request_helper(url, 'GET', username='jones', status_code=200)
        activity_actions = [i['action'] for i in response.data]
        self.assertEquals(len(activity_actions), 4)
        action_log.insert(0, models.ListingActivity.DISABLED)
        self.assertEqual(activity_actions, action_log)
        activity_agency = [i['listing']['agency'] for i in response.data]
        self.assertEquals(json.dumps(activity_agency[0]), '{"title": "Ministry of Truth", "short_name": "Minitrue"}')

        # ENABLED
        data['is_enabled'] = True
        url = '/api/listing/{0!s}/'.format(app_id)
        response = self._request_helper(url, 'PUT', data=data, username='jones', status_code=200)

        # Verify that it was enabled
        url = '/api/listing/{0!s}/activity/'.format(app_id)
        response = self._request_helper(url, 'GET', username='jones', status_code=200)
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
        self.assertEqual(data.get('next'), None)
        self.assertEqual(data.get('previous'), None)
        self.assertTrue(len(data.get('results')) >= 0)
