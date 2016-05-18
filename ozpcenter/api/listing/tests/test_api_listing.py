"""
Tests for listing endpoints
"""
from copy import deepcopy
from decimal import Decimal
import json
import unittest

from django.db import transaction
from django.db.utils import IntegrityError
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ozpcenter.scripts import sample_data_generator as data_gen
import ozpcenter.api.listing.views as views
import ozpcenter.api.listing.model_access as model_access
from ozpcenter import models as models
from ozpcenter import model_access as generic_model_access


class ListingApiTest(APITestCase):

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

    def test_search_categories_single_with_space(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?category=Health and Fitness'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [i['title'] for i in response.data]
        self.assertTrue('Hatch Latch' in titles)
        self.assertEqual(len(titles), 20)

    def test_search_categories_multiple_with_space(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?category=Health and Fitness&category=Communication'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [i['title'] for i in response.data]
        self.assertTrue('Air Mail' in titles)
        self.assertTrue('Bread Basket' in titles)

    def test_search_text(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?search=air ma'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [i['title'] for i in response.data]
        self.assertTrue('Air Mail' in titles)
        self.assertEqual(len(titles), 10)

    def test_search_type(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?type=web application'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [i['title'] for i in response.data]
        self.assertTrue('Air Mail' in titles)
        self.assertTrue(len(titles) > 7)

    def test_search_is_enable(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?search=airmail&type=web application'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ids = [record.get('id') for record in response.data]
        self.assertEqual(ids, [1, 12, 23, 34, 45, 56, 67, 78, 89, 100])

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
            "listing_type": {"title": "web application"},
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
                {"small_image": {"id": 1}, "large_image": {"id": 2}},
                {"small_image": {"id": 3}, "large_image": {"id": 4}}
                ]

            }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?search=airmail&type=web application'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ids = [record.get('id') for record in response.data]
        self.assertEqual(ids, [12, 23, 34, 45, 56, 67, 78, 89, 100])

    def test_search_agency(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?agency=Minipax&agency=Miniluv'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [i['title'] for i in response.data]
        self.assertTrue('Chatter Box' in titles)

    def test_search_limit(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?limit=1'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [i['title'] for i in response.data['results']]
        self.assertTrue('JotSpot' in titles)
        self.assertEqual(len(titles), 1)

    def test_search_offset_limit(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?offset=1&limit=1'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [i['title'] for i in response.data['results']]
        self.assertTrue('JotSpot 1' in titles)
        self.assertEqual(len(titles), 1)

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

    def test_get_reviews(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        air_mail_id = models.Listing.objects.get(title='Air Mail').id
        url = '/api/listing/%s/review/' % air_mail_id
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_review(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        air_mail_id = models.Listing.objects.get(title='Air Mail').id
        url = '/api/listing/%s/review/1/' % air_mail_id
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('rate' in response.data)
        self.assertTrue('text' in response.data)
        self.assertTrue('author' in response.data)
        self.assertTrue('listing' in response.data)

    def test_create_review(self):
        # create a new review
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        air_mail_id = models.Listing.objects.get(title='Air Mail').id
        url = '/api/listing/%s/review/' % air_mail_id
        data = {'rate': 4, 'text': 'winston test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_id = response.data['id']
        new_review = models.Review.objects.get(id=created_id)
        self.assertEqual(created_id, new_review.id)

        # creating a duplicate review should fail
        # http://stackoverflow.com/questions/21458387/transactionmanagementerror-you-cant-execute-queries-until-the-end-of-the-atom
        # try:
        #     with transaction.atomic():
        #         response = self.client.post(url, data, format='json')
        #         # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        #         self.assertTrue(0, 'Duplicate question allowed.')
        # except IntegrityError:
        #     pass

        # creating a review for an app this user cannot see should fail
        bread_basket_id = models.Listing.objects.get(title='Bread Basket').id
        user = generic_model_access.get_profile('rutherford').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/%s/review/' % bread_basket_id
        data = {'rate': 4, 'text': 'rutherford test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_no_text(self):
        # create a new review
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        air_mail_id = models.Listing.objects.get(title='Air Mail').id
        url = '/api/listing/%s/review/' % air_mail_id
        data = {'rate': 3}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_id = response.data['id']
        new_review = models.Review.objects.get(id=created_id)
        self.assertEqual(created_id, new_review.id)

    def test_update_review(self):
        """
        Also tests the listing/<id>/activity endpoint
        """
        # create a new review
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        air_mail_id = models.Listing.objects.get(title='Air Mail').id
        url = '/api/listing/%s/review/' % air_mail_id
        data = {'rate': 4, 'text': 'winston test review'}
        response = self.client.post(url, data, format='json')
        review_id = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # now update it
        url = '/api/listing/%s/review/%s/' % (air_mail_id, review_id)
        data = {'rate': 4, 'text': 'winston test review'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(4, response.data['rate'])

        # test the listing/<id>/activity endpoint
        url = '/api/listing/%s/activity/' % air_mail_id
        response = self.client.get(url, format='json')
        activiy_actions = [i['action'] for i in response.data]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(models.ListingActivity.REVIEW_EDITED in activiy_actions)

        # try to edit a review from another user - should fail
        url = '/api/listing/%s/review/1/' % air_mail_id
        data = {'rate': 4, 'text': 'winston test review'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_simple_delete_review(self):
        # create a new review
        user = generic_model_access.get_profile('rutherford').user
        self.client.force_authenticate(user=user)
        air_mail_id = models.Listing.objects.get(title='Air Mail').id
        url = '/api/listing/%s/review/' % air_mail_id
        data = {'rate': 4, 'text': 'rutherford test review'}
        response = self.client.post(url, data, format='json')
        review_id = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # now delete it
        url = '/api/listing/%s/review/%s/' % (air_mail_id, review_id)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # test the listing/<id>/activity endpoint
        url = '/api/listing/%s/activity/' % air_mail_id
        response = self.client.get(url, format='json')
        activiy_actions = [i['action'] for i in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(models.ListingActivity.REVIEW_DELETED in activiy_actions)

    def test_delete_review(self):
        # create a new review
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        air_mail_id = models.Listing.objects.get(title='Air Mail').id
        url = '/api/listing/%s/review/' % air_mail_id
        data = {'rate': 4, 'text': 'winston test review'}
        response = self.client.post(url, data, format='json')
        review_id = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # trying to delete it as a different user should fail...
        url = '/api/listing/%s/review/%s/' % (air_mail_id, review_id)
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # ... unless that user is an org steward or apps mall steward
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_rating_updates(self):
        """
        Tests that reviews are updated
        """
        title = 'Hatch Latch'
        # get a listing with no reviews
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        listing = models.Listing.objects.get(title=title)
        self.assertEqual(listing.avg_rate, 0.0)
        self.assertEqual(listing.total_votes, 0)
        self.assertEqual(listing.total_reviews, 0)
        self.assertEqual(listing.total_rate1, 0)
        self.assertEqual(listing.total_rate2, 0)
        self.assertEqual(listing.total_rate3, 0)
        self.assertEqual(listing.total_rate4, 0)
        self.assertEqual(listing.total_rate5, 0)

        # add one review
        url = '/api/listing/%s/review/' % listing.id
        data = {'rate': 1, 'text': 'winston test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check calculations
        listing = models.Listing.objects.get(title=title)
        self.assertEqual(listing.avg_rate, 1.0)
        self.assertEqual(listing.total_votes, 1)
        self.assertEqual(listing.total_reviews, 1)
        self.assertEqual(listing.total_rate1, 1)
        self.assertEqual(listing.total_rate2, 0)
        self.assertEqual(listing.total_rate3, 0)
        self.assertEqual(listing.total_rate4, 0)
        self.assertEqual(listing.total_rate5, 0)

        # add a few more reviews
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/%s/review/' % listing.id
        data = {'rate': 2, 'text': 'julia test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = generic_model_access.get_profile('charrington').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/%s/review/' % listing.id
        data = {'rate': 3, 'text': 'charrington test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/%s/review/' % listing.id
        data = {'rate': 4, 'text': 'jones test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = generic_model_access.get_profile('rutherford').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/%s/review/' % listing.id
        data = {'rate': 5, 'text': 'rutherford test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = generic_model_access.get_profile('syme').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/%s/review/' % listing.id
        data = {'rate': 5, 'text': 'syme test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        syme_review_id = response.data['id']

        # and one without a review
        user = generic_model_access.get_profile('tparsons').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/%s/review/' % listing.id
        data = {'rate': 4}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        tparsons_review_id = response.data['id']

        # check calculations
        listing = models.Listing.objects.get(title=title)
        # (2*5 + 2*4 + 1*3 + 1*2 + 1*1)/7 = (24)/7 = 3.429
        self.assertEqual(listing.avg_rate, 3.4)
        self.assertEqual(listing.total_votes, 7)
        self.assertEqual(listing.total_reviews, 6)
        self.assertEqual(listing.total_rate1, 1)
        self.assertEqual(listing.total_rate2, 1)
        self.assertEqual(listing.total_rate3, 1)
        self.assertEqual(listing.total_rate4, 2)
        self.assertEqual(listing.total_rate5, 2)

        # update an existing review
        user = generic_model_access.get_profile('tparsons').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/%s/review/%s/' % (listing.id,
            tparsons_review_id)
        data = {'rate': 2}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check calculations
        listing = models.Listing.objects.get(title=title)
        # (2*5 + 1*4 + 1*3 + 2*2 + 1*1)/7 = (22)/7 = 3.14
        self.assertEqual(listing.avg_rate, 3.1)
        self.assertEqual(listing.total_votes, 7)
        self.assertEqual(listing.total_reviews, 6)
        self.assertEqual(listing.total_rate1, 1)
        self.assertEqual(listing.total_rate2, 2)
        self.assertEqual(listing.total_rate3, 1)
        self.assertEqual(listing.total_rate4, 1)
        self.assertEqual(listing.total_rate5, 2)

        # delete an existing review
        user = generic_model_access.get_profile('syme').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/%s/review/%s/' % (listing.id, syme_review_id)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # check calculations
        listing = models.Listing.objects.get(title=title)
        # (1*5 + 1*4 + 1*3 + 2*2 + 1*1)/6 = (17)/6 = 2.83
        self.assertEqual(listing.avg_rate, 2.8)
        self.assertEqual(listing.total_votes, 6)
        self.assertEqual(listing.total_reviews, 5)
        self.assertEqual(listing.total_rate1, 1)
        self.assertEqual(listing.total_rate2, 2)
        self.assertEqual(listing.total_rate3, 1)
        self.assertEqual(listing.total_rate4, 1)
        self.assertEqual(listing.total_rate5, 1)

    def test_create_listing_minimal(self):
        # create a new listing with minimal data (title)
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/'
        title = 'julias app'
        data = {'title': title, 'security_marking': 'UNCLASSIFIED'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], title)

    def test_create_listing_no_title(self):
        # create a new listing with minimal data (title)
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/'
        data = {'description': 'text here'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # TODO: we have some strange inter-test dependency here. if  this test
    # doesn't run last (or after some other unknown test), it segfaults. Naming
    # the test 'test_z*' seems to make it run at the end. One could also run
    # the tests with the --reverse flag (but then you'd need to change this test
    # name to remove the _z)
    def test_z_create_listing_full(self):
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/'
        title = 'julias app'
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
            "listing_type": {"title": "web application"},
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
                {"small_image": {"id": 1}, "large_image": {"id": 2}},
                {"small_image": {"id": 3}, "large_image": {"id": 4}}
            ]

        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # title
        self.assertEqual(response.data['title'], title)
        # description
        self.assertEqual(response.data['description'], 'description of app')
        # launch_url
        self.assertEqual(response.data['launch_url'],
            'http://www.google.com/launch')
        # version_name
        self.assertEqual(response.data['version_name'], '1.0.0')
        # unique_name
        self.assertEqual(response.data['unique_name'], 'org.apps.julia-one')
        # what_is_new
        self.assertEqual(response.data['what_is_new'], 'nothing is new')
        # description_short
        self.assertEqual(response.data['description_short'],
            'a shorter description')
        # requirements
        self.assertEqual(response.data['requirements'], 'None')
        # is_private
        self.assertEqual(response.data['is_private'], True)
        # contacts
        self.assertEqual(len(response.data['contacts']), 2)
        names = []
        for c in response.data['contacts']:
            names.append(c['name'])
        self.assertTrue('me' in names)
        self.assertTrue('you' in names)
        # security_marking
        self.assertEqual(response.data['security_marking'],
            'UNCLASSIFIED')
        # listing_type
        self.assertEqual(response.data['listing_type']['title'],
            'web application')
        # icons
        self.assertEqual(response.data['small_icon']['id'], 1)
        self.assertEqual(response.data['large_icon']['id'], 2)
        self.assertEqual(response.data['banner_icon']['id'], 3)
        self.assertEqual(response.data['large_banner_icon']['id'], 4)
        # categories
        categories = []
        for c in response.data['categories']:
            categories.append(c['title'])
        self.assertTrue('Business' in categories)
        self.assertTrue('Education' in categories)
        # owners
        owners = []
        for o in response.data['owners']:
            owners.append(o['user']['username'])
        self.assertTrue('wsmith' in owners)
        self.assertTrue('julia' in owners)
        # tags
        tags = []
        for t in response.data['tags']:
            tags.append(t['name'])
        self.assertTrue('demo' in tags)
        self.assertTrue('map' in tags)
        # intents
        intents = []
        for i in response.data['intents']:
            intents.append(i['action'])
        self.assertTrue('/application/json/view' in intents)
        self.assertTrue('/application/json/edit' in intents)
        # doc_urls
        doc_urls = []
        for d in response.data['doc_urls']:
            doc_urls.append(d['url'])
        self.assertTrue('http://www.google.com/wiki' in doc_urls)
        self.assertTrue('http://www.google.com/guide' in doc_urls)
        # screenshots
        screenshots_small = []
        for s in response.data['screenshots']:
            screenshots_small.append(s['small_image']['id'])
        self.assertTrue(1 in screenshots_small)
        self.assertTrue(3 in screenshots_small)

        screenshots_large = []
        for s in response.data['screenshots']:
            screenshots_large.append(s['large_image']['id'])
        self.assertTrue(2 in screenshots_large)
        self.assertTrue(4 in screenshots_large)

        # fields that should come back with default values
        self.assertEqual(response.data['approved_date'], None)
        self.assertEqual(response.data['approval_status'],
            models.Listing.IN_PROGRESS)
        self.assertEqual(response.data['is_enabled'], True)
        self.assertEqual(response.data['is_featured'], False)
        self.assertEqual(response.data['avg_rate'], 0.0)
        self.assertEqual(response.data['total_votes'], 0)
        self.assertEqual(response.data['total_rate5'], 0)
        self.assertEqual(response.data['total_rate4'], 0)
        self.assertEqual(response.data['total_rate3'], 0)
        self.assertEqual(response.data['total_rate2'], 0)
        self.assertEqual(response.data['total_rate1'], 0)
        self.assertEqual(response.data['total_reviews'], 0)
        self.assertEqual(response.data['iframe_compatible'], True)
        self.assertEqual(response.data['required_listings'], None)
        self.assertTrue(response.data['edited_date'])

    def test_delete_listing(self):
        url = '/api/listing/1/'
        response = self._request_helper(url, 'GET', username='wsmith', status_code=200)
        self.assertFalse(response.data.get('is_deleted'))

        url = '/api/listing/1/'
        response = self._request_helper(url, 'DELETE', username='wsmith', status_code=204)

        url = '/api/listing/1/'
        response = self._request_helper(url, 'GET', username='wsmith', status_code=200)
        self.assertTrue(response.data.get('is_deleted'))

    def test_delete_listing_permission_denied(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/1/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_listing_partial(self):
        """
        This was added to catch the case where a listing that didn't previously
        have an icon was being updated, and the update method in the serializer
        was invoking instance.small_icon.id to get the old value for the
        change_details. There was no previous value, so accessing
        instance.small_icon.id raised an exception. The same problem could exist
        on any property that isn't a simple data type
        """
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/1/'

        listing = models.Listing.objects.get(id=1)
        listing.small_icon = None
        listing.large_icon = None
        listing.banner_icon = None
        listing.large_banner_icon = None
        listing.listing_type = None
        listing.save()

        # now make another change to the listing
        data = self.client.get(url, format='json').data
        data['small_icon'] = {'id': 1}
        data['large_icon'] = {'id': 2}
        data['banner_icon'] = {'id': 3}
        data['large_banner_icon'] = {'id': 4}
        data['listing_type'] = {'title': 'web application'}
        # and another update
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['edited_date'])
        self.assertEqual(response.data['small_icon']['id'], 1)
        self.assertEqual(response.data['large_icon']['id'], 2)
        self.assertEqual(response.data['banner_icon']['id'], 3)
        self.assertEqual(response.data['large_banner_icon']['id'], 4)

    def test_update_listing_full(self):
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/1/'
        title = 'julias app 2'
        data = {
            "title": title,
            "description": "description of app",
            "launch_url": "http://www.google.com/launch",
            "version_name": "2.1.8",
            "unique_name": "org.apps.julia-one",
            "what_is_new": "nothing is new",
            "description_short": "a shorter description",
            "requirements": "Many new things",
            "is_private": "true",
            "is_enabled": "false",
            "is_featured": "false",
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
            "security_marking": "SECRET",
            "listing_type": {"title": "widget"},
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
                {"name": "wiki", "url": "http://www.google.com/wiki2"},
                {"name": "guide", "url": "http://www.google.com/guide2"}
            ],
            "screenshots": [
                {"small_image": {"id": 1}, "large_image": {"id": 2}},
                {"small_image": {"id": 3}, "large_image": {"id": 4}}
            ]

        }
        # for checking Activity status later on
        old_listing_data = self.client.get(url, format='json').data
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # title
        self.assertEqual(response.data['title'], data['title'])
        # description
        self.assertEqual(response.data['description'], data['description'])
        # launch_url
        self.assertEqual(response.data['launch_url'], data['launch_url'])
        # version_name
        self.assertEqual(response.data['version_name'], data['version_name'])
        # unique_name
        self.assertEqual(response.data['unique_name'], data['unique_name'])
        # what_is_new
        self.assertEqual(response.data['what_is_new'], data['what_is_new'])
        # description_short
        self.assertEqual(response.data['description_short'], data['description_short'])
        # requirements
        self.assertEqual(response.data['requirements'], data['requirements'])
        # is_private
        self.assertEqual(response.data['is_private'], True)
        # contacts
        self.assertEqual(len(response.data['contacts']), 2)
        names = []
        for c in response.data['contacts']:
            names.append(c['name'])
        self.assertTrue('me' in names)
        self.assertTrue('you' in names)
        # security_marking
        self.assertEqual(response.data['security_marking'],
            'SECRET')
        # listing_type
        self.assertEqual(response.data['listing_type']['title'],
            'widget')
        # icons
        self.assertEqual(response.data['small_icon']['id'], 1)
        self.assertEqual(response.data['large_icon']['id'], 2)
        self.assertEqual(response.data['banner_icon']['id'], 3)
        self.assertEqual(response.data['large_banner_icon']['id'], 4)
        # categories
        categories = []
        for c in response.data['categories']:
            categories.append(c['title'])
        self.assertEqual(len(response.data['categories']), 2)
        self.assertTrue('Business' in categories)
        self.assertTrue('Education' in categories)
        # owners
        owners = []
        for o in response.data['owners']:
            owners.append(o['user']['username'])
        self.assertEqual(len(response.data['owners']), 2)
        self.assertTrue('wsmith' in owners)
        self.assertTrue('julia' in owners)
        # tags
        tags = []
        for t in response.data['tags']:
            tags.append(t['name'])
        self.assertEqual(len(response.data['tags']), 2)
        self.assertTrue('demo' in tags)
        self.assertTrue('map' in tags)
        # intents
        intents = []
        for i in response.data['intents']:
            intents.append(i['action'])
        self.assertEqual(len(response.data['intents']), 2)
        self.assertTrue('/application/json/view' in intents)
        self.assertTrue('/application/json/edit' in intents)
        # doc_urls
        doc_urls = []
        for d in response.data['doc_urls']:
            doc_urls.append(d['url'])
        self.assertEqual(len(response.data['doc_urls']), 2)
        self.assertTrue('http://www.google.com/wiki2' in doc_urls)
        self.assertTrue('http://www.google.com/guide2' in doc_urls)
        # screenshots
        screenshots_small = []
        self.assertEqual(len(response.data['screenshots']), 2)
        for s in response.data['screenshots']:
            screenshots_small.append(s['small_image']['id'])
        self.assertTrue(1 in screenshots_small)
        self.assertTrue(3 in screenshots_small)

        screenshots_large = []
        for s in response.data['screenshots']:
            screenshots_large.append(s['large_image']['id'])
        self.assertTrue(2 in screenshots_large)
        self.assertTrue(4 in screenshots_large)

        self.assertTrue(response.data['approved_date'])
        self.assertEqual(response.data['approval_status'],
            models.Listing.APPROVED)
        self.assertEqual(response.data['is_enabled'], False)
        self.assertEqual(response.data['is_featured'], False)
        self.assertEqual(response.data['avg_rate'], 3.0)
        self.assertEqual(response.data['total_votes'], 3)
        self.assertEqual(response.data['total_rate5'], 1)
        self.assertEqual(response.data['total_rate4'], 0)
        self.assertEqual(response.data['total_rate3'], 1)
        self.assertEqual(response.data['total_rate2'], 0)
        self.assertEqual(response.data['total_rate1'], 1)
        self.assertEqual(response.data['total_reviews'], 3)
        self.assertEqual(response.data['iframe_compatible'], False)
        self.assertEqual(response.data['required_listings'], None)
        self.assertTrue(response.data['edited_date'])

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #                   verify change_details
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        activity_url = url + 'activity/'
        activity_response = self.client.get(activity_url, format='json')
        activity_data = activity_response.data

        fields = ['title', 'description', 'description_short', 'version_name',
            'requirements', 'unique_name', 'what_is_new', 'launch_url',
            'is_enabled', 'is_featured', 'is_private', 'doc_urls', 'contacts',
            'screenshots', 'categories', 'owners', 'tags', 'small_icon',
            'large_icon', 'banner_icon', 'large_banner_icon', 'security_marking',
            'listing_type', 'approval_status', 'intents']

        total_found = 0
        for activity in activity_data:
            if activity['action'] == 'MODIFIED':
                for change in activity['change_details']:
                    if change['field_name'] == 'title':
                        self.assertEqual(change['new_value'], data['title'])
                        self.assertEqual(change['old_value'], old_listing_data['title'])
                        total_found += 1
                    if change['field_name'] == 'description':
                        self.assertEqual(change['new_value'], data['description'])
                        self.assertEqual(change['old_value'], old_listing_data['description'])
                        total_found += 1
                    if change['field_name'] == 'description_short':
                        self.assertEqual(change['new_value'], data['description_short'])
                        self.assertEqual(change['old_value'], old_listing_data['description_short'])
                        total_found += 1
                    if change['field_name'] == 'version_name':
                        self.assertEqual(change['new_value'], data['version_name'])
                        self.assertEqual(change['old_value'], old_listing_data['version_name'])
                        total_found += 1
                    if change['field_name'] == 'requirements':
                        self.assertEqual(change['new_value'], data['requirements'])
                        self.assertEqual(change['old_value'], old_listing_data['requirements'])
                        total_found += 1
                    if change['field_name'] == 'what_is_new':
                        self.assertEqual(change['new_value'], data['what_is_new'])
                        self.assertEqual(change['old_value'], old_listing_data['what_is_new'])
                        total_found += 1
                    if change['field_name'] == 'unique_name':
                        self.assertEqual(change['new_value'], data['unique_name'])
                        self.assertEqual(change['old_value'], old_listing_data['unique_name'])
                        total_found += 1
                    if change['field_name'] == 'launch_url':
                        self.assertEqual(change['new_value'], data['launch_url'])
                        self.assertEqual(change['old_value'], old_listing_data['launch_url'])
                        total_found += 1
                    if change['field_name'] == 'is_private':
                        self.assertEqual(change['new_value'], data['is_private'])
                        self.assertEqual(change['old_value'], model_access.bool_to_string(old_listing_data['is_private']))
                        total_found += 1
                    if change['field_name'] == 'is_featured':
                        self.assertEqual(change['new_value'], data['is_featured'])
                        self.assertEqual(change['old_value'], model_access.bool_to_string(old_listing_data['is_featured']))
                        total_found += 1
                    if change['field_name'] == 'listing_type':
                        self.assertEqual(change['new_value'], data['listing_type']['title'])
                        self.assertEqual(change['old_value'], old_listing_data['listing_type']['title'])
                        total_found += 1
                    if change['field_name'] == 'security_marking':
                        self.assertEqual(change['new_value'], data['security_marking'])
                        self.assertEqual(change['old_value'], old_listing_data['security_marking'])
                        total_found += 1
                    if change['field_name'] == 'small_icon':
                        self.assertEqual(change['new_value'], str(data['small_icon']['id']) + '.UNCLASSIFIED')
                        self.assertEqual(change['old_value'], str(old_listing_data['small_icon']['id']) + '.UNCLASSIFIED')
                        total_found += 1
                    if change['field_name'] == 'large_icon':
                        self.assertEqual(change['new_value'], str(data['large_icon']['id']) + '.UNCLASSIFIED')
                        self.assertEqual(change['old_value'], str(old_listing_data['large_icon']['id']) + '.UNCLASSIFIED')
                        total_found += 1
                    if change['field_name'] == 'banner_icon':
                        self.assertEqual(change['new_value'], str(data['banner_icon']['id']) + '.UNCLASSIFIED')
                        self.assertEqual(change['old_value'], str(old_listing_data['banner_icon']['id']) + '.UNCLASSIFIED')
                        total_found += 1
                    if change['field_name'] == 'large_banner_icon':
                        self.assertEqual(change['new_value'], str(data['large_banner_icon']['id']) + '.UNCLASSIFIED')
                        self.assertEqual(change['old_value'], str(old_listing_data['large_banner_icon']['id']) + '.UNCLASSIFIED')
                        total_found += 1
                    if change['field_name'] == 'doc_urls':
                        self.assertEqual(change['new_value'],
                            model_access.doc_urls_to_string(data['doc_urls']))
                        self.assertEqual(change['old_value'],
                            model_access.doc_urls_to_string(old_listing_data['doc_urls']))
                        total_found += 1
                    if change['field_name'] == 'screenshots':
                        self.assertEqual(change['new_value'],
                            model_access.screenshots_to_string(data['screenshots']))
                        self.assertEqual(change['old_value'],
                            model_access.screenshots_to_string(old_listing_data['screenshots']))
                        total_found += 1
                    if change['field_name'] == 'contacts':
                        self.assertEqual(change['new_value'],
                            model_access.contacts_to_string(data['contacts']))
                        self.assertEqual(change['old_value'],
                            model_access.contacts_to_string(old_listing_data['contacts']))
                        total_found += 1
                    if change['field_name'] == 'intents':
                        self.assertEqual(change['new_value'],
                            model_access.intents_to_string(data['intents']))
                        self.assertEqual(change['old_value'],
                            model_access.intents_to_string(old_listing_data['intents']))
                        total_found += 1
                    if change['field_name'] == 'categories':
                        self.assertEqual(change['new_value'],
                            model_access.categories_to_string(data['categories']))
                        self.assertEqual(change['old_value'],
                            model_access.categories_to_string(old_listing_data['categories']))
                        total_found += 1
                    if change['field_name'] == 'tags':
                        self.assertEqual(change['new_value'],
                            model_access.tags_to_string(data['tags']))
                        self.assertEqual(change['old_value'],
                            model_access.tags_to_string(old_listing_data['tags']))
                        total_found += 1
                    if change['field_name'] == 'owners':
                        self.assertEqual(change['new_value'],
                            model_access.owners_to_string(data['owners']))
                        self.assertEqual(change['old_value'],
                            model_access.owners_to_string(old_listing_data['owners']))
                        total_found += 1

        self.assertEqual(total_found, len(fields) - 2)    # (-1 for approved_status) + (-1 for is_enabled)

    def test_z_create_update(self):
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/'
        data = {
          "title": "test",
          "screenshots": [],
          "contacts": [
            {
              "name": "test1",
              "email": "test1@domain.com",
              "secure_phone": "240-544-8777",
              "contact_type": {
                "name": "Civillian"
              }
            },
            {
              "name": "test2",
              "email": "test2@domain.com",
              "secure_phone": "240-888-7477",
              "contact_type": {
                "name": "Civillian"
              }
            }
          ],
          "tags": [],
          "owners": [
            {
              "display_name": "Big Brother",
              "id": 4,
              "user": {
                "username": "bigbrother"
              }
            }
          ],
          "agency": {
            "short_name": "Miniluv",
            "title": "Ministry of Love"
          },
          "categories": [
            {
              "title": "Books and Reference"
            }
          ],
          "intents": [],
          "doc_urls": [],
          "security_marking": "UNCLASSIFIED//FOR OFFICIAL USE ONLY//ABCDE",
          "listing_type": {
            "title": "web application"
          },
          "last_activity": {
            "action": "APPROVED"
          },
          "required_listings": None
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['approval_status'], 'IN_PROGRESS')
        listing_id = response.data['id']

        data = {
          "id": listing_id,
          "title": "test",
          "description": None,
          "description_short": None,
          "screenshots": [],
          "contacts": [
            {
              "id": 4,
              "contact_type": {
                "name": "Government"
              },
              "secure_phone": "240-544-8777",
              "unsecure_phone": None,
              "email": "test1@domain.com",
              "name": "test15",
              "organization": None
            },
            {
              "id": 5,
              "contact_type": {
                "name": "Civillian"
              },
              "secure_phone": "240-888-7477",
              "unsecure_phone": None,
              "email": "test2@domain.com",
              "name": "test2",
              "organization": None
            }
          ],
          "avg_rate": 0,
          "total_votes": 0,
          "tags": [],
          "requirements": None,
          "version_name": None,
          "launch_url": None,
          "what_is_new": None,
          "owners": [
            {
              "display_name": "Big Brother",
              "id": 4,
              "user": {
                "username": "bigbrother"
              }
            }
          ],
          "agency": {
            "short_name": "Miniluv",
            "title": "Ministry of Love"
          },
          "is_enabled": True,
          "categories": [
            {
              "title": "Books and Reference"
            }
          ],
          "intents": [],
          "doc_urls": [],
          "approval_status": "IN_PROGRESS",
          "is_featured": False,
          "is_private": False,
          "security_marking": "UNCLASSIFIED//FOR OFFICIAL USE ONLY//ABCDE",
          "listing_type": {
            "title": "web application"
          },
          "unique_name": None,
          "last_activity": {
            "action": "APPROVED"
          },
          "required_listings": None
        }

        url = '/api/listing/%s/' % listing_id
        response = self.client.put(url, data, format='json')

        contacts = response.data['contacts']
        contact_types = [i['contact_type']['name'] for i in contacts]
        self.assertEqual(str(contact_types), str(['Civillian', 'Government']))

    def test_update_listing_approval_status_deny_user(self):
        # a standard user cannot update the approval_status
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/'

        data = {
            "title": 'mr jones app',
            "approval_status": "APPROVED",
            "security_marking": "UNCLASSIFIED"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['approval_status'], 'IN_PROGRESS')

        data = response.data
        data['approval_status'] = models.Listing.APPROVED
        listing_id = data['id']

        url = '/api/listing/%s/' % listing_id
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # double check that the status wasn't changed
        # TODO: listing doesn't exist?
        # url = '/api/listing/%s/' % listing_id
        # response = self.client.get(url, data, format='json')
        # self.assertEqual(response.data['approval_status'], models.Listing.IN_PROGRESS)

    def _request_helper(self, url, method, data=None, username='bigbrother', status_code=200):
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
        url = '/api/listing/%s/activity/' % app_id
        response = self._request_helper(url, 'GET', username='jones', status_code=200)

        activity_actions = [i['action'] for i in response.data]
        self.assertEqual(len(activity_actions), 1)
        action_log.insert(0, models.ListingActivity.CREATED)
        self.assertEqual(activity_actions, action_log)
        activity_agency = [i['listing']['agency'] for i in response.data]
        self.assertEquals(json.dumps(activity_agency[0]), '{"title": "Ministry of Truth", "short_name": "Minitrue"}')
        for entry in response.data:
            self.assertTrue('small_icon' in entry['listing'])

        # MODIFIED
        data['title'] = "mr jones mod app"
        url = '/api/listing/%s/' % app_id
        response = self._request_helper(url, 'PUT', data=data, username='jones', status_code=200)
        data = response.data

        # VERIFY that is was modified
        url = '/api/listing/%s/activity/' % app_id
        response = self._request_helper(url, 'GET', username='jones', status_code=200)

        activity_actions = [i['action'] for i in response.data]
        self.assertEqual(len(activity_actions), 2)
        action_log.insert(0, models.ListingActivity.MODIFIED)
        self.assertEqual(activity_actions, action_log)
        activity_agency = [i['listing']['agency'] for i in response.data]
        self.assertEquals(json.dumps(activity_agency[0]), '{"title": "Ministry of Truth", "short_name": "Minitrue"}')
        for entry in response.data:
            self.assertTrue('small_icon' in entry['listing'])

        # SUBMITTED
        data['approval_status'] = models.Listing.PENDING
        url = '/api/listing/%s/' % app_id
        response = self._request_helper(url, 'PUT', data=data, username='jones', status_code=200)

        # Verify that is was submitted
        url = '/api/listing/%s/activity/' % app_id
        response = self._request_helper(url, 'GET', username='jones', status_code=200)

        activity_actions = [i['action'] for i in response.data]
        self.assertEquals(len(activity_actions), 3)
        action_log.insert(0, models.ListingActivity.SUBMITTED)
        self.assertEqual(activity_actions, action_log)
        self.assertTrue(models.ListingActivity.SUBMITTED in activity_actions)
        activity_agency = [i['listing']['agency'] for i in response.data]
        self.assertEquals(json.dumps(activity_agency[0]), '{"title": "Ministry of Truth", "short_name": "Minitrue"}')
        for entry in response.data:
            self.assertTrue('small_icon' in entry['listing'])

        # APPROVED_ORG

        # APPROVED

        # DISABLE
        data['is_enabled'] = False
        url = '/api/listing/%s/' % app_id
        response = self._request_helper(url, 'PUT', data=data, username='jones', status_code=200)

        # Verify that it was disabled
        url = '/api/listing/%s/activity/' % app_id
        response = self._request_helper(url, 'GET', username='jones', status_code=200)
        activity_actions = [i['action'] for i in response.data]
        self.assertEquals(len(activity_actions), 4)
        action_log.insert(0, models.ListingActivity.DISABLED)
        self.assertEqual(activity_actions, action_log)
        activity_agency = [i['listing']['agency'] for i in response.data]
        self.assertEquals(json.dumps(activity_agency[0]), '{"title": "Ministry of Truth", "short_name": "Minitrue"}')
        for entry in response.data:
            self.assertTrue('small_icon' in entry['listing'])

        # ENABLED
        data['is_enabled'] = True
        url = '/api/listing/%s/' % app_id
        response = self._request_helper(url, 'PUT', data=data, username='jones', status_code=200)

        # Verify that it was enabled
        url = '/api/listing/%s/activity/' % app_id
        response = self._request_helper(url, 'GET', username='jones', status_code=200)
        activity_actions = [i['action'] for i in response.data]
        self.assertEquals(len(activity_actions), 5)
        action_log.insert(0, models.ListingActivity.ENABLED)
        self.assertEqual(activity_actions, action_log)
        activity_agency = [i['listing']['agency'] for i in response.data]
        self.assertEquals(json.dumps(activity_agency[0]), '{"title": "Ministry of Truth", "short_name": "Minitrue"}')
        for entry in response.data:
            self.assertTrue('small_icon' in entry['listing'])

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
        print('for bigbrother, got titles: %s' % titles)
        counter = 0
        for i in expected_titles:
            # Bread Basket is a private app, and bigbrother is not in that
            # organization
            if i != 'Bread Basket':
                print('checking for app %s' % i)
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

    def test_get_listings_with_query_params(self):
        """
        Supported query params: org (agency title), approval_status, enabled
        """
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/?approval_status=APPROVED&org=Ministry of Truth&enabled=true'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 5)
        # TODO: more tests

    def test_counts_in_listings(self):
        """
        Supported query params: org (agency title), approval_status, enabled
        """
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        last_item = data[-1]

        expected_item = {"counts": {
            "organizations": {
                "4": 0,
                "2": 0,
                "1": 100,
                "3": 10
                },
            "REJECTED": 0,
            "enabled": 110,
            "APPROVED_ORG": 0,
            "total": 110,
            "APPROVED": 110,
            "PENDING": 0,
            "IN_PROGRESS": 0,
            "DELETED": 0
            }
            }
        self.assertEquals(last_item, expected_item)

    def test_create_listing_with_different_agency(self):
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/'
        data = {'title': 'test app', 'security_marking': 'UNCLASSIFIED',
                'agency': {'title': 'Ministry of Plenty'}}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_listing_with_invalid_agency(self):
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/'
        data = {'title': 'test app', 'security_marking': 'UNCLASSIFIED',
            'agency': {'title': 'Ministry of NONE'}}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_listing_normal_user(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/1/rejection/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {'description': 'because it\'s not good'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reject_listing_org_steward(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/1/rejection/'
        data = {'description': 'because it\'s not good'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = '/api/listing/1/activity/'
        response = self.client.get(url, format='json')
        actions = [i['action'] for i in response.data]
        self.assertTrue('REJECTED' in actions)

        url = '/api/listing/1/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['last_activity']['action'], 'REJECTED')
        current_rejection = response.data['current_rejection']
        self.assertEqual(current_rejection['author']['user']['username'], 'wsmith')
        self.assertTrue(current_rejection['description'])
        self.assertTrue(current_rejection['author']['display_name'])
