"""
Utils tests
"""
from django.test import TestCase
from django.db.utils import IntegrityError
from django.db import transaction

from ozpcenter import models as models
import ozpcenter.api.storefront.model_access as model_access
from ozpcenter.scripts import sample_data_generator as data_gen

class StorefrontTest(TestCase):

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

	def test_get_storefront(self):
		username = 'wsmith'
		listings = model_access.get_storefront(username)