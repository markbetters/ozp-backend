"""
Tests for notification endpoints
"""
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
        self.assertEqual(response.status_code, 401)

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
        print('dismissed_notification_id: %s' % dismissed_notification_id)
        url = url + str(dismissed_notification_id) + '/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, 204)


        # now get our notifications again, make sure the one was removed
        url = '/api/self/notification/'
        # test authorized user
        response = self.client.get(url, format='json')
        notification_ids = []
        for i in response.data:
            notification_ids.append(i['id'])

        self.assertEqual(1, len(notification_ids))
        self.assertTrue(notification_ids[0] != dismissed_notification_id)

