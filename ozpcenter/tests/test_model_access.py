"""
Model access tests
"""
from django.test import TestCase
from django.db.utils import IntegrityError
from django.db import transaction

from ozpcenter import models as models
from ozpcenter import model_access as model_access
from ozpcenter.scripts import sample_data_generator as data_gen

class ModelAccessTest(TestCase):

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

	def test_make_keysafe(self):
		name = 'Test @string\'s !'
		key_name = model_access.make_keysafe(name)
		self.assertEqual('teststrings', key_name)

	def test_get_listings(self):
		username = 'wsmith'
		listings = model_access.get_listings(username)
		self.assertEqual(len(listings), 2)
		all_listings = models.Listing.objects.all()
		self.assertEqual(len(all_listings), 3)