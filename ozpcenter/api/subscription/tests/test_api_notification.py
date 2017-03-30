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



class SubscriptionApiTest(APITestCase):

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

    # def test_get_self_notification(self):
    #     user = generic_model_access.get_profile('wsmith').user
    #     self.client.force_authenticate(user=user)
    #
    #     url = '/api/self/notification/'
    #     response = self.client.get(url, format='json')
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     for current_notification in response.data:
    #         self.assertIn('id', current_notification)
    #         self.assertIn('created_date', current_notification)
    #         self.assertIn('expires_date', current_notification)
    #         self.assertIn('message', current_notification)
    #         self.assertIn('author', current_notification)
    #         self.assertIn('listing', current_notification)
    #         self.assertIn('agency', current_notification)
    #         self.assertIn('notification_type', current_notification)
    #         self.assertIn('peer', current_notification)
    #
    # def test_get_self_notification_unauthorized(self):
    #     url = '/api/self/notification/'
    #     response = self.client.get(url, format='json')
    #
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #
    #
    # def test_delete_system_notification_apps_mall_steward(self):
    #     user = generic_model_access.get_profile('bigbrother').user
    #     self.client.force_authenticate(user=user)
    #
    #     url = '/api/notification/1/'
    #     response = self.client.delete(url, format='json')
    #
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #
    # # TODO below test should work when permission gets refactored (rivera 20160620)
    # @skip("should work when permission gets refactored (rivera 20160620)")
    # def test_delete_system_notification_org_steward(self):
    #     user = generic_model_access.get_profile('wsmith').user
    #     self.client.force_authenticate(user=user)
    #     url = '/api/notification/1/'
    #     response = self.client.delete(url, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    # def test_delete_system_notification_user_unauthorized(self):
    #     user = generic_model_access.get_profile('jones').user
    #     self.client.force_authenticate(user=user)
    #
    #     url = '/api/notification/1/'
    #     response = self.client.delete(url, format='json')
    #
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
