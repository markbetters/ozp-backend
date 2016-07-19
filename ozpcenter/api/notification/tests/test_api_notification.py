"""
Tests for notification endpoints
"""
from unittest import skip
import datetime
import pytz

from rest_framework import status
from rest_framework.test import APITestCase

from ozpcenter import model_access as generic_model_access
from ozpcenter.scripts import sample_data_generator as data_gen
from ozpcenter.api.library.tests.test_api_library import _create_create_bookmark


def _import_bookmarks(test_case_instance, username, bookmark_notification_id, status_code=201):
    user = generic_model_access.get_profile(username).user
    test_case_instance.client.force_authenticate(user=user)
    url = '/api/self/library/import_bookmarks/'
    data = {'bookmark_notification_id': bookmark_notification_id}
    response = test_case_instance.client.post(url, data, format='json')

    if response:
        if status_code == 201:
            test_case_instance.assertEqual(response.status_code, status.HTTP_201_CREATED)
        elif status_code == 400:
            test_case_instance.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        else:
            raise Exception('status code is not supported')

    return response


class NotificationApiTest(APITestCase):

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

    def test_get_self_notification(self):
        # test authorized user
        url = '/api/self/notification/'
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for current_notification in response.data:
            self.assertIn('id', current_notification)
            self.assertIn('created_date', current_notification)
            self.assertIn('expires_date', current_notification)
            self.assertIn('message', current_notification)
            self.assertIn('author', current_notification)
            self.assertIn('listing', current_notification)
            self.assertIn('agency', current_notification)
            self.assertIn('notification_type', current_notification)
            self.assertIn('peer', current_notification)

    def test_get_self_notification_unauthorized(self):
        url = '/api/self/notification/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_self_notification_ordering(self):
        url = '/api/self/notification/'
        # get default
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        default_ids = [record['id'] for record in response.data]

        self.assertEqual(default_ids, [5, 2, 1])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = '/api/self/notification/?ordering=-created_date'
        # get reversed order
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        reverse_order_ids = [record['id'] for record in response.data]

        self.assertEqual(reverse_order_ids, default_ids)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = '/api/self/notification/?ordering=created_date'
        # get ascending order
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        order_ids = [record['id'] for record in response.data]

        self.assertEqual(reverse_order_ids, list(reversed(order_ids)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dismiss_self_notification(self):
        url = '/api/self/notification/'
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        notification_ids = []
        for i in response.data:
            notification_ids.append(i['id'])

        self.assertEqual(3, len(notification_ids))

        # now dismiss the first notification
        dismissed_notification_id = notification_ids[0]
        url = url + str(dismissed_notification_id) + '/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # now get our notifications again, make sure the one was removed
        url = '/api/self/notification/'
        response = self.client.get(url, format='json')
        notification_ids = []
        for i in response.data:
            notification_ids.append(i['id'])

        self.assertEqual(2, len(notification_ids))
        self.assertTrue(notification_ids[0] != dismissed_notification_id)

    def test_get_pending_notifications(self):
        url = '/api/notifications/pending/'
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expires_at = [i['expires_date'] for i in response.data]
        self.assertTrue(len(expires_at) > 1)
        now = datetime.datetime.now(pytz.utc)
        for i in expires_at:
            test_time = datetime.datetime.strptime(i,
                "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
            self.assertTrue(test_time > now)

    def test_get_pending_notifications_user_unauthorized(self):
        url = '/api/notifications/pending/'
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_all_pending_notifications_listing_filter(self):
        url = '/api/notifications/pending/?listing=1'
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [i['id'] for i in response.data]

        self.assertTrue(ids, [1])
        expires_at = [i['expires_date'] for i in response.data]
        self.assertTrue(len(expires_at) == 1)
        now = datetime.datetime.now(pytz.utc)
        for i in expires_at:
            test_time = datetime.datetime.strptime(i,
                "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
            self.assertTrue(test_time > now)

    def test_all_pending_notifications_listing_filter_user_unauthorized(self):
        url = '/api/notifications/pending/?listing=1'
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_expired_notifications(self):
        url = '/api/notifications/expired/'
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expires_at = [i['expires_date'] for i in response.data]
        self.assertTrue(len(expires_at) > 1)
        now = datetime.datetime.now(pytz.utc)
        for i in expires_at:
            test_time = datetime.datetime.strptime(i,
                "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
            self.assertTrue(test_time < now)

    def test_get_expired_notifications_user_unauthorized(self):
        url = '/api/notifications/expired/'
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # TODO should work when data script gets refactored (rivera 20160620)
    @skip("should work when data script gets refactored (rivera 20160620)")
    def test_all_expired_notifications_listing_filter(self):
        url = '/api/notifications/expired/?listing=1'
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [i['id'] for i in response.data]

        self.assertTrue(ids, [1])
        expires_at = [i['expires_date'] for i in response.data]
        self.assertTrue(len(expires_at) == 1)
        now = datetime.datetime.now(pytz.utc)
        for i in expires_at:
            test_time = datetime.datetime.strptime(i,
                "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
            self.assertTrue(test_time < now)

    def test_all_expired_notifications_listing_filter_user_unauthorized(self):
        url = '/api/notifications/expired/?listing=1'
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # TODO: test_all_notifications_listing_filter (rivera 20160617)

    def test_create_system_notification(self):
        url = '/api/notification/'
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        data = {'expires_date': '2016-09-01T15:45:55.322421Z',
                'message': 'a simple test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'a simple test')
        self.assertEqual(response.data['notification_type'], 'SYSTEM')

    def test_create_system_notification_unauthorized_user(self):
        # test unauthorized user - only org stewards and above can create
        url = '/api/notification/'
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        data = {'expires_date': '2016-09-01T15:45:55.322421Z',
                'message': 'a simple test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_system_notification(self):
        url = '/api/notification/1/'
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now)}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_system_notification_unauthorized_user(self):
        url = '/api/notification/1/'
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now)}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # TODO below test should work when permission gets refactored (rivera 20160620)
    @skip("should work permissions gets refactored (rivera 20160620)")
    def test_update_system_notification_unauthorized_org_steward(self):
        url = '/api/notification/1/'
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now)}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_listing_notification_app_mall_steward(self):
        url = '/api/notification/'
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        now = datetime.datetime.now(pytz.utc)

        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {
            'id': 1
            }}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'a simple listing test')
        self.assertEqual(response.data['notification_type'], 'LISTING')
        self.assertEqual(response.data['listing']['id'], 1)
        self.assertEqual(response.data['agency'], None)
        self.assertTrue('expires_date' in data)

    def test_create_listing_notification_app_mall_steward_invalid_format(self):
        url = '/api/notification/'
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        now = datetime.datetime.now(pytz.utc)

        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {
            'invalid': 1
            }}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ['Valid Listing ID is required'])

    def test_create_listing_notification_app_mall_steward_invalid_id(self):
        url = '/api/notification/'
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        now = datetime.datetime.now(pytz.utc)

        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {
            'id': -1
            }}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ['Could not find listing'])

    def test_create_listing_agency_notification_app_mall_steward_invalid(self):
        url = '/api/notification/'
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        now = datetime.datetime.now(pytz.utc)

        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {
            'id': 1
            },
            'agency': {
            'id': 1
            }}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ["Notifications can only be one type. Input: ['listing', 'agency']"])

    def test_create_listing_notification_org_steward(self):
        url = '/api/notification/'
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        now = datetime.datetime.now(pytz.utc)

        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {
            'id': 1
            }}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'a simple listing test')
        self.assertEqual(response.data['notification_type'], 'LISTING')
        self.assertEqual(response.data['listing']['id'], 1)
        self.assertEqual(response.data['agency'], None)
        self.assertTrue('expires_date' in data)

    def test_create_listing_notification_org_steward_invalid_format(self):
        url = '/api/notification/'
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        now = datetime.datetime.now(pytz.utc)

        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {
            'invalid': 1
            }}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ["Valid Listing ID is required"])

    def test_create_listing_notification_org_steward_invalid_id(self):
        url = '/api/notification/'
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        now = datetime.datetime.now(pytz.utc)

        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {
            'id': -1
            }}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ["Could not find listing"])

    # TODO: test_create_listing_notification_org_steward_invalid (rivera 20160617)
    # TODO: test_create_listing_notification_user_unauthorized (rivera 20160617)

    def test_create_agency_notification_app_mall_steward(self):
        url = '/api/notification/'
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        now = datetime.datetime.now(pytz.utc)

        data = {'expires_date': str(now),
                'message': 'A Simple Agency Test',
                'agency': {
            'id': 1
            }}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'A Simple Agency Test')
        self.assertEqual(response.data['notification_type'], 'AGENCY')
        self.assertEqual(response.data['agency']['id'], 1)
        self.assertEqual(response.data['listing'], None)
        self.assertTrue('expires_date' in data)

    def test_create_agency_notification_app_mall_steward_invalid_format(self):
        url = '/api/notification/'
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        now = datetime.datetime.now(pytz.utc)

        data = {'expires_date': str(now),
                'message': 'a simple agency test',
                'agency': {
            'invalid': 1
            }}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ['Valid Agency ID is required'])

    def test_create_agency_notification_app_mall_steward_invalid_id(self):
        url = '/api/notification/'
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        now = datetime.datetime.now(pytz.utc)

        data = {'expires_date': str(now),
                'message': 'a simple agency test',
                'agency': {
            'id': -1
            }}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ['Could not find agency'])

    # TODO: test_create_agency_notification_org_steward (rivera 20160617)
    # TODO: test_create_agency_notification_org_steward_invalid (rivera 20160617)
    # TODO: test_create_agency_notification_user_unauthorized (rivera 20160617)

    def test_create_peer_notification_app_mall_steward(self):
        url = '/api/notification/'
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        now = datetime.datetime.now(pytz.utc)

        data = {"expires_date": str(now),
                "message": "A Simple Peer to Peer Notification",
                "peer": {
                    "user": {
                      "username": "jones"
                    }
            }}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'A Simple Peer to Peer Notification')
        self.assertEqual(response.data['notification_type'], 'PEER')
        self.assertEqual(response.data['agency'], None)
        self.assertEqual(response.data['listing'], None)
        self.assertEqual(response.data['peer'], {'user': {'username': 'jones'}})
        self.assertTrue('expires_date' in data)

    @skip("should work when data script gets refactored (rivera 20160620)")
    def test_create_peer_bookmark_notification_app_mall_steward(self):
        url = '/api/notification/'
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        now = datetime.datetime.now(pytz.utc)

        data = {"expires_date": str(now),
                "message": "A Simple Peer to Peer Notification",
                "peer": {
                    "user": {
                      "username": "jones"
                    },
                    "folder_name": "folder"
            }}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'A Simple Peer to Peer Notification')
        self.assertEqual(response.data['notification_type'], 'PEER')
        self.assertEqual(response.data['agency'], None)
        self.assertEqual(response.data['listing'], None)
        self.assertTrue('expires_date' in data)

        # eval({
        #     'request': {
        #         'uri': '/api/notification/',
        #         'user': 'bigbrother',
        #         'action': 'POST',
        #         'data': {
        #             "expires_date": datetime.datetime.now(pytz.utc),
        #             "message": "A Simple Peer to Peer Notification",
        #             "peer": {
        #                 "user": {
        #                     "username": "jones"
        #                 },
        #                 "folder_name": "folder"
        #             }
        #         }
        #     },
        #     'response': {
        #         'status_code[eq]': 201,
        #         'd.message[eq]': 'A Simple Peer to Peer Notification',
        #         'd.notification_type[eq]': 'PEER',
        #         'd.agency[eq],d.listing[eq]': None,
        #         'd.expires_date[ex]': True
        #     }
        # })

    # TODO test_create_peer_notification_invalid (rivera 20160617)
    # TODO test_create_peer_bookmark_notification (rivera 20160617)

    def test_create_peer_bookmark_notification_integration(self):
        """
        test_create_peer_bookmark_notification_integration
        """
        # Listing ID: 1, 2, 3, 4
        # wsmith (minitrue, stewarded_orgs: minitrue)
        # julia (minitrue, stewarded_orgs: minitrue, miniluv)
        # bigbrother2 - minitrue
        response = _create_create_bookmark(self, 'wsmith', 3, folder_name='foldername1', status_code=201)
        self.assertEqual(response.data['listing']['id'], 3)

        response = _create_create_bookmark(self, 'wsmith', 4, folder_name='foldername1', status_code=201)
        self.assertEqual(response.data['listing']['id'], 4)

        # Compare Notifications for users
        usernames_list = {'wsmith': [1, 2, 5],
                          'julia': [1, 2],
                          'jones': [1, 2],
                          'bigbrother': [1, 2]}

        for username, ids_list in usernames_list.items():
            url = '/api/self/notification/'
            user = generic_model_access.get_profile(username).user
            self.client.force_authenticate(user=user)
            response = self.client.get(url, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            before_notification_ids = sorted([entry.get('id') for entry in response.data])
            self.assertEqual(before_notification_ids, ids_list)

        # Compare Library for users
        usernames_list = {'wsmith': [1, 2, 3, 4],
                          'julia': [],
                          'jones': [],
                          'bigbrother': []}

        for username, ids_list in usernames_list.items():
            url = '/api/self/library/'
            user = generic_model_access.get_profile(username).user
            self.client.force_authenticate(user=user)
            response = self.client.get(url, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            before_notification_ids = sorted([entry.get('id') for entry in response.data])
            self.assertEqual(before_notification_ids, ids_list, 'Comparing Library for {}'.format(username))

        # Create Bookmark
        response = _create_create_bookmark(self, 'bigbrother', 4, folder_name='foldername2', status_code=201)
        self.assertEqual(response.data['listing']['id'], 4)

        # Compare Library for users
        usernames_list = {'wsmith': [1, 2, 3, 4],
                          'julia': [],
                          'jones': [],
                          'bigbrother': [5]}

        for username, ids_list in usernames_list.items():
            url = '/api/self/library/'
            user = generic_model_access.get_profile(username).user
            self.client.force_authenticate(user=user)
            response = self.client.get(url, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            before_notification_ids = sorted([entry.get('id') for entry in response.data])
            self.assertEqual(before_notification_ids, ids_list, 'Comparing Library for {}'.format(username))

        # Create Bookmark Notification
        bookmark_notification_ids = []

        for i in range(3):
            url = '/api/notification/'
            user = generic_model_access.get_profile('wsmith').user
            self.client.force_authenticate(user=user)
            now = datetime.datetime.now(pytz.utc) + datetime.timedelta(days=5)

            data = {'expires_date': str(now),
                    'message': 'A Simple Peer to Peer Notification',
                    'peer': {
                        'user': {
                          'username': 'julia',
                        },
                        'folder_name': 'foldername1'
                }}

            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['message'], 'A Simple Peer to Peer Notification')
            self.assertEqual(response.data['notification_type'], 'PEER.BOOKMARK')
            self.assertEqual(response.data['agency'], None)
            self.assertEqual(response.data['listing'], None)
            peer_data = {'user': {'username': 'julia'}, 'folder_name': 'foldername1', '_bookmark_listing_ids': [3, 4]}
            self.assertEqual(response.data['peer'], peer_data)
            self.assertTrue('expires_date' in data)

            bookmark_notification_ids.append(response.data['id'])

            # Compare Notifications for users
            usernames_list = {'wsmith': [1, 2, 5],
                              'julia': [1, 2] + bookmark_notification_ids,
                              'jones': [1, 2],
                              'bigbrother': [1, 2]}

            for username, ids_list in usernames_list.items():
                url = '/api/self/notification/'
                user = generic_model_access.get_profile(username).user
                self.client.force_authenticate(user=user)
                response = self.client.get(url, format='json')
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                before_notification_ids = sorted([entry.get('id') for entry in response.data])
                self.assertEqual(before_notification_ids, ids_list)

        bookmark_notification1_id = bookmark_notification_ids[0]

        # Import Bookmarks
        _import_bookmarks(self, 'julia', bookmark_notification1_id, status_code=201)

        # Compare Library for users
        usernames_list = {'wsmith': [1, 2, 3, 4],
                          'julia': [6, 7],
                          'jones': [],
                          'bigbrother': [5]}

        for username, ids_list in usernames_list.items():
            url = '/api/self/library/'
            user = generic_model_access.get_profile(username).user
            self.client.force_authenticate(user=user)
            response = self.client.get(url, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            before_notification_ids = sorted([entry.get('id') for entry in response.data])
            self.assertEqual(before_notification_ids, ids_list, 'Comparing Library for {}'.format(username))

        # Compare Notifications for users
        usernames_list = {'wsmith': [1, 2, 5],
                          'julia': [1, 2] + bookmark_notification_ids[1:],
                          'jones': [1, 2],
                          'bigbrother': [1, 2]}

        for username, ids_list in usernames_list.items():
            url = '/api/self/notification/'
            user = generic_model_access.get_profile(username).user
            self.client.force_authenticate(user=user)
            response = self.client.get(url, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            before_notification_ids = sorted([entry.get('id') for entry in response.data])
            self.assertEqual(before_notification_ids, ids_list)

    def test_delete_system_notification_apps_mall_steward(self):
        url = '/api/notification/1/'
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # eval({
        #     'request': {
        #         'uri': '/api/notification/1/',
        #         'user': 'bigbrother',
        #         'action': 'DELETE',
        #     },
        #     'response': {
        #         'status_code[eq]': 204,
        #     }
        # })

    # TODO below test should work when permission gets refactored (rivera 20160620)
    @skip("should work when permission gets refactored (rivera 20160620)")
    def test_delete_system_notification_org_steward(self):
        url = '/api/notification/1/'
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_system_notification_user_unauthorized(self):
        url = '/api/notification/1/'
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
