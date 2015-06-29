"""
Tests for endpoints used on the Discovery page
"""
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

import ozpcenter.access_control as access_control

from ozpcenter.scripts import sample_data_generator as data_gen

class DiscoveryPageTest(APITestCase):

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

	def test_bookmark_app(self):
		"""
		POST to /self/library
		"""
		# url = reverse('account-list')
		# data = {'name': 'DabApps'}
		# response = self.client.post(url, data, format='json')
		# self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		# self.assertEqual(response.data, data)
