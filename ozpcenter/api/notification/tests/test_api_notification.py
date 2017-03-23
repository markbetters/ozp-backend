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
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/notification/'
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
        # Get default
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/notification/'
        response = self.client.get(url, format='json')

        default_ids = [record['id'] for record in response.data]
        self.assertEqual(default_ids, [118, 117, 116, 15, 5, 2, 1])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get reversed order
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/notification/?ordering=-created_date'
        response = self.client.get(url, format='json')

        reverse_order_ids = [record['id'] for record in response.data]
        self.assertEqual(reverse_order_ids, default_ids)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get ascending order
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/notification/?ordering=created_date'
        response = self.client.get(url, format='json')

        order_ids = [record['id'] for record in response.data]
        self.assertEqual(reverse_order_ids, list(reversed(order_ids)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dismiss_self_notification(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/notification/'
        response = self.client.get(url, format='json')
        notification_ids = []
        for i in response.data:
            notification_ids.append([i['id'], ''.join(i['message'].split())])

        # New
        [[16, 'BreadBasketupdatenextweek(12)'],
         [15, 'Skybox1updatenextweek(11)'],
         [13, 'AirMailupdatenextweek(9)'],
         [9, 'Skybox3updatenextweek(5)'],
         [8, 'Skybox2updatenextweek(4)'],
         [7, 'Skybox1updatenextweek(3)'],
         [6, 'AirMailupdatenextweek(2)'],
         [5, 'BreadBasketupdatenextweek(1)'],
         [2, 'Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B'],
         [1, 'Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z']]

        self.assertEqual(100, len(notification_ids))

        # now dismiss the first notification
        dismissed_notification_id = notification_ids[0][0]
        url = url + str(dismissed_notification_id) + '/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # now get our notifications again, make sure the one was removed
        url = '/api/self/notification/'
        response = self.client.get(url, format='json')
        notification_ids = []
        for i in response.data:
            notification_ids.append([i['id'], ''.join(i['message'].split())])

        self.assertEqual(6, len(notification_ids))
        self.assertTrue(notification_ids[0][0] != dismissed_notification_id)

    def test_get_pending_notifications(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/notifications/pending/'
        response = self.client.get(url, format='json')

        expires_at = [i['expires_date'] for i in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(expires_at) > 1)
        now = datetime.datetime.now(pytz.utc)
        for i in expires_at:
            test_time = datetime.datetime.strptime(i,
                "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
            self.assertTrue(test_time > now)

    def test_get_pending_notifications_user_unauthorized(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)

        url = '/api/notifications/pending/'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_all_pending_notifications_listing_filter(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        url = '/api/notifications/pending/?listing=1'
        response = self.client.get(url, format='json')

        ids = [i['id'] for i in response.data]
        expires_at = [i['expires_date'] for i in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ids, [1])
        self.assertTrue(len(expires_at) == 1)
        now = datetime.datetime.now(pytz.utc)
        for i in expires_at:
            test_time = datetime.datetime.strptime(i,
                "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
            self.assertTrue(test_time > now)

    def test_all_pending_notifications_listing_filter_user_unauthorized(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)

        url = '/api/notifications/pending/?listing=1'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_expired_notifications(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/notifications/expired/'
        response = self.client.get(url, format='json')

        expires_at = [i['expires_date'] for i in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(expires_at) > 1)
        now = datetime.datetime.now(pytz.utc)
        for i in expires_at:
            test_time = datetime.datetime.strptime(i,
                "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
            self.assertTrue(test_time < now)

    def test_get_expired_notifications_user_unauthorized(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)

        url = '/api/notifications/expired/'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # TODO should work when data script gets refactored (rivera 20160620)
    @skip("should work when data script gets refactored (rivera 20160620)")
    def test_all_expired_notifications_listing_filter(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        url = '/api/notifications/expired/?listing=1'
        response = self.client.get(url, format='json')

        ids = [i['id'] for i in response.data]
        expires_at = [i['expires_date'] for i in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ids, [1])
        self.assertTrue(len(expires_at) == 1)
        now = datetime.datetime.now(pytz.utc)
        for i in expires_at:
            test_time = datetime.datetime.strptime(i,
                "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
            self.assertTrue(test_time < now)

    def test_all_expired_notifications_listing_filter_user_unauthorized(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)

        url = '/api/notifications/expired/?listing=1'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # TODO: test_all_notifications_listing_filter (rivera 20160617)

    def test_create_system_notification(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        data = {'expires_date': '2016-09-01T15:45:55.322421Z',
                'message': 'a simple test'}

        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'a simple test')
        self.assertEqual(response.data['notification_type'], 'system')

    def test_create_system_notification_unauthorized_user(self):
        # test unauthorized user - only org stewards and above can create
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)

        data = {'expires_date': '2016-09-01T15:45:55.322421Z',
                'message': 'a simple test'}
        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_system_notification(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now)}
        url = '/api/notification/1/'
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # TODO: Verify expires_date

    def test_update_system_notification_unauthorized_user(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now)}
        url = '/api/notification/1/'
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # TODO below test should work when permission gets refactored (rivera 20160620)
    @skip("should work permissions gets refactored (rivera 20160620)")
    def test_update_system_notification_unauthorized_org_steward(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now)}
        url = '/api/notification/1/'
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_listing_notification_app_mall_steward(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {
            'id': 1
            }}
        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'a simple listing test')
        self.assertEqual(response.data['notification_type'], 'listing')
        self.assertEqual(response.data['listing']['id'], 1)
        self.assertEqual(response.data['agency'], None)
        self.assertTrue('expires_date' in data)

    def test_create_listing_notification_app_mall_steward_invalid_format(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {'invalid': 1}
                }

        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ['Valid Listing ID is required'])

    def test_create_listing_notification_app_mall_steward_invalid_id(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {'id': -1}
                }

        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ['Could not find listing'])

    def test_create_listing_agency_notification_app_mall_steward_invalid(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {'id': 1},
                'agency': {'id': 1}
                }

        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ["Notifications can only be one type. Input: ['listing', 'agency']"])

    def test_create_listing_notification_org_steward(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {'id': 1}
                }

        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'a simple listing test')
        self.assertEqual(response.data['notification_type'], 'listing')
        self.assertEqual(response.data['listing']['id'], 1)
        self.assertEqual(response.data['agency'], None)
        self.assertTrue('expires_date' in data)

    def test_create_listing_notification_org_steward_invalid_format(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {'invalid': 1}
                }

        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ["Valid Listing ID is required"])

    def test_create_listing_notification_org_steward_invalid_id(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now),
                'message': 'a simple listing test',
                'listing': {'id': -1}
                }

        url = '/api/notification/'
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
                'agency': {'id': 1}
                }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'A Simple Agency Test')
        self.assertEqual(response.data['notification_type'], 'agency')
        self.assertEqual(response.data['agency']['id'], 1)
        self.assertEqual(response.data['listing'], None)
        self.assertTrue('expires_date' in data)

    def test_create_agency_notification_app_mall_steward_invalid_format(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now),
                'message': 'a simple agency test',
                'agency': {'invalid': 1}
                }
        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ['Valid Agency ID is required'])

    def test_create_agency_notification_app_mall_steward_invalid_id(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now),
                'message': 'a simple agency test',
                'agency': {'id': -1}
                }
        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ['Could not find agency'])

    # TODO: test_create_agency_notification_org_steward (rivera 20160617)
    # TODO: test_create_agency_notification_org_steward_invalid (rivera 20160617)
    # TODO: test_create_agency_notification_user_unauthorized (rivera 20160617)

    def test_create_peer_notification_app_mall_steward(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {"expires_date": str(now),
                "message": "A Simple Peer to Peer Notification",
                "peer": {
                    "user": {
                      "username": "jones"
                    }}
                }

        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'A Simple Peer to Peer Notification')
        self.assertEqual(response.data['notification_type'], 'peer')
        self.assertEqual(response.data['agency'], None)
        self.assertEqual(response.data['listing'], None)
        self.assertEqual(response.data['peer'], {'user': {'username': 'jones'}})
        self.assertTrue('expires_date' in data)

    @skip("should work when data script gets refactored (rivera 20160620)")
    def test_create_peer_bookmark_notification_app_mall_steward(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        now = datetime.datetime.now(pytz.utc)
        data = {"expires_date": str(now),
                "message": "A Simple Peer to Peer Notification",
                "peer": {
                    "user": {
                      "username": "jones"
                    },
                    "folder_name": "folder"}
                }
        url = '/api/notification/'
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'A Simple Peer to Peer Notification')
        self.assertEqual(response.data['notification_type'], 'peer_bookmark')
        self.assertEqual(response.data['agency'], None)
        self.assertEqual(response.data['listing'], None)
        self.assertTrue('expires_date' in data)

    # TODO test_create_peer_notification_invalid (rivera 20160617)
    # TODO test_create_peer_bookmark_notification (rivera 20160617)

    def test_create_peer_bookmark_notification_integration(self):
        """
        test_create_peer_bookmark_notification_integration
        Listing ID: 1, 2, 3, 4
        wsmith (minitrue, stewarded_orgs: minitrue)
        julia (minitrue, stewarded_orgs: minitrue, miniluv)
        bigbrother2 - minitrue
        """
        response = _create_create_bookmark(self, 'wsmith', 3, folder_name='foldername1', status_code=201)
        self.assertEqual(response.data['listing']['id'], 3)

        response = _create_create_bookmark(self, 'wsmith', 4, folder_name='foldername1', status_code=201)
        self.assertEqual(response.data['listing']['id'], 4)

        # Compare Notifications for users
        usernames_list = {'wsmith': ['listing-Skybox3updatenextweek',
                                     'listing-Skybox2updatenextweek',
                                     'listing-Skybox1updatenextweek',
                                     'listing-BreadBasketupdatenextweek',
                                     'listing-AirMail3updatenextweek',
                                     'listing-AirMail2updatenextweek',
                                     'listing-AirMailupdatenextweek',
                                     'system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                                     'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z'],
                          'julia': ['system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                                    'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z'],
                          'jones': ['system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                                   'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z'],
                          'bigbrother': ['listing-BreadBasketupdatenextweek',
                                         'system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                                         'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z']
                          }

        for username, ids_list in usernames_list.items():
            user = generic_model_access.get_profile(username).user
            self.client.force_authenticate(user=user)

            url = '/api/self/notification/'
            response = self.client.get(url, format='json')

            before_notification_ids = ['{}-{}'.format(entry.get('notification_type'), ''.join(entry.get('message').split())) for entry in response.data]
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(before_notification_ids, ids_list, 'Checking for {}'.format(username))

        # Compare Library for users
        usernames_list = {'wsmith': ['Bread Basket-None',
                                     'Air Mail-None',
                                     'Skybox 1-None',
                                     'Skybox 2-None',
                                     'Skybox 3-None',
                                     'Air Mail 2-foldername1',
                                     'Air Mail 3-foldername1'],
                          'julia': [],
                          'jones': [],
                          'bigbrother': ['Bread Basket-None']}

        for username, ids_list in usernames_list.items():
            user = generic_model_access.get_profile(username).user
            self.client.force_authenticate(user=user)

            url = '/api/self/library/'
            response = self.client.get(url, format='json')
            before_notification_ids = ['{}-{}'.format(entry['listing']['title'], entry['folder']) for entry in response.data]
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(before_notification_ids, ids_list, 'Comparing Library for {}'.format(username))

        # Create Bookmark
        response = _create_create_bookmark(self, 'bigbrother', 4, folder_name='foldername2', status_code=201)
        self.assertEqual(response.data['listing']['id'], 4)

        # Compare Library for users
        usernames_list = {'wsmith': ['Bread Basket-None',
                                     'Air Mail-None',
                                     'Skybox 1-None',
                                     'Skybox 2-None',
                                     'Skybox 3-None',
                                     'Air Mail 2-foldername1',
                                     'Air Mail 3-foldername1'],
                          'julia': [],
                          'jones': [],
                          'bigbrother': ['Bread Basket-None', 'Air Mail 3-foldername2']}

        for username, ids_list in usernames_list.items():
            user = generic_model_access.get_profile(username).user
            self.client.force_authenticate(user=user)

            url = '/api/self/library/'
            response = self.client.get(url, format='json')

            before_notification_ids = ['{}-{}'.format(entry['listing']['title'], entry['folder']) for entry in response.data]
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(before_notification_ids, ids_list, 'Comparing Library for {}'.format(username))

        # Create Bookmark Notification
        bookmark_notification_ids = []
        bookmark_notification_ids_raw = []

        for i in range(3):
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

            url = '/api/notification/'
            response = self.client.post(url, data, format='json')

            peer_data = {'user': {'username': 'julia'}, 'folder_name': 'foldername1'}  # '_bookmark_listing_ids': [3, 4]}
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['message'], 'A Simple Peer to Peer Notification')
            self.assertEqual(response.data['notification_type'], 'peer_bookmark')
            self.assertEqual(response.data['agency'], None)
            self.assertEqual(response.data['listing'], None)
            self.assertEqual(response.data['peer'], peer_data)
            self.assertTrue('expires_date' in data)

            bookmark_notification_ids.append('{}-{}'.format(response.data['notification_type'], ''.join(response.data['message'].split())))
            bookmark_notification_ids_raw.append(response.data['id'])

            # Compare Notifications for users
            usernames_list = {'wsmith': ['listing-Skybox3updatenextweek',
                                         'listing-Skybox2updatenextweek',
                                         'listing-Skybox1updatenextweek',
                                         'listing-BreadBasketupdatenextweek',
                                         'listing-AirMail3updatenextweek',
                                         'listing-AirMail2updatenextweek',
                                         'listing-AirMailupdatenextweek',
                                         'system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                                         'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z'],
                              'julia': bookmark_notification_ids[::-1] + ['system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                                        'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z'],
                              'jones': ['system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                                        'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z'],
                              'bigbrother': ['listing-BreadBasketupdatenextweek',
                                             'listing-AirMail3updatenextweek',
                                             'system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                                             'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z']}

            for username, ids_list in usernames_list.items():
                user = generic_model_access.get_profile(username).user
                self.client.force_authenticate(user=user)

                url = '/api/self/notification/'
                response = self.client.get(url, format='json')

                before_notification_ids = ['{}-{}'.format(entry.get('notification_type'), ''.join(entry.get('message').split())) for entry in response.data]
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(before_notification_ids, ids_list, 'comparing {}'.format(username))

        bookmark_notification1_id = bookmark_notification_ids_raw[0]

        # Import Bookmarks
        _import_bookmarks(self, 'julia', bookmark_notification1_id, status_code=201)

        # Compare Library for users
        usernames_list = {'wsmith': ['Bread Basket-None',
                                     'Air Mail-None',
                                     'Skybox 1-None',
                                     'Skybox 2-None',
                                     'Skybox 3-None',
                                     'Air Mail 2-foldername1',
                                     'Air Mail 3-foldername1'],
                          'julia': ['Air Mail 2-foldername1', 'Air Mail 3-foldername1'],
                          'jones': [],
                          'bigbrother': ['Bread Basket-None', 'Air Mail 3-foldername2']}

        for username, ids_list in usernames_list.items():
            user = generic_model_access.get_profile(username).user
            self.client.force_authenticate(user=user)

            url = '/api/self/library/'
            response = self.client.get(url, format='json')

            before_notification_ids = ['{}-{}'.format(entry['listing']['title'], entry['folder']) for entry in response.data]
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(before_notification_ids, ids_list, 'Comparing Library for {}'.format(username))

        # Compare Notifications for users
        usernames_list = {'wsmith': ['listing-Skybox3updatenextweek',
                                     'listing-Skybox2updatenextweek',
                                     'listing-Skybox1updatenextweek',
                                     'listing-BreadBasketupdatenextweek',
                                     'listing-AirMail3updatenextweek',
                                     'listing-AirMail2updatenextweek',
                                     'listing-AirMailupdatenextweek',
                                     'system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                                     'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z'],
                          'julia': bookmark_notification_ids[::-1] + ['listing-AirMail3updatenextweek',
                                                                      'listing-AirMail2updatenextweek',
                                                                      'system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                                                                      'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z'],
                          'jones': ['system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                                    'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z'],
                          'bigbrother': ['listing-BreadBasketupdatenextweek',
                                         'listing-AirMail3updatenextweek',
                                         'system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                                         'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z']}

        for username, ids_list in usernames_list.items():
            user = generic_model_access.get_profile(username).user
            self.client.force_authenticate(user=user)

            url = '/api/self/notification/'
            response = self.client.get(url, format='json')

            before_notification_ids = ['{}-{}'.format(entry.get('notification_type'), ''.join(entry.get('message').split())) for entry in response.data]
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(before_notification_ids, ids_list, 'Comparing Notifications for {}'.format(username))

    def test_delete_system_notification_apps_mall_steward(self):
        user = generic_model_access.get_profile('bigbrother').user
        self.client.force_authenticate(user=user)

        url = '/api/notification/1/'
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # TODO below test should work when permission gets refactored (rivera 20160620)
    @skip("should work when permission gets refactored (rivera 20160620)")
    def test_delete_system_notification_org_steward(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/notification/1/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_system_notification_user_unauthorized(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)

        url = '/api/notification/1/'
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
