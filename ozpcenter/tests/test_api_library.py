"""
Tests for library endpoints (listings in a user's library)
"""
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

import ozpcenter.access_control as access_control

from ozpcenter.scripts import sample_data_generator as data_gen
from ozpcenter import views as views
from ozpcenter import models as models


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
		factory = APIRequestFactory()
		user = models.Profile.objects.get(username='wsmith').django_user
		view = views.ApplicationLibraryEntryViewSet.as_view({'get': 'list'})
		request = factory.get('/self/library', format='json')
		force_authenticate(request, user=user)
		response = view(request)
		print('response.data: %s' % response.data)


