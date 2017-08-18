"""
Tests for library endpoints (listings in a user's library)
"""
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from ozpcenter import model_access as generic_model_access
from ozpcenter.scripts import sample_data_generator as data_gen


def _edit_listing(test_case_instance, id, input_data, default_user='bigbrother'):
    """
    Helper Method to modify a listing

    Args:
        test_case_instance
        id
        input_data
        default_user(optional)

    Return:
        response
    """
    user = generic_model_access.get_profile(default_user).user
    test_case_instance.client.force_authenticate(user=user)
    url = '/api/listing/{0!s}/'.format(id)
    # GET Listing
    data = test_case_instance.client.get(url, format='json').data

    for current_key in input_data:
        if current_key in data:
            data[current_key] = input_data[current_key]

    # PUT the Modification
    response = test_case_instance.client.put(url, data, format='json')
    test_case_instance.assertEqual(response.status_code, status.HTTP_200_OK)
    return response


def _create_create_bookmark(test_case_instance, username, listing_id, folder_name=None, status_code=200):
    """
    Create Bookmark Helper Function

    Args:
        test_case_instance
        username
        listing_id
        folder_name(optional)
        status_code

    Returns:
        response
    """
    user = generic_model_access.get_profile(username).user
    test_case_instance.client.force_authenticate(user=user)

    data = {'listing': {'id': listing_id}, 'folder': folder_name}
    url = '/api/self/library/'
    response = test_case_instance.client.post(url, data, format='json')

    if response:
        if status_code == 201:
            test_case_instance.assertEqual(response.status_code, status.HTTP_201_CREATED)
        elif status_code == 400:
            test_case_instance.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        else:
            raise Exception('status code is not supported')

    return response


@override_settings(ES_ENABLED=False)
class LibraryApiTest(APITestCase):

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

    def test_get_library(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/library/'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_library(self):
        """
        POST to /self/library
        """
        # Listing is Enabled
        response = _create_create_bookmark(self, 'wsmith', 1, folder_name='', status_code=201)
        self.assertEqual(response.data['listing']['id'], 1)

        # Disable Listing
        _edit_listing(self, 1, {'is_enabled': False}, 'wsmith')

        # POST to /self/library after listing disabled
        response = _create_create_bookmark(self, 'wsmith', 1, folder_name='', status_code=400)

        # Enabled Listing
        _edit_listing(self, 1, {'is_enabled': True}, 'wsmith')
        # POST to /self/library after listing disabled
        response = _create_create_bookmark(self, 'wsmith', 1, folder_name='', status_code=201)
        self.assertEqual(response.data['listing']['id'], 1)

    def test_get_library_list(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/library/'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(5, len(response.data))
        self.assertIn('listing', response.data[0])
        self.assertIn('id', response.data[0]['listing'])
        self.assertIn('title', response.data[0]['listing'])
        self.assertIn('unique_name', response.data[0]['listing'])
        self.assertIn('folder', response.data[0])

    def test_get_library_self_when_listing_disabled_enabled(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/library/'
        response = self.client.get(url, format='json')

        listing_ids = [record['listing']['id'] for record in response.data]
        first_listing_id = listing_ids[0]  # Should be 2
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(listing_ids, [11, 1, 112, 113, 114], 'Comparing Ids #1')

        # Get Library for current user after listing was disabled
        _edit_listing(self, first_listing_id, {'is_enabled': False})

        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/library/'
        response = self.client.get(url, format='json')

        listing_ids = [record['listing']['id'] for record in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(listing_ids, [1, 112, 113, 114], 'Comparing Ids #2')

        # Get Library for current user after listing was Enable
        _edit_listing(self, first_listing_id, {'is_enabled': True})

        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/library/'
        response = self.client.get(url, format='json')

        listing_ids = [record['listing']['id'] for record in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(listing_ids, [11, 1, 112, 113, 114], 'Comparings Ids #3')

    def test_get_library_list_listing_type(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/library/?type=Web Application'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(5, len(response.data))
        self.assertIn('listing', response.data[0])
        self.assertIn('id', response.data[0]['listing'])
        self.assertIn('title', response.data[0]['listing'])
        self.assertIn('unique_name', response.data[0]['listing'])
        self.assertIn('folder', response.data[0])

    def test_get_library_list_listing_type_empty(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/library/?type=widget'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data))

    def test_get_library_pk(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/library/1/'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('listing', response.data)
        self.assertIn('id', response.data['listing'])
        self.assertIn('title', response.data['listing'])
        self.assertIn('unique_name', response.data['listing'])
        self.assertIn('folder', response.data)

    def test_update_library(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/library/'
        response = self.client.get(url, format='json')

        put_data = []
        position_count = 0

        for i in response.data:
            position_count = position_count + 1

            data = {'id': i['id'],
                    'folder': 'test',
                    'listing': {'id': i['listing']['id']},
                    'position': position_count
                    }
            put_data.append(data)

        url = '/api/self/library/update_all/'
        response = self.client.put(url, put_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
