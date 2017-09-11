"""
Tests for Listing Elasticsearch Search endpoints

/api/listing/essearch
"""
import logging

from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase

from ozpcenter import model_access as generic_model_access
from ozpcenter.scripts import sample_data_generator as data_gen
from ozpcenter.tests.helper import ListingFile

from ozpcenter.tests.helper import unittest_request_helper
from ozpcenter.api.listing import model_access_es
from ozpcenter.api.listing.elasticsearch_util import elasticsearch_factory


@override_settings(ES_ENABLED=False)
class ListingESSearchApiTest(APITestCase):

    @override_settings(ES_ENABLED=True)
    def setUp(self):
        """
        setUp is invoked before each test method
        """
        self.error_string = None
        self.es_failed = False
        try:
            elasticsearch_factory.check_elasticsearch()
        except Exception as err:
            self.error_string = str(err)
            self.es_failed = True

        if not self.es_failed:
            logging.getLogger('elasticsearch').setLevel(logging.CRITICAL)
            model_access_es.bulk_reindex()

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the whole TestCase (only run once for the TestCase)
        """
        data_gen.run()

    @override_settings(ES_ENABLED=True)
    def test_essearch_categories_single_with_space(self):
        """
        test_essearch_categories_single_with_space
        TODO: Iterate through all categories in categories.yaml file, Deal with Private apps
        TODO: TEST listing_title = Newspaper when is_private = True
        """
        if self.es_failed:
            self.skipTest('Elasticsearch is not currently up: {}'.format(self.error_string))

        search_category = 'Health and Fitness'
        url = '/api/listings/essearch/?category={}'.format(search_category)
        response = unittest_request_helper(self, url, 'GET', username='wsmith', status_code=200)

        titles = sorted([i['title'] for i in response.data['results']])
        listings_from_file = ListingFile.filter_listings(is_enabled=True,
                                        approval_status='APPROVED',
                                        categories__in=['Health and Fitness'])
        sorted_listings_from_file = sorted([listing['title'] for listing in listings_from_file])
        self.assertEqual(titles, sorted_listings_from_file)

    @override_settings(ES_ENABLED=True)
    def test_essearch_categories_multiple_with_space(self):
        """
        test_essearch_categories_multiple_with_space
        TODO: TEST listing_title = Newspaper when is_private = True
        """
        if self.es_failed:
            self.skipTest('Elasticsearch is not currently up: {}'.format(self.error_string))
        url = '/api/listings/essearch/?category=Health and Fitness&category=Communication'
        response = unittest_request_helper(self, url, 'GET', username='wsmith', status_code=200)

        titles = sorted([i['title'] for i in response.data['results']])
        listings_from_file = ListingFile.filter_listings(is_enabled=True,
                                        approval_status='APPROVED',
                                        categories__in=['Health and Fitness', 'Communication'])
        sorted_listings_from_file = sorted([listing['title'] for listing in listings_from_file])

        self.assertEqual(titles, sorted_listings_from_file)
    #
    # def test_search_text(self):
    #     user = generic_model_access.get_profile('wsmith').user
    #     self.client.force_authenticate(user=user)
    #     url = '/api/listings/search/?search=air mail'
    #     #  url = '/api/listings/search/?search=air ma'
    #     #  TODO: Figure out why 'air ma' returns
    #     # ['Sun',  'Barbecue',  'Wolf Finder',  'LIT RANCH',  'Navigation using Maps',
    #     #                     'Air Mail',  'Rogue',  'Cheese and Crackers',
    #     #                     'Double Heroides',  'KIAA0319',  'Karta GPS',  'Sir Baboon McGood']
    #     response = self.client.get(url, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    #     titles = [i['title'] for i in response.data['results']]
    #     excepted_titles = ['Air Mail']
    #     self.assertEqual(titles, excepted_titles)
    #     for listing_map in response.data:
    #         self.assertEquals(validate_listing_map_keys(listing_map), [])
    #
    # @skip("TODO See Below todo (rivera 20170818)")
    # def test_search_text_partial(self):
    #     user = generic_model_access.get_profile('wsmith').user
    #     self.client.force_authenticate(user=user)
    #     url = '/api/listings/search/?search=air ma'
    #
    #     response = self.client.get(url, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    #     titles = [i['title'] for i in response.data['results']]
    #     excepted_titles = ['Air Mail']
    #     #  TODO: Figure out why 'air ma' returns
    #     # ['Sun',  'Barbecue',  'Wolf Finder',  'LIT RANCH',  'Navigation using Maps',
    #     #                     'Air Mail',  'Rogue',  'Cheese and Crackers',
    #     #                     'Double Heroides',  'KIAA0319',  'Karta GPS',  'Sir Baboon McGood']
    #     self.assertEqual(titles, excepted_titles)
    #     for listing_map in response.data:
    #         self.assertEquals(validate_listing_map_keys(listing_map), [])
    #

    @override_settings(ES_ENABLED=True)
    def test_essearch_filter_type(self):
        """
        test_essearch_filter_type
        TODO: Iterate through all Listings types in listings_types.yaml file, Deal with Private apps
        """
        if self.es_failed:
            self.skipTest('Elasticsearch is not currently up: {}'.format(self.error_string))

        url = '/api/listings/essearch/?type=Web Application'
        response = unittest_request_helper(self, url, 'GET', username='wsmith', status_code=200)

        titles = sorted([i['title'] for i in response.data['results']])
        listings_from_file = ListingFile.filter_listings(is_enabled=True,
                                        approval_status='APPROVED',
                                        listing_type='Web Application')
        sorted_listings_from_file = sorted([listing['title'] for listing in listings_from_file])
        self.assertEqual(titles, sorted_listings_from_file)

    @override_settings(ES_ENABLED=True)
    def test_essearch_tags(self):
        if self.es_failed:
            self.skipTest('Elasticsearch is not currently up: {}'.format(self.error_string))

        url = '/api/listings/essearch/?search=demo_tag'
        response = unittest_request_helper(self, url, 'GET', username='wsmith', status_code=200)

        titles = sorted([i['title'] for i in response.data['results']])
        expected_listing = ['Air Mail', 'Bread Basket', 'Chart Course', 'Chatter Box', 'Clipboard',
            'Deadpool', 'Desktop Virtualization', 'Diamond', 'Dinosaur', 'Dragons', 'FrameIt',
            'Harley-Davidson CVO', 'Hatch Latch', 'JotSpot', 'LocationAnalyzer', 'LocationLister',
            'LocationViewer', 'Mini Dachshund', 'Monkey Finder', 'Personal Computer', 'Ruby on Rails',
            'Skybox', 'Smart Phone', 'Taxonomy Classifier']

        self.assertEqual(titles, expected_listing)

    @override_settings(ES_ENABLED=True)
    def test_essearch_filter_tag(self):
        if self.es_failed:
            self.skipTest('Elasticsearch is not currently up: {}'.format(self.error_string))

        url = '/api/listings/essearch/?tag=demo_tag'
        response = unittest_request_helper(self, url, 'GET', username='wsmith', status_code=200)

        titles = sorted([i['title'] for i in response.data['results']])
        listings_from_file = ListingFile.filter_listings(is_enabled=True,
                                        approval_status='APPROVED',
                                        tags__in=['demo_tag'])
        sorted_listings_from_file = sorted([listing['title'] for listing in listings_from_file])

        self.assertEqual(titles, sorted_listings_from_file)

    # def test_search_tags_startwith(self):
    #     user = generic_model_access.get_profile('wsmith').user
    #     self.client.force_authenticate(user=user)
    #     url = '/api/listings/search/?search=tag_'
    #     response = self.client.get(url, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    #     titles = [i['title'] for i in response.data['results']]
    #     self.assertTrue('Air Mail' in titles)
    #     self.assertTrue(len(titles) == 1)
    #     for listing_map in response.data:
    #         self.assertEquals(validate_listing_map_keys(listing_map), [])
    #
    @override_settings(ES_ENABLED=True)
    def test_essearch_is_enable(self):
        if self.es_failed:
            self.skipTest('Elasticsearch is not currently up: {}'.format(self.error_string))

        url = '/api/listings/essearch/?search=demo_tag&type=Web Application'
        response = unittest_request_helper(self, url, 'GET', username='wsmith', status_code=200)

        titles_ids = [[record.get('title'), record.get('id')] for record in response.data['results']]
        titles = sorted([i[0] for i in titles_ids])
        expected_titles = ['Air Mail', 'Bread Basket', 'Chart Course', 'Chatter Box', 'Clipboard',
            'FrameIt', 'Hatch Latch', 'JotSpot', 'LocationAnalyzer', 'LocationLister',
            'LocationViewer', 'Monkey Finder', 'Skybox', 'Smart Phone', 'Taxonomy Classifier']

        self.assertEqual(titles, expected_titles)

        # Disable one app
        url = '/api/listing/{}/'.format(titles_ids[0][1])
        title = '{}_disabled'.format(titles_ids[0][0])

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
        response = unittest_request_helper(self, url, 'PUT', data=data, username='bigbrother', status_code=200)

        elasticsearch_factory.wait_for_yellow_cluster_heath()

        # Check
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/essearch/?search=demo_tag&type=Web Application'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles_ids = [[record.get('title'), record.get('id')] for record in response.data['results']]
        titles = sorted([i[0] for i in titles_ids])

        expected_titles = ['Bread Basket', 'Chart Course', 'Chatter Box', 'Clipboard',
            'FrameIt', 'Hatch Latch', 'JotSpot', 'LocationAnalyzer', 'LocationLister',
            'LocationViewer', 'Monkey Finder', 'Skybox', 'Smart Phone', 'Taxonomy Classifier']

        self.assertEqual(titles, expected_titles)
    #
    # def test_search_agency(self):
    #     user = generic_model_access.get_profile('wsmith').user
    #     self.client.force_authenticate(user=user)
    #     url = '/api/listings/search/?agency=Minipax&agency=Miniluv'
    #     response = self.client.get(url, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    #     titles = [i['title'] for i in response.data['results']]
    #     self.assertTrue('Chatter Box' in titles)
    #     for listing_map in response.data:
    #         self.assertEquals(validate_listing_map_keys(listing_map), [])
    #
    # def test_search_limit(self):
    #     user = generic_model_access.get_profile('wsmith').user
    #     self.client.force_authenticate(user=user)
    #     url = '/api/listings/search/?limit=1'
    #     response = self.client.get(url, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    #     titles = [i['title'] for i in response.data['results']]
    #     # TODO: Not predictable, This will change every time listing.yaml changes
    #     self.assertTrue('Global Navigation Grid Code' in titles)
    #     self.assertEqual(len(titles), 1)
    #     for listing_map in response.data['results']:
    #         self.assertEquals(validate_listing_map_keys(listing_map), [])
    #
    # def test_search_offset_limit(self):
    #     user = generic_model_access.get_profile('wsmith').user
    #     self.client.force_authenticate(user=user)
    #     url = '/api/listings/search/?offset=1&limit=1'
    #     response = self.client.get(url, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    #     titles = [i['title'] for i in response.data['results']]
    #     # TODO: Not predictable, This will change every time listing.yaml changes
    #     self.assertTrue('Map of the world' in titles)
    #     self.assertEqual(len(titles), 1)
    #     for listing_map in response.data['results']:
    #         self.assertEquals(validate_listing_map_keys(listing_map), [])
