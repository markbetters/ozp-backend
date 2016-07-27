"""
Tests for listing endpoints
"""
from rest_framework import status
from rest_framework.test import APITestCase

from ozpcenter import model_access as generic_model_access
from ozpcenter.scripts import sample_data_generator as data_gen


class ListingUserApiTest(APITestCase):

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

    def test_self_listing(self):
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/self/listing/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles = [i['title'] for i in response.data]
        self.assertTrue('Bread Basket' in titles)
        self.assertTrue('Chatter Box' in titles)
        self.assertTrue('Air Mail' not in titles)
        for listing_map in response.data:
            self.assertEquals(self._validate_listing_map_keys(listing_map), [])

    def test_self_deleted_listing(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/self/listing/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles = [i['id'] for i in response.data]
        self.assertTrue('1' not in titles)
        for listing_map in response.data:
            self.assertEquals(self._validate_listing_map_keys(listing_map), [])
