"""
Tests for library endpoints (listings in a user's library)
"""
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

import ozpcenter.access_control as access_control

from ozpcenter.scripts import sample_data_generator as data_gen
import ozpcenter.api.library.views as views
from ozpcenter import models as models
from ozpcenter import model_access as generic_model_access


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
		print('got django user: %s' % user)
		url = '/api/library/'
		response = self.client.get(url, format='json')
		print('response.data: %s' % response.data)

	def test_bookmark_app(self):
		"""
		POST to /self/library
		"""
		# url = reverse('account-list')
		# data = {'name': 'DabApps'}
		# response = self.client.post(url, data, format='json')
		# self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		# self.assertEqual(response.data, data)
		pass

