"""
Tests that the sample data was created correctly
"""

from django.test import TestCase
from django.db.utils import IntegrityError
from django.db import transaction

from ozpcenter import models as models
from ozpcenter.tests import sample_data_generator as data_gen

class SampleDataGeneratorTest(TestCase):

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
		data_gen.create_sample_data()


	def test_categories(self):
		categories = models.Category.objects.all()
		self.assertEqual(len(categories), 5)
