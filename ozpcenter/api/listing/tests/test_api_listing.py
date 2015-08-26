"""
Tests for listing endpoints
"""
from copy import deepcopy
from decimal import Decimal
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
import ozpcenter.api.listing.views as views
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
        self.assertEqual(len(titles), 2)

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
        self.assertEqual(len(titles), 1)

    def test_search_type(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?type=web application'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [i['title'] for i in response.data]
        self.assertTrue('Air Mail' in titles)
        self.assertTrue(len(titles) > 7)

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
        self.assertTrue('Air Mail' in titles)
        self.assertEqual(len(titles), 1)

    def test_search_offset_limit(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listings/search/?offset=1&limit=1'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [i['title'] for i in response.data['results']]
        self.assertTrue('Bread Basket' in titles)
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
        url = '/api/listing/%s/itemComment/' % air_mail_id
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_review(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        air_mail_id = models.Listing.objects.get(title='Air Mail').id
        url = '/api/listing/%s/itemComment/1/' % air_mail_id
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
        url = '/api/listing/%s/itemComment/' % air_mail_id
        data = {'rate': 4, 'text': 'winston test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_id = response.data['id']
        new_review = models.ItemComment.objects.get(id=created_id)
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
        url = '/api/listing/%s/itemComment/' % bread_basket_id
        data = {'rate': 4, 'text': 'rutherford test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_no_text(self):
        # create a new review
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        air_mail_id = models.Listing.objects.get(title='Air Mail').id
        url = '/api/listing/%s/itemComment/' % air_mail_id
        data = {'rate': 3}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_id = response.data['id']
        new_review = models.ItemComment.objects.get(id=created_id)
        self.assertEqual(created_id, new_review.id)

    def test_update_review(self):
        """
        Also tests the listing/<id>/activity endpoint
        """
        # create a new review
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        air_mail_id = models.Listing.objects.get(title='Air Mail').id
        url = '/api/listing/%s/itemComment/' % air_mail_id
        data = {'rate': 4, 'text': 'winston test review'}
        response = self.client.post(url, data, format='json')
        comment_id = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # now update it
        url = '/api/listing/%s/itemComment/%s/' % (air_mail_id, comment_id)
        data = {'rate': 4, 'text': 'winston test review'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(4, response.data['rate'])

        # test the listing/<id>/activity endpoint
        url = '/api/listing/%s/activity/' % air_mail_id
        response = self.client.get(url, format='json')
        activiy_actions = [i['action'] for i in response.data]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(models.Action.REVIEW_EDITED in activiy_actions)

        # try to edit a comment from another user - should fail
        url = '/api/listing/%s/itemComment/1/' % air_mail_id
        data = {'rate': 4, 'text': 'winston test review'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_simple_delete_review(self):
        # create a new review
        user = generic_model_access.get_profile('rutherford').user
        self.client.force_authenticate(user=user)
        air_mail_id = models.Listing.objects.get(title='Air Mail').id
        url = '/api/listing/%s/itemComment/' % air_mail_id
        data = {'rate': 4, 'text': 'rutherford test review'}
        response = self.client.post(url, data, format='json')
        comment_id = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # now delete it
        url = '/api/listing/%s/itemComment/%s/' % (air_mail_id, comment_id)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # test the listing/<id>/activity endpoint
        url = '/api/listing/%s/activity/' % air_mail_id
        response = self.client.get(url, format='json')
        activiy_actions = [i['action'] for i in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(models.Action.REVIEW_DELETED in activiy_actions)

    def test_delete_review(self):
        # create a new review
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        air_mail_id = models.Listing.objects.get(title='Air Mail').id
        url = '/api/listing/%s/itemComment/' % air_mail_id
        data = {'rate': 4, 'text': 'winston test review'}
        response = self.client.post(url, data, format='json')
        comment_id = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # trying to delete it as a different user should fail...
        url = '/api/listing/%s/itemComment/%s/' % (air_mail_id, comment_id)
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
        self.assertEqual(listing.total_comments, 0)
        self.assertEqual(listing.total_rate1, 0)
        self.assertEqual(listing.total_rate2, 0)
        self.assertEqual(listing.total_rate3, 0)
        self.assertEqual(listing.total_rate4, 0)
        self.assertEqual(listing.total_rate5, 0)

        # add one review
        url = '/api/listing/%s/itemComment/' % listing.id
        data = {'rate': 1, 'text': 'winston test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check calculations
        listing = models.Listing.objects.get(title=title)
        self.assertEqual(listing.avg_rate, 1.0)
        self.assertEqual(listing.total_votes, 1)
        self.assertEqual(listing.total_comments, 1)
        self.assertEqual(listing.total_rate1, 1)
        self.assertEqual(listing.total_rate2, 0)
        self.assertEqual(listing.total_rate3, 0)
        self.assertEqual(listing.total_rate4, 0)
        self.assertEqual(listing.total_rate5, 0)

        # add a few more reviews
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/%s/itemComment/' % listing.id
        data = {'rate': 2, 'text': 'julia test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = generic_model_access.get_profile('charrington').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/%s/itemComment/' % listing.id
        data = {'rate': 3, 'text': 'charrington test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/%s/itemComment/' % listing.id
        data = {'rate': 4, 'text': 'jones test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = generic_model_access.get_profile('rutherford').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/%s/itemComment/' % listing.id
        data = {'rate': 5, 'text': 'rutherford test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = generic_model_access.get_profile('syme').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/%s/itemComment/' % listing.id
        data = {'rate': 5, 'text': 'syme test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        syme_comment_id = response.data['id']

        # and one without a comment
        user = generic_model_access.get_profile('tparsons').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/%s/itemComment/' % listing.id
        data = {'rate': 4}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        tparsons_comment_id = response.data['id']

        # check calculations
        listing = models.Listing.objects.get(title=title)
        # (2*5 + 2*4 + 1*3 + 1*2 + 1*1)/7 = (24)/7 = 3.429
        self.assertEqual(listing.avg_rate, Decimal('3.4'))
        self.assertEqual(listing.total_votes, 7)
        self.assertEqual(listing.total_comments, 6)
        self.assertEqual(listing.total_rate1, 1)
        self.assertEqual(listing.total_rate2, 1)
        self.assertEqual(listing.total_rate3, 1)
        self.assertEqual(listing.total_rate4, 2)
        self.assertEqual(listing.total_rate5, 2)

        # update an existing review
        user = generic_model_access.get_profile('tparsons').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/%s/itemComment/%s/' % (listing.id,
            tparsons_comment_id)
        data = {'rate': 2}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check calculations
        listing = models.Listing.objects.get(title=title)
        # (2*5 + 1*4 + 1*3 + 2*2 + 1*1)/7 = (22)/7 = 3.14
        self.assertEqual(listing.avg_rate, Decimal('3.1'))
        self.assertEqual(listing.total_votes, 7)
        self.assertEqual(listing.total_comments, 6)
        self.assertEqual(listing.total_rate1, 1)
        self.assertEqual(listing.total_rate2, 2)
        self.assertEqual(listing.total_rate3, 1)
        self.assertEqual(listing.total_rate4, 1)
        self.assertEqual(listing.total_rate5, 2)


        # delete an existing review
        user = generic_model_access.get_profile('syme').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/%s/itemComment/%s/' % (listing.id, syme_comment_id)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # check calculations
        listing = models.Listing.objects.get(title=title)
        # (1*5 + 1*4 + 1*3 + 2*2 + 1*1)/6 = (17)/6 = 2.83
        self.assertEqual(listing.avg_rate, Decimal('2.8'))
        self.assertEqual(listing.total_votes, 6)
        self.assertEqual(listing.total_comments, 5)
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
        data = {'title': title}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], title)

        # trying to create an app without a title should fail
        data = {'description': 'text here'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_listing_full(self):
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
            "access_control": {"title": "UNCLASSIFIED"},
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
        # access_control
        self.assertEqual(response.data['access_control']['title'],
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
            models.ApprovalStatus.IN_PROGRESS)
        self.assertEqual(response.data['is_enabled'], True)
        self.assertEqual(response.data['is_featured'], False)
        self.assertEqual(response.data['avg_rate'], '0.0')
        self.assertEqual(response.data['total_votes'], 0)
        self.assertEqual(response.data['total_rate5'], 0)
        self.assertEqual(response.data['total_rate4'], 0)
        self.assertEqual(response.data['total_rate3'], 0)
        self.assertEqual(response.data['total_rate2'], 0)
        self.assertEqual(response.data['total_rate1'], 0)
        self.assertEqual(response.data['total_comments'], 0)
        self.assertEqual(response.data['singleton'], False)
        self.assertEqual(response.data['required_listings'], None)

    def test_delete_listing(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/1/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_listing_permission_denied(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/1/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_listing_full(self):
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/1/'
        title = 'julias app'
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
            "access_control": {"title": "SECRET"},
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
        # access_control
        self.assertEqual(response.data['access_control']['title'],
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


        self.assertEqual(response.data['approved_date'], None)
        self.assertEqual(response.data['approval_status'],
            models.ApprovalStatus.APPROVED)
        self.assertEqual(response.data['is_enabled'], False)
        self.assertEqual(response.data['is_featured'], False)
        self.assertEqual(response.data['avg_rate'], '0.0')
        self.assertEqual(response.data['total_votes'], 0)
        self.assertEqual(response.data['total_rate5'], 0)
        self.assertEqual(response.data['total_rate4'], 0)
        self.assertEqual(response.data['total_rate3'], 0)
        self.assertEqual(response.data['total_rate2'], 0)
        self.assertEqual(response.data['total_rate1'], 0)
        self.assertEqual(response.data['total_comments'], 0)
        self.assertEqual(response.data['singleton'], False)
        self.assertEqual(response.data['required_listings'], None)


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
            'large_icon', 'banner_icon', 'large_banner_icon', 'access_control',
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
                    if change['field_name'] == 'is_enabled':
                        self.assertEqual(change['new_value'], data['is_enabled'])
                        self.assertEqual(change['old_value'], str(old_listing_data['is_enabled']).lower())
                        total_found += 1
                    if change['field_name'] == 'is_private':
                        self.assertEqual(change['new_value'], data['is_private'])
                        self.assertEqual(change['old_value'], str(old_listing_data['is_private']).lower())
                        total_found += 1
                    if change['field_name'] == 'doc_urls':
                        # self.assertEqual(change['new_value'], data['doc_urls'])
                        # self.assertEqual(change['old_value'], old_listing_data['requirements'])
                        total_found += 1

        # self.assertEqual(total_found, len(fields))
        self.assertEqual(total_found, 11)



    def test_update_listing_approval_status_deny_user(self):
        # a standard user cannot update the approval_status
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/'

        data = {
            "title": 'mr jones app',
            "approval_status": "APPROVED"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['approval_status'], 'IN_PROGRESS')

        data = response.data
        data['approval_status'] = models.ApprovalStatus.APPROVED

        url = '/api/listing/%s/' % data['id']
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # double check that the status wasn't changed
        url = '/api/listing/%s/' % data['id']
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.data['approval_status'], models.ApprovalStatus.IN_PROGRESS)

    def test_listing_activities(self):
        # CREATED
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/'

        data = {
            "title": 'mr jones app'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        app_id = response.data['id']
        data = response.data

        url = '/api/listing/%s/activity/' % app_id
        response = self.client.get(url, format='json')
        activity_actions = [i['action'] for i in response.data]
        self.assertTrue(len(activity_actions), 1)
        self.assertTrue(activity_actions[0], 'CREATED')

        # MODIFIED
        url = '/api/listing/%s/' % app_id
        response = self.client.put(url, data, format='json')

        url = '/api/listing/%s/activity/' % app_id
        response = self.client.get(url, format='json')
        activity_actions = [i['action'] for i in response.data]
        self.assertTrue(len(activity_actions), 2)
        print('activiy_actions: %s' % activity_actions)
        self.assertTrue(models.Action.MODIFIED in activity_actions)

        # SUBMITTED


        # APPROVED_ORG

        # APPROVED

        # ENABLED

        # DISABLED









