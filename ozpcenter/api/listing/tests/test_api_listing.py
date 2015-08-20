"""
Tests for listing endpoints
"""
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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

    def test_create_listing_contacts(self):
        # create a new listing with contacts
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/'
        title = 'julias app'
        data = {'title': title, "contacts": [
                {"email": "a@a.com", "secure_phone": "111-222-3434",
                    "unsecure_phone": "444-555-4545", "name": "me",
                    "contact_type": "Government"
                },
                {"email": "b@b.com", "secure_phone": "222-222-3333",
                    "unsecure_phone": "555-555-5555", "name": "you",
                    "contact_type": "Military"
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], title)
        self.assertEqual(len(response.data['contacts']), 2)
        names = []
        for c in response.data['contacts']:
            names.append(c['name'])
        self.assertTrue('me' in names)
        self.assertTrue('you' in names)




