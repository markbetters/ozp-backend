"""
Tests for notification endpoints
"""
import datetime
import pytz

from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

import ozpcenter.access_control as access_control

from ozpcenter.scripts import sample_data_generator as data_gen
import ozpcenter.api.notification.views as views
from ozpcenter import models as models
from ozpcenter import model_access as generic_model_access


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
        url = '/api/self/notification/'
        # test unauthorized user
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # test authorized user
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        first_notification = response.data[0]
        self.assertIn('id', first_notification)
        self.assertIn('author', first_notification)
        self.assertIn('listing', first_notification)
        self.assertIn('created_date', first_notification)
        self.assertIn('message', first_notification)
        self.assertIn('expires_date', first_notification)
        self.assertIn('dismissed_by', first_notification)

    def test_dismiss_self_notification(self):
        url = '/api/self/notification/'
        # test authorized user
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        notification_ids = []
        for i in response.data:
            notification_ids.append(i['id'])

        self.assertEqual(2, len(notification_ids))

        # now dismiss the first notification
        dismissed_notification_id = notification_ids[0]
        url = url + str(dismissed_notification_id) + '/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


        # now get our notifications again, make sure the one was removed
        url = '/api/self/notification/'
        # test authorized user
        response = self.client.get(url, format='json')
        notification_ids = []
        for i in response.data:
            notification_ids.append(i['id'])

        self.assertEqual(1, len(notification_ids))
        self.assertTrue(notification_ids[0] != dismissed_notification_id)

    def test_get_pending_notifications(self):
        url = '/api/notifications/pending/'
        # test unauthorized user
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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

    def test_get_expired_notifications(self):
        url = '/api/notifications/expired/'
        # test unauthorized user
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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

    def test_create_system_notification(self):
        url = '/api/notification/'
        # test unauthorized user - only org stewards and above can create
        # system notifications
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        data = {'expires_date': '2016-09-01T15:45:55.322421Z',
            'message': 'a simple test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        data = {'expires_date': '2016-09-01T15:45:55.322421Z',
            'message': 'a simple test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'a simple test')

    def test_delete_system_notification(self):
        url = '/api/notification/1/'
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        now = datetime.datetime.now(pytz.utc)
        data = {'expires_date': str(now)}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

