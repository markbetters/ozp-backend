"""
Tests for listing endpoints
"""
from rest_framework import status
from rest_framework.test import APITestCase

from ozpcenter import model_access as generic_model_access
from ozpcenter import models
from ozpcenter.scripts import sample_data_generator as data_gen


class ListingReviewApiTest(APITestCase):

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

    def test_get_reviews(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        air_mail_id = models.Listing.objects.get(title='Air Mail').id
        url = '/api/listing/{0!s}/review/'.format(air_mail_id)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_review(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        air_mail_id = models.Listing.objects.get(title='Air Mail').id
        url = '/api/listing/{0!s}/review/1/'.format(air_mail_id)
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
        url = '/api/listing/{0!s}/review/'.format(air_mail_id)
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

    def test_create_review_not_found(self):
        # creating a review for an app this user cannot see should fail
        bread_basket_id = models.Listing.objects.get(title='Bread Basket').id
        user = generic_model_access.get_profile('rutherford').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/{0!s}/review/'.format(bread_basket_id)
        data = {'rate': 4, 'text': 'rutherford test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_review_no_text(self):
        # create a new review
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        air_mail_id = models.Listing.objects.get(title='Air Mail').id
        url = '/api/listing/{0!s}/review/'.format(air_mail_id)
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
        url = '/api/listing/{0!s}/review/'.format(air_mail_id)
        data = {'rate': 4, 'text': 'winston test review'}
        response = self.client.post(url, data, format='json')
        review_id = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # now update it
        url = '/api/listing/{0!s}/review/{1!s}/'.format(air_mail_id, review_id)
        data = {'rate': 4, 'text': 'winston test review'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(4, response.data['rate'])

        # test the listing/<id>/activity endpoint
        url = '/api/listing/{0!s}/activity/'.format(air_mail_id)
        response = self.client.get(url, format='json')
        activiy_actions = [i['action'] for i in response.data]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(models.ListingActivity.REVIEW_EDITED in activiy_actions)

        # try to edit a review from another user - should fail
        url = '/api/listing/{0!s}/review/1/'.format(air_mail_id)
        data = {'rate': 4, 'text': 'winston test review'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_simple_delete_review(self):
        # create a new review
        user = generic_model_access.get_profile('rutherford').user
        self.client.force_authenticate(user=user)
        air_mail_id = models.Listing.objects.get(title='Air Mail').id
        url = '/api/listing/{0!s}/review/'.format(air_mail_id)
        data = {'rate': 4, 'text': 'rutherford test review'}
        response = self.client.post(url, data, format='json')
        review_id = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # now delete it
        url = '/api/listing/{0!s}/review/{1!s}/'.format(air_mail_id, review_id)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # test the listing/<id>/activity endpoint
        url = '/api/listing/{0!s}/activity/'.format(air_mail_id)
        response = self.client.get(url, format='json')
        activiy_actions = [i['action'] for i in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(models.ListingActivity.REVIEW_DELETED in activiy_actions)

    def test_delete_review(self):
        # create a new review
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        air_mail_id = models.Listing.objects.get(title='Air Mail').id
        url = '/api/listing/{0!s}/review/'.format(air_mail_id)
        data = {'rate': 4, 'text': 'winston test review'}
        response = self.client.post(url, data, format='json')
        review_id = response.data['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # trying to delete it as a different user should fail...
        url = '/api/listing/{0!s}/review/{1!s}/'.format(air_mail_id, review_id)
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
        url = '/api/listing/{0!s}/review/'.format(listing.id)
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
        url = '/api/listing/{0!s}/review/'.format(listing.id)
        data = {'rate': 2, 'text': 'julia test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = generic_model_access.get_profile('charrington').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/{0!s}/review/'.format(listing.id)
        data = {'rate': 3, 'text': 'charrington test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/{0!s}/review/'.format(listing.id)
        data = {'rate': 4, 'text': 'jones test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = generic_model_access.get_profile('rutherford').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/{0!s}/review/'.format(listing.id)
        data = {'rate': 5, 'text': 'rutherford test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = generic_model_access.get_profile('syme').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/{0!s}/review/'.format(listing.id)
        data = {'rate': 5, 'text': 'syme test review'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        syme_review_id = response.data['id']

        # and one without a review
        user = generic_model_access.get_profile('tparsons').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/{0!s}/review/'.format(listing.id)
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
        url = '/api/listing/{0!s}/review/{1!s}/'.format(listing.id,
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
        url = '/api/listing/{0!s}/review/{1!s}/'.format(listing.id, syme_review_id)
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
