"""
Tests for notification endpoints
"""
from unittest import skip
import copy
import datetime
import pytz

from django.test import override_settings
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


@override_settings(ES_ENABLED=False)
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
            self.assertIn('notification_id', current_notification)
            self.assertIn('read_status', current_notification)
            self.assertIn('acknowledged_status', current_notification)

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
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notification_list = ['{}-{}-{}'.format(entry['entity_id'], entry['notification_type'], ''.join(entry['message'].split())) for entry in response.data]

        expected_data = ['147-listing-Saturnupdatenextweek',
                         '101-listing-Mallratsupdatenextweek',
                         '101-listing-Mallratsupdatenextweek',
                         '81-listing-JeanGreyupdatenextweek',
                         '77-listing-IronManupdatenextweek',
                         '63-listing-Grandfatherclockupdatenextweek',
                         '44-listing-Diamondupdatenextweek',
                         '23-listing-BreadBasketupdatenextweek',
                         '23-listing-BreadBasketupdatenextweek',
                         '10-listing-BaltimoreRavensupdatenextweek',
                         '10-listing-BaltimoreRavensupdatenextweek',
                         '9-listing-Azerothupdatenextweek',
                         '9-listing-Azerothupdatenextweek',
                         '2-listing-AirMailupdatenextweek',
                         '2-listing-AirMailupdatenextweek',
                         '160-listing-Auserhasratedlisting<b>Strokeplay</b>3stars',
                         '136-listing-Auserhasratedlisting<b>Ruby</b>5stars',
                         '133-listing-Auserhasratedlisting<b>ProjectManagement</b>1star',
                         '133-listing-Auserhasratedlisting<b>ProjectManagement</b>2stars',
                         '109-listing-Auserhasratedlisting<b>Moonshine</b>2stars',
                         '109-listing-Auserhasratedlisting<b>Moonshine</b>5stars',
                         '96-listing-Auserhasratedlisting<b>LocationLister</b>4stars',
                         '90-listing-Auserhasratedlisting<b>Lager</b>2stars',
                         '90-listing-Auserhasratedlisting<b>Lager</b>5stars',
                         '88-listing-Auserhasratedlisting<b>KomodoDragon</b>1star',
                         '82-listing-Auserhasratedlisting<b>JotSpot</b>4stars',
                         '70-listing-Auserhasratedlisting<b>HouseTargaryen</b>5stars',
                         '69-listing-Auserhasratedlisting<b>HouseStark</b>4stars',
                         '69-listing-Auserhasratedlisting<b>HouseStark</b>1star',
                         '65-listing-Auserhasratedlisting<b>Harley-DavidsonCVO</b>3stars',
                         '30-listing-Auserhasratedlisting<b>ChartCourse</b>5stars',
                         '30-listing-Auserhasratedlisting<b>ChartCourse</b>2stars',
                         '27-listing-Auserhasratedlisting<b>BusinessManagementSystem</b>2stars',
                         '27-listing-Auserhasratedlisting<b>BusinessManagementSystem</b>4stars',
                         '27-listing-Auserhasratedlisting<b>BusinessManagementSystem</b>3stars',
                         '23-listing-Auserhasratedlisting<b>BreadBasket</b>5stars',
                         '23-listing-Auserhasratedlisting<b>BreadBasket</b>2stars',
                         '18-listing-Auserhasratedlisting<b>Bleach</b>5stars',
                         '18-listing-Auserhasratedlisting<b>Bleach</b>4stars',
                         '14-listing-Auserhasratedlisting<b>BassFishing</b>4stars',
                         '11-listing-Auserhasratedlisting<b>Barbecue</b>5stars',
                         '2-listing-Auserhasratedlisting<b>AirMail</b>4stars',
                         '2-listing-Auserhasratedlisting<b>AirMail</b>1star',
                         '2-listing-Auserhasratedlisting<b>AirMail</b>3stars',
                         '2-listing-Auserhasratedlisting<b>AirMail</b>5stars',
                         'None-system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                         'None-system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z']

        self.assertListEqual(notification_list, expected_data)

        # Get reversed order
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/notification/?ordering=-notification__created_date'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notification_list = ['{}-{}-{}'.format(entry['entity_id'], entry['notification_type'], ''.join(entry['message'].split())) for entry in response.data]

        self.assertEqual(notification_list, expected_data)

        # Get ascending order
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/notification/?ordering=notification__created_date'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notification_list = ['{}-{}-{}'.format(entry['entity_id'], entry['notification_type'], ''.join(entry['message'].split())) for entry in response.data]
        self.assertEqual(notification_list, list(reversed(expected_data)))

    def test_dismiss_self_notification(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)

        url = '/api/self/notification/'
        response = self.client.get(url, format='json')
        mailbox_ids = []
        notification_ids = []
        for i in response.data:
            notification_ids.append([i['notification_id'], ''.join(i['message'].split())])
            mailbox_ids.append(i['id'])

        expected = [[229, 'Saturnupdatenextweek'],
                    [222, 'Mallratsupdatenextweek'],
                    [221, 'Mallratsupdatenextweek'],
                    [213, 'JeanGreyupdatenextweek'],
                    [212, 'IronManupdatenextweek'],
                    [205, 'Grandfatherclockupdatenextweek'],
                    [200, 'Diamondupdatenextweek'],
                    [196, 'BreadBasketupdatenextweek'],
                    [195, 'BreadBasketupdatenextweek'],
                    [191, 'BaltimoreRavensupdatenextweek'],
                    [190, 'BaltimoreRavensupdatenextweek'],
                    [189, 'Azerothupdatenextweek'],
                    [188, 'Azerothupdatenextweek'],
                    [187, 'AirMailupdatenextweek'],
                    [186, 'AirMailupdatenextweek'],
                    [161, 'Auserhasratedlisting<b>Strokeplay</b>3stars'],
                    [149, 'Auserhasratedlisting<b>Ruby</b>5stars'],
                    [144, 'Auserhasratedlisting<b>ProjectManagement</b>1star'],
                    [143, 'Auserhasratedlisting<b>ProjectManagement</b>2stars'],
                    [125, 'Auserhasratedlisting<b>Moonshine</b>2stars'],
                    [124, 'Auserhasratedlisting<b>Moonshine</b>5stars'],
                    [101, 'Auserhasratedlisting<b>LocationLister</b>4stars'],
                    [99, 'Auserhasratedlisting<b>Lager</b>2stars'],
                    [98, 'Auserhasratedlisting<b>Lager</b>5stars'],
                    [94, 'Auserhasratedlisting<b>KomodoDragon</b>1star'],
                    [89, 'Auserhasratedlisting<b>JotSpot</b>4stars'],
                    [77, 'Auserhasratedlisting<b>HouseTargaryen</b>5stars'],
                    [76, 'Auserhasratedlisting<b>HouseStark</b>4stars'],
                    [75, 'Auserhasratedlisting<b>HouseStark</b>1star'],
                    [70, 'Auserhasratedlisting<b>Harley-DavidsonCVO</b>3stars'],
                    [47, 'Auserhasratedlisting<b>ChartCourse</b>5stars'],
                    [46, 'Auserhasratedlisting<b>ChartCourse</b>2stars'],
                    [45, 'Auserhasratedlisting<b>BusinessManagementSystem</b>2stars'],
                    [44, 'Auserhasratedlisting<b>BusinessManagementSystem</b>4stars'],
                    [43, 'Auserhasratedlisting<b>BusinessManagementSystem</b>3stars'],
                    [40, 'Auserhasratedlisting<b>BreadBasket</b>5stars'],
                    [39, 'Auserhasratedlisting<b>BreadBasket</b>2stars'],
                    [35, 'Auserhasratedlisting<b>Bleach</b>5stars'],
                    [34, 'Auserhasratedlisting<b>Bleach</b>4stars'],
                    [29, 'Auserhasratedlisting<b>BassFishing</b>4stars'],
                    [23, 'Auserhasratedlisting<b>Barbecue</b>5stars'],
                    [11, 'Auserhasratedlisting<b>AirMail</b>4stars'],
                    [10, 'Auserhasratedlisting<b>AirMail</b>1star'],
                    [9, 'Auserhasratedlisting<b>AirMail</b>3stars'],
                    [8, 'Auserhasratedlisting<b>AirMail</b>5stars'],
                    [2, 'Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B'],
                    [1, 'Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z']]

        self.assertEqual(expected, notification_ids)

        # now dismiss the first notification
        dismissed_mailbox_id = mailbox_ids[0]
        url = url + str(dismissed_mailbox_id) + '/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # now get our notifications again, make sure the one was removed
        url = '/api/self/notification/'
        response = self.client.get(url, format='json')
        notification_ids = []
        for i in response.data:
            notification_ids.append([i['notification_id'], ''.join(i['message'].split())])

        expected = [[222, 'Mallratsupdatenextweek'],
                    [221, 'Mallratsupdatenextweek'],
                    [213, 'JeanGreyupdatenextweek'],
                    [212, 'IronManupdatenextweek'],
                    [205, 'Grandfatherclockupdatenextweek'],
                    [200, 'Diamondupdatenextweek'],
                    [196, 'BreadBasketupdatenextweek'],
                    [195, 'BreadBasketupdatenextweek'],
                    [191, 'BaltimoreRavensupdatenextweek'],
                    [190, 'BaltimoreRavensupdatenextweek'],
                    [189, 'Azerothupdatenextweek'],
                    [188, 'Azerothupdatenextweek'],
                    [187, 'AirMailupdatenextweek'],
                    [186, 'AirMailupdatenextweek'],
                    [161, 'Auserhasratedlisting<b>Strokeplay</b>3stars'],
                    [149, 'Auserhasratedlisting<b>Ruby</b>5stars'],
                    [144, 'Auserhasratedlisting<b>ProjectManagement</b>1star'],
                    [143, 'Auserhasratedlisting<b>ProjectManagement</b>2stars'],
                    [125, 'Auserhasratedlisting<b>Moonshine</b>2stars'],
                    [124, 'Auserhasratedlisting<b>Moonshine</b>5stars'],
                    [101, 'Auserhasratedlisting<b>LocationLister</b>4stars'],
                    [99, 'Auserhasratedlisting<b>Lager</b>2stars'],
                    [98, 'Auserhasratedlisting<b>Lager</b>5stars'],
                    [94, 'Auserhasratedlisting<b>KomodoDragon</b>1star'],
                    [89, 'Auserhasratedlisting<b>JotSpot</b>4stars'],
                    [77, 'Auserhasratedlisting<b>HouseTargaryen</b>5stars'],
                    [76, 'Auserhasratedlisting<b>HouseStark</b>4stars'],
                    [75, 'Auserhasratedlisting<b>HouseStark</b>1star'],
                    [70, 'Auserhasratedlisting<b>Harley-DavidsonCVO</b>3stars'],
                    [47, 'Auserhasratedlisting<b>ChartCourse</b>5stars'],
                    [46, 'Auserhasratedlisting<b>ChartCourse</b>2stars'],
                    [45, 'Auserhasratedlisting<b>BusinessManagementSystem</b>2stars'],
                    [44, 'Auserhasratedlisting<b>BusinessManagementSystem</b>4stars'],
                    [43, 'Auserhasratedlisting<b>BusinessManagementSystem</b>3stars'],
                    [40, 'Auserhasratedlisting<b>BreadBasket</b>5stars'],
                    [39, 'Auserhasratedlisting<b>BreadBasket</b>2stars'],
                    [35, 'Auserhasratedlisting<b>Bleach</b>5stars'],
                    [34, 'Auserhasratedlisting<b>Bleach</b>4stars'],
                    [29, 'Auserhasratedlisting<b>BassFishing</b>4stars'],
                    [23, 'Auserhasratedlisting<b>Barbecue</b>5stars'],
                    [11, 'Auserhasratedlisting<b>AirMail</b>4stars'],
                    [10, 'Auserhasratedlisting<b>AirMail</b>1star'],
                    [9, 'Auserhasratedlisting<b>AirMail</b>3stars'],
                    [8, 'Auserhasratedlisting<b>AirMail</b>5stars'],
                    [2, 'Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B'],
                    [1, 'Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z']]

        self.assertEqual(expected, notification_ids)

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
            test_time = datetime.datetime.strptime(i, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
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

        url = '/api/notifications/pending/?listing=1'  # ID 1 belongs to AcousticGuitar
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notification_list = [['{}-{}-{}'.format(entry['entity_id'], entry['notification_type'], ''.join(entry['message'].split())), entry['expires_date']] for entry in response.data]
        expected = ['1-listing-AcousticGuitarupdatenextweek',
                    '1-listing-Auserhasratedlisting<b>AcousticGuitar</b>5stars',
                    '1-listing-Auserhasratedlisting<b>AcousticGuitar</b>1star',
                    '1-listing-Auserhasratedlisting<b>AcousticGuitar</b>3stars']

        self.assertEqual(expected, [entry[0] for entry in notification_list])

        now = datetime.datetime.now(pytz.utc)
        expires_at = [entry[1] for entry in notification_list]
        for i in expires_at:
            test_time = datetime.datetime.strptime(i, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
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
        # test_create_system_notification_unauthorized_user
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

        TODO: refactor to make easier to understand and read code

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
        usernames_list = {'bigbrother': ['listing-WolfFinderupdatenextweek',
                                        'listing-WolfFinderupdatenextweek',
                                        'listing-WhiteHorseupdatenextweek',
                                        'listing-Violinupdatenextweek',
                                        'listing-Tornadoupdatenextweek',
                                        'listing-Stopsignupdatenextweek',
                                        'listing-SoundMixerupdatenextweek',
                                        'listing-Snowupdatenextweek',
                                        'listing-Pianoupdatenextweek',
                                        'listing-Parrotletupdatenextweek',
                                        'listing-MonkeyFinderupdatenextweek',
                                        'listing-LionFinderupdatenextweek',
                                        'listing-Lightningupdatenextweek',
                                        'listing-KillerWhaleupdatenextweek',
                                        'listing-KillerWhaleupdatenextweek',
                                        'listing-InformationalBookupdatenextweek',
                                        'listing-GalleryofMapsupdatenextweek',
                                        'listing-ElectricPianoupdatenextweek',
                                        'listing-ElectricGuitarupdatenextweek',
                                        'listing-ChartCourseupdatenextweek',
                                        'listing-ChartCourseupdatenextweek',
                                        'listing-Chainboatnavigationupdatenextweek',
                                        'listing-BreadBasketupdatenextweek',
                                        'listing-BreadBasketupdatenextweek',
                                        'listing-AcousticGuitarupdatenextweek',
                                        'listing-Auserhasratedlisting<b>WolfFinder</b>4stars',
                                        'listing-Auserhasratedlisting<b>WolfFinder</b>5stars',
                                        'listing-Auserhasratedlisting<b>WhiteHorse</b>4stars',
                                        'listing-Auserhasratedlisting<b>Tornado</b>1star',
                                        'listing-Auserhasratedlisting<b>Tornado</b>1star',
                                        'listing-Auserhasratedlisting<b>Tornado</b>1star',
                                        'listing-Auserhasratedlisting<b>SailboatRacing</b>3stars',
                                        'listing-Auserhasratedlisting<b>NetworkSwitch</b>4stars',
                                        'listing-Auserhasratedlisting<b>MonkeyFinder</b>1star',
                                        'listing-Auserhasratedlisting<b>MonkeyFinder</b>1star',
                                        'listing-Auserhasratedlisting<b>LionFinder</b>1star',
                                        'listing-Auserhasratedlisting<b>KillerWhale</b>3stars',
                                        'listing-Auserhasratedlisting<b>KillerWhale</b>4stars',
                                        'listing-Auserhasratedlisting<b>JarofFlies</b>3stars',
                                        'listing-Auserhasratedlisting<b>InformationalBook</b>5stars',
                                        'listing-Auserhasratedlisting<b>HouseStark</b>4stars',
                                        'listing-Auserhasratedlisting<b>HouseStark</b>1star',
                                        'listing-Auserhasratedlisting<b>HouseLannister</b>1star',
                                        'listing-Auserhasratedlisting<b>Greatwhiteshark</b>3stars',
                                        'listing-Auserhasratedlisting<b>Greatwhiteshark</b>5stars',
                                        'listing-Auserhasratedlisting<b>AcousticGuitar</b>5stars',
                                        'listing-Auserhasratedlisting<b>AcousticGuitar</b>1star',
                                        'listing-Auserhasratedlisting<b>AcousticGuitar</b>3stars',
                                        'system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                                        'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z'],
                          'jones': ['listing-Lagerupdatenextweek',
                                    'listing-KillerWhaleupdatenextweek',
                                    'listing-KillerWhaleupdatenextweek',
                                    'listing-BassFishingupdatenextweek',
                                    'listing-Auserhasratedlisting<b>Strokeplay</b>3stars',
                                    'listing-Auserhasratedlisting<b>ProjectManagement</b>1star',
                                    'listing-Auserhasratedlisting<b>ProjectManagement</b>2stars',
                                    'listing-Auserhasratedlisting<b>Moonshine</b>2stars',
                                    'listing-Auserhasratedlisting<b>Moonshine</b>5stars',
                                    'listing-Auserhasratedlisting<b>Harley-DavidsonCVO</b>3stars',
                                    'listing-Auserhasratedlisting<b>BassFishing</b>4stars',
                                    'listing-Auserhasratedlisting<b>Barbecue</b>5stars',
                                    'system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                                    'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z'],
                          'julia': ['listing-Auserhasratedlisting<b>Venus</b>1star',
                                    'listing-Auserhasratedlisting<b>Venus</b>4stars',
                                    'listing-Auserhasratedlisting<b>Uranus</b>2stars',
                                    'listing-Auserhasratedlisting<b>Uranus</b>5stars',
                                    'listing-Auserhasratedlisting<b>Ten</b>3stars',
                                    'listing-Auserhasratedlisting<b>Ten</b>5stars',
                                    'listing-Auserhasratedlisting<b>Ten</b>4stars',
                                    'listing-Auserhasratedlisting<b>Sun</b>5stars',
                                    'listing-Auserhasratedlisting<b>Sun</b>5stars',
                                    'listing-Auserhasratedlisting<b>Strokeplay</b>3stars',
                                    'listing-Auserhasratedlisting<b>Stopsign</b>5stars',
                                    'listing-Auserhasratedlisting<b>Stopsign</b>5stars',
                                    'listing-Auserhasratedlisting<b>Saturn</b>5stars',
                                    'listing-Auserhasratedlisting<b>Saturn</b>3stars',
                                    'listing-Auserhasratedlisting<b>Ruby</b>5stars',
                                    'listing-Auserhasratedlisting<b>ProjectManagement</b>1star',
                                    'listing-Auserhasratedlisting<b>ProjectManagement</b>2stars',
                                    'listing-Auserhasratedlisting<b>Pluto(Notaplanet)</b>5stars',
                                    'listing-Auserhasratedlisting<b>Pluto(Notaplanet)</b>1star',
                                    'listing-Auserhasratedlisting<b>Neptune</b>1star',
                                    'listing-Auserhasratedlisting<b>Neptune</b>5stars',
                                    'listing-Auserhasratedlisting<b>MotorcycleHelmet</b>5stars',
                                    'listing-Auserhasratedlisting<b>Moonshine</b>2stars',
                                    'listing-Auserhasratedlisting<b>Moonshine</b>5stars',
                                    'listing-Auserhasratedlisting<b>MixingConsole</b>1star',
                                    'listing-Auserhasratedlisting<b>MiniDachshund</b>1star',
                                    'listing-Auserhasratedlisting<b>MiniDachshund</b>1star',
                                    'listing-Auserhasratedlisting<b>MiniDachshund</b>1star',
                                    'listing-Auserhasratedlisting<b>MiniDachshund</b>1star',
                                    'listing-Auserhasratedlisting<b>MiniDachshund</b>1star',
                                    'listing-Auserhasratedlisting<b>MiniDachshund</b>1star',
                                    'listing-Auserhasratedlisting<b>MiniDachshund</b>1star',
                                    'listing-Auserhasratedlisting<b>MiniDachshund</b>1star',
                                    'listing-Auserhasratedlisting<b>MiniDachshund</b>5stars',
                                    'listing-Auserhasratedlisting<b>MiniDachshund</b>5stars',
                                    'listing-Auserhasratedlisting<b>Minesweeper</b>2stars',
                                    'listing-Auserhasratedlisting<b>Minesweeper</b>5stars',
                                    'listing-Auserhasratedlisting<b>LocationLister</b>4stars',
                                    'listing-Auserhasratedlisting<b>Lager</b>2stars',
                                    'listing-Auserhasratedlisting<b>Lager</b>5stars',
                                    'listing-Auserhasratedlisting<b>LITRANCH</b>5stars',
                                    'listing-Auserhasratedlisting<b>LITRANCH</b>5stars',
                                    'listing-Auserhasratedlisting<b>LITRANCH</b>1star',
                                    'listing-Auserhasratedlisting<b>KomodoDragon</b>1star',
                                    'listing-Auserhasratedlisting<b>Jupiter</b>3stars',
                                    'listing-Auserhasratedlisting<b>Jupiter</b>5stars',
                                    'listing-Auserhasratedlisting<b>JotSpot</b>4stars',
                                    'listing-Auserhasratedlisting<b>Jasoom</b>2stars',
                                    'listing-Auserhasratedlisting<b>Jasoom</b>5stars',
                                    'listing-Auserhasratedlisting<b>JarofFlies</b>3stars',
                                    'listing-Auserhasratedlisting<b>HouseTargaryen</b>5stars',
                                    'listing-Auserhasratedlisting<b>HouseStark</b>4stars',
                                    'listing-Auserhasratedlisting<b>HouseStark</b>1star',
                                    'listing-Auserhasratedlisting<b>Harley-DavidsonCVO</b>3stars',
                                    'listing-Auserhasratedlisting<b>Greatwhiteshark</b>3stars',
                                    'listing-Auserhasratedlisting<b>Greatwhiteshark</b>5stars',
                                    'listing-Auserhasratedlisting<b>FightClub</b>3stars',
                                    'listing-Auserhasratedlisting<b>ClerksII</b>3stars',
                                    'listing-Auserhasratedlisting<b>Clerks</b>3stars',
                                    'listing-Auserhasratedlisting<b>ChartCourse</b>5stars',
                                    'listing-Auserhasratedlisting<b>ChartCourse</b>2stars',
                                    'listing-Auserhasratedlisting<b>BusinessManagementSystem</b>2stars',
                                    'listing-Auserhasratedlisting<b>BusinessManagementSystem</b>4stars',
                                    'listing-Auserhasratedlisting<b>BusinessManagementSystem</b>3stars',
                                    'listing-Auserhasratedlisting<b>BreadBasket</b>5stars',
                                    'listing-Auserhasratedlisting<b>BreadBasket</b>2stars',
                                    'listing-Auserhasratedlisting<b>Bleach</b>5stars',
                                    'listing-Auserhasratedlisting<b>Bleach</b>4stars',
                                    'listing-Auserhasratedlisting<b>BassFishing</b>4stars',
                                    'listing-Auserhasratedlisting<b>Basketball</b>5stars',
                                    'listing-Auserhasratedlisting<b>Basketball</b>2stars',
                                    'listing-Auserhasratedlisting<b>Barsoom</b>5stars',
                                    'listing-Auserhasratedlisting<b>Barsoom</b>3stars',
                                    'listing-Auserhasratedlisting<b>Barsoom</b>5stars',
                                    'listing-Auserhasratedlisting<b>Barbecue</b>5stars',
                                    'listing-Auserhasratedlisting<b>BaltimoreRavens</b>5stars',
                                    'listing-Auserhasratedlisting<b>Azeroth</b>5stars',
                                    'listing-Auserhasratedlisting<b>Azeroth</b>3stars',
                                    'listing-Auserhasratedlisting<b>Azeroth</b>3stars',
                                    'listing-Auserhasratedlisting<b>Azeroth</b>5stars',
                                    'listing-Auserhasratedlisting<b>Azeroth</b>5stars',
                                    'listing-Auserhasratedlisting<b>AirMail</b>4stars',
                                    'listing-Auserhasratedlisting<b>AirMail</b>1star',
                                    'listing-Auserhasratedlisting<b>AirMail</b>3stars',
                                    'listing-Auserhasratedlisting<b>AirMail</b>5stars',
                                    'system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                                    'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z'],
                          'wsmith': ['listing-Saturnupdatenextweek',
                                     'listing-Mallratsupdatenextweek',
                                     'listing-Mallratsupdatenextweek',
                                     'listing-JeanGreyupdatenextweek',
                                     'listing-IronManupdatenextweek',
                                     'listing-Grandfatherclockupdatenextweek',
                                     'listing-Diamondupdatenextweek',
                                     'listing-BreadBasketupdatenextweek',
                                     'listing-BreadBasketupdatenextweek',
                                     'listing-BaltimoreRavensupdatenextweek',
                                     'listing-BaltimoreRavensupdatenextweek',
                                     'listing-Azerothupdatenextweek',
                                     'listing-Azerothupdatenextweek',
                                     'listing-AirMailupdatenextweek',
                                     'listing-AirMailupdatenextweek',
                                     'listing-Auserhasratedlisting<b>Strokeplay</b>3stars',
                                     'listing-Auserhasratedlisting<b>Ruby</b>5stars',
                                     'listing-Auserhasratedlisting<b>ProjectManagement</b>1star',
                                     'listing-Auserhasratedlisting<b>ProjectManagement</b>2stars',
                                     'listing-Auserhasratedlisting<b>Moonshine</b>2stars',
                                     'listing-Auserhasratedlisting<b>Moonshine</b>5stars',
                                     'listing-Auserhasratedlisting<b>LocationLister</b>4stars',
                                     'listing-Auserhasratedlisting<b>Lager</b>2stars',
                                     'listing-Auserhasratedlisting<b>Lager</b>5stars',
                                     'listing-Auserhasratedlisting<b>KomodoDragon</b>1star',
                                     'listing-Auserhasratedlisting<b>JotSpot</b>4stars',
                                     'listing-Auserhasratedlisting<b>HouseTargaryen</b>5stars',
                                     'listing-Auserhasratedlisting<b>HouseStark</b>4stars',
                                     'listing-Auserhasratedlisting<b>HouseStark</b>1star',
                                     'listing-Auserhasratedlisting<b>Harley-DavidsonCVO</b>3stars',
                                     'listing-Auserhasratedlisting<b>ChartCourse</b>5stars',
                                     'listing-Auserhasratedlisting<b>ChartCourse</b>2stars',
                                     'listing-Auserhasratedlisting<b>BusinessManagementSystem</b>2stars',
                                     'listing-Auserhasratedlisting<b>BusinessManagementSystem</b>4stars',
                                     'listing-Auserhasratedlisting<b>BusinessManagementSystem</b>3stars',
                                     'listing-Auserhasratedlisting<b>BreadBasket</b>5stars',
                                     'listing-Auserhasratedlisting<b>BreadBasket</b>2stars',
                                     'listing-Auserhasratedlisting<b>Bleach</b>5stars',
                                     'listing-Auserhasratedlisting<b>Bleach</b>4stars',
                                     'listing-Auserhasratedlisting<b>BassFishing</b>4stars',
                                     'listing-Auserhasratedlisting<b>Barbecue</b>5stars',
                                     'listing-Auserhasratedlisting<b>AirMail</b>4stars',
                                     'listing-Auserhasratedlisting<b>AirMail</b>1star',
                                     'listing-Auserhasratedlisting<b>AirMail</b>3stars',
                                     'listing-Auserhasratedlisting<b>AirMail</b>5stars',
                                     'system-Systemwillbefunctioninginadegredadedstatebetween1800Z-0400ZonA/B',
                                     'system-Systemwillbegoingdownforapproximately30minutesonX/Yat1100Z']}

        usernames_list_main = usernames_list
        usernames_list_actual = {}
        for username, ids_list in usernames_list.items():
            user = generic_model_access.get_profile(username).user
            self.client.force_authenticate(user=user)

            url = '/api/self/notification/'
            response = self.client.get(url, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            before_notification_ids = ['{}-{}'.format(entry.get('notification_type'), ''.join(entry.get('message').split())) for entry in response.data]
            usernames_list_actual[username] = before_notification_ids

        for username, ids_list in usernames_list.items():
            before_notification_ids = usernames_list_actual[username]
            self.assertEqual(ids_list, before_notification_ids, 'Checking for {}'.format(username))

        # Compare Library for users
        usernames_list = {'bigbrother': ['Tornado-Weather',
                                        'Lightning-Weather',
                                        'Snow-Weather',
                                        'Wolf Finder-Animals',
                                        'Killer Whale-Animals',
                                        'Lion Finder-Animals',
                                        'Monkey Finder-Animals',
                                        'Parrotlet-Animals',
                                        'White Horse-Animals',
                                        'Electric Guitar-Instruments',
                                        'Acoustic Guitar-Instruments',
                                        'Sound Mixer-Instruments',
                                        'Electric Piano-Instruments',
                                        'Piano-Instruments',
                                        'Violin-Instruments',
                                        'Bread Basket-None',
                                        'Informational Book-None',
                                        'Stop sign-None',
                                        'Chain boat navigation-None',
                                        'Gallery of Maps-None',
                                        'Chart Course-None'],
                          'jones': ['Bass Fishing-None', 'Killer Whale-None', 'Lager-None'],
                          'julia': [],
                          'wsmith': ['Air Mail-old',
                                     'Albatron Technology-foldername1',
                                     'Aliens-foldername1',
                                     'Bread Basket-old',
                                     'Diamond-None',
                                     'Grandfather clock-None',
                                     'Baltimore Ravens-None',
                                     'Iron Man-heros',
                                     'Jean Grey-heros',
                                     'Mallrats-heros',
                                     'Azeroth-planets',
                                     'Saturn-planets']}

        usernames_list_actual = {}
        for username, ids_list in usernames_list.items():
            user = generic_model_access.get_profile(username).user
            self.client.force_authenticate(user=user)

            url = '/api/self/library/'
            response = self.client.get(url, format='json')
            before_notification_ids = ['{}-{}'.format(entry['listing']['title'], entry['folder']) for entry in response.data]
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            usernames_list_actual[username] = before_notification_ids

        for username, ids_list in usernames_list.items():
            before_notification_ids = usernames_list_actual[username]
            self.assertEqual(ids_list, before_notification_ids, 'Checking for {}'.format(username))

        # Create Bookmark
        response = _create_create_bookmark(self, 'bigbrother', 4, folder_name='foldername2', status_code=201)
        self.assertEqual(response.data['listing']['id'], 4)

        # Compare Library for users
        usernames_list = {'wsmith': ['Air Mail-old',
                                     'Albatron Technology-foldername1',
                                     'Aliens-foldername1',
                                     'Bread Basket-old',
                                     'Diamond-None',
                                     'Grandfather clock-None',
                                     'Baltimore Ravens-None',
                                     'Iron Man-heros',
                                     'Jean Grey-heros',
                                     'Mallrats-heros',
                                     'Azeroth-planets',
                                     'Saturn-planets'],
                          'julia': [],
                          'jones': ['Bass Fishing-None', 'Killer Whale-None', 'Lager-None'],
                          'bigbrother': ['Tornado-Weather',
                                         'Aliens-foldername2',
                                         'Lightning-Weather',
                                         'Snow-Weather',
                                         'Wolf Finder-Animals',
                                         'Killer Whale-Animals',
                                         'Lion Finder-Animals',
                                         'Monkey Finder-Animals',
                                         'Parrotlet-Animals',
                                         'White Horse-Animals',
                                         'Electric Guitar-Instruments',
                                         'Acoustic Guitar-Instruments',
                                         'Sound Mixer-Instruments',
                                         'Electric Piano-Instruments',
                                         'Piano-Instruments',
                                         'Violin-Instruments',
                                         'Bread Basket-None',
                                         'Informational Book-None',
                                         'Stop sign-None',
                                         'Chain boat navigation-None',
                                         'Gallery of Maps-None',
                                         'Chart Course-None']}

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
            usernames_list = copy.deepcopy(usernames_list_main)
            usernames_list['julia'] = bookmark_notification_ids[::-1] + usernames_list_main['julia']

            usernames_list_actual = {}
            for username, ids_list in usernames_list.items():
                user = generic_model_access.get_profile(username).user
                self.client.force_authenticate(user=user)

                url = '/api/self/notification/'
                response = self.client.get(url, format='json')
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                before_notification_ids = ['{}-{}'.format(entry.get('notification_type'), ''.join(entry.get('message').split())) for entry in response.data]
                usernames_list_actual[username] = before_notification_ids

            for username, ids_list in usernames_list.items():
                before_notification_ids = usernames_list_actual[username]
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(ids_list, before_notification_ids, 'Checking for {}'.format(username))

        bookmark_notification1_id = bookmark_notification_ids_raw[0]

        # Import Bookmarks
        _import_bookmarks(self, 'julia', bookmark_notification1_id, status_code=201)

        # Compare Library for users
        usernames_list = {'wsmith': ['Air Mail-old',
                                     'Albatron Technology-foldername1',
                                     'Aliens-foldername1',
                                     'Bread Basket-old',
                                     'Diamond-None',
                                     'Grandfather clock-None',
                                     'Baltimore Ravens-None',
                                     'Iron Man-heros',
                                     'Jean Grey-heros',
                                     'Mallrats-heros',
                                     'Azeroth-planets',
                                     'Saturn-planets'],
                          'julia': ['Albatron Technology-foldername1', 'Aliens-foldername1'],
                          'jones': ['Bass Fishing-None', 'Killer Whale-None', 'Lager-None'],
                          'bigbrother': ['Tornado-Weather',
                                         'Aliens-foldername2',
                                         'Lightning-Weather',
                                         'Snow-Weather',
                                         'Wolf Finder-Animals',
                                         'Killer Whale-Animals',
                                         'Lion Finder-Animals',
                                         'Monkey Finder-Animals',
                                         'Parrotlet-Animals',
                                         'White Horse-Animals',
                                         'Electric Guitar-Instruments',
                                         'Acoustic Guitar-Instruments',
                                         'Sound Mixer-Instruments',
                                         'Electric Piano-Instruments',
                                         'Piano-Instruments',
                                         'Violin-Instruments',
                                         'Bread Basket-None',
                                         'Informational Book-None',
                                         'Stop sign-None',
                                         'Chain boat navigation-None',
                                         'Gallery of Maps-None',
                                         'Chart Course-None']}

        for username, ids_list in usernames_list.items():
            user = generic_model_access.get_profile(username).user
            self.client.force_authenticate(user=user)

            url = '/api/self/library/'
            response = self.client.get(url, format='json')

            before_notification_ids = ['{}-{}'.format(entry['listing']['title'], entry['folder']) for entry in response.data]
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(before_notification_ids, ids_list, 'Comparing Library for {}'.format(username))

        # Compare Notifications for users
        usernames_list = copy.deepcopy(usernames_list_main)
        usernames_list['julia'] = bookmark_notification_ids[::-1] + usernames_list_main['julia']

        for username, ids_list in usernames_list.items():
            user = generic_model_access.get_profile(username).user
            self.client.force_authenticate(user=user)

            url = '/api/self/notification/'
            response = self.client.get(url, format='json')

            before_notification_ids = ['{}-{}'.format(entry.get('notification_type'), ''.join(entry.get('message').split())) for entry in response.data]
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(ids_list, before_notification_ids, 'Comparing Notifications for {}'.format(username))

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

    # TODO: Unittest for below
    # AMLNG-378 - As a user, I want to receive notification about changes on Listings I've bookmarked
    # AMLNG-377 - As an owner or ORG CS, I want to receive notification of user rating and reviews
    # AMLNG-376 - As a ORG CS, I want to receive notification of Listings submitted for my organization
    # AMLNG-173 - As Org Content Steward, I want notification if an owner has cancelled an app that was pending deletion
    # AMLNG-170 - As an Owner I want to receive notice of whether my deletion request has been approved or rejected
    # AMLNG-461 - As Developer, I want to refactor code to make it modular and easier way to add Notification Types
