"""
Listing tests
"""
from django.test import TestCase
from django.db.utils import IntegrityError
from django.db import transaction

from ozpcenter import models as models
import ozpcenter.api.listing.model_access as model_access
from ozpcenter.scripts import sample_data_generator as data_gen

class ListingTest(TestCase):

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

    def test_get_listings(self):
        username = 'wsmith'
        listings = model_access.get_listings(username)
        self.assertTrue(len(listings) >= 2)
        all_listings = models.Listing.objects.all()
        self.assertEqual(len(all_listings), 8)

    def test_filter_listings(self):
        username = 'wsmith'
        filter_params = {
            'categories': ['Business'],
            'agencies': ['Ministry of Truth'],
            'listing_types': ['Web Application'],
            'offset': 0,
            'limit': 24
        }
        listings = model_access.filter_listings(username, filter_params)