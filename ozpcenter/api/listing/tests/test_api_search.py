"""
Tests for listing endpoints
"""
from rest_framework import status
from rest_framework.test import APITestCase

from ozpcenter import model_access as generic_model_access
from ozpcenter.scripts import sample_data_generator as data_gen
from ozpcenter.tests.helper import ListingFile


class ListingSearchApiTest(APITestCase):

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

    def test_search_categories_single_with_space(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        search_category = 'Health and Fitness'
        url = '/api/listings/search/?category={}'.format(search_category)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles = sorted([i['title'] for i in response.data])
        listings_from_file = ListingFile.filter_listings(is_enabled=True,
                                        approval_status='APPROVED',
                                        categories__in=['Health and Fitness'])
        sorted_listings_from_file = sorted([listing['title'] for listing in listings_from_file])
        print(titles)
        print(sorted_listings_from_file)

        # TODO: TEST Newspaper when is_private = True

        self.assertEqual(titles, sorted_listings_from_file)

        for listing_map in response.data:
            self.assertEquals(self._validate_listing_map_keys(listing_map), [])

    def test_search_categories_multiple_with_space(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?category=Health and Fitness&category=Communication'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles = sorted([i['title'] for i in response.data])
        listings_from_file = ListingFile.filter_listings(is_enabled=True,
                                        approval_status='APPROVED',
                                        categories__in=['Health and Fitness','Communication'])
        sorted_listings_from_file = sorted([listing['title'] for listing in listings_from_file])

        self.assertEqual(titles, sorted_listings_from_file)

        for listing_map in response.data:
            self.assertEquals(self._validate_listing_map_keys(listing_map), [])

    def test_search_text(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?search=air ma'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles = [i['title'] for i in response.data]
        self.assertTrue('Air Mail' in titles)
        self.assertEqual(len(titles), 10)
        for listing_map in response.data:
            self.assertEquals(self._validate_listing_map_keys(listing_map), [])

    def test_search_type(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?type=Web Application'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles = [i['title'] for i in response.data]
        self.assertTrue('Air Mail' in titles)
        self.assertTrue(len(titles) > 7)
        for listing_map in response.data:
            self.assertEquals(self._validate_listing_map_keys(listing_map), [])

    def test_search_tags(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?search=tag_1'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles = [i['title'] for i in response.data]
        self.assertTrue('Air Mail 1' in titles)
        self.assertTrue(len(titles) == 1)
        for listing_map in response.data:
            self.assertEquals(self._validate_listing_map_keys(listing_map), [])

    def test_search_tags_startwith(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?search=tag_'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles = [i['title'] for i in response.data]
        self.assertTrue('Air Mail 1' in titles)
        self.assertTrue('Air Mail' in titles)
        self.assertTrue(len(titles) == 10)
        for listing_map in response.data:
            self.assertEquals(self._validate_listing_map_keys(listing_map), [])

    def test_search_is_enable(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?search=airmail&type=Web Application'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ids = [record.get('id') for record in response.data]
        self.assertEqual(ids, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        for listing_map in response.data:
            self.assertEquals(self._validate_listing_map_keys(listing_map), [])

        # Disable one app
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        url = '/api/listing/1/'
        title = 'airmail_disabled'

        data = {
            "title": title,
            "description": "description of app",
            "launch_url": "http://www.google.com/launch",
            "version_name": "1.0.0",
            "unique_name": "org.apps.julia-one",
            "what_is_new": "nothing is new",
            "description_short": "a shorter description",
            "requirements": "None",
            "is_private": "true",
            "is_enable": "false",
            "contacts": [
                {"email": "a@a.com", "secure_phone": "111-222-3434",
                 "unsecure_phone": "444-555-4545", "name": "me",
                 "contact_type": {"name": "Government"}
                    },
                {"email": "b@b.com", "secure_phone": "222-222-3333",
                 "unsecure_phone": "555-555-5555", "name": "you",
                 "contact_type": {"name": "Military"}
                    }
                ],
            "security_marking": "UNCLASSIFIED",
            "listing_type": {"title": "Web Application"},
            "small_icon": {"id": 1},
            "large_icon": {"id": 2},
            "banner_icon": {"id": 3},
            "large_banner_icon": {"id": 4},
            "categories": [
                {"title": "Business"},
                {"title": "Education"}
                ],
            "owners": [
                {"user": {"username": "wsmith"}},
                {"user": {"username": "julia"}}
                ],
            "tags": [
                {"name": "demo"},
                {"name": "map"}
                ],
            "intents": [
                {"action": "/application/json/view"},
                {"action": "/application/json/edit"}
                ],
            "doc_urls": [
                {"name": "wiki", "url": "http://www.google.com/wiki"},
                {"name": "guide", "url": "http://www.google.com/guide"}
                ],
            "screenshots": [
                {"small_image": {"id": 1}, "large_image": {"id": 2}, "description": "Test Description"},
                {"small_image": {"id": 3}, "large_image": {"id": 4}, "description": "Test Description"}
                ]

            }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?search=airmail&type=Web Application'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ids = [record.get('id') for record in response.data]
        self.assertEqual(ids, [2, 3, 4, 5, 6, 7, 8, 9, 10])
        for listing_map in response.data:
            self.assertEquals(self._validate_listing_map_keys(listing_map), [])

    def test_search_agency(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?agency=Minipax&agency=Miniluv'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles = [i['title'] for i in response.data]
        self.assertTrue('Chatter Box' in titles)
        for listing_map in response.data:
            self.assertEquals(self._validate_listing_map_keys(listing_map), [])

    def test_search_limit(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?limit=1'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles = [i['title'] for i in response.data['results']]
        self.assertTrue('JotSpot' in titles)
        self.assertEqual(len(titles), 1)
        for listing_map in response.data['results']:
            self.assertEquals(self._validate_listing_map_keys(listing_map), [])

    def test_search_offset_limit(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?offset=1&limit=1'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles = [i['title'] for i in response.data['results']]
        self.assertTrue('JotSpot 1' in titles)
        self.assertEqual(len(titles), 1)
        for listing_map in response.data['results']:
            self.assertEquals(self._validate_listing_map_keys(listing_map), [])
