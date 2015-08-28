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
        """
        test for model_access.get_storefront()

        TODO: test for correct fields returned, number of entries returned,
            and ordering. Might want to use factories here (instead of the
            sample data generator)

        """
        username = 'wsmith'
        data = model_access.get_storefront(username)

        # test that only APPROVED listings are returned
        for i in data['featured']:
            self.assertEqual(i.approval_status, models.ApprovalStatus.APPROVED)

        for i in data['recent']:
            self.assertEqual(i.approval_status, models.ApprovalStatus.APPROVED)

        for i in data['most_popular']:
            self.assertEqual(i.approval_status, models.ApprovalStatus.APPROVED)


    def test_get_metadata(self):
        """
        test for model_access.get_metadata()
        """
        metadata = model_access.get_metadata()
        categories = metadata['categories']
        keys = list(categories[0].keys()).sort()
        expected_keys = ['description', 'title'].sort()
        self.assertEqual(keys, expected_keys)

        agencies = metadata['agencies']
        keys = list(agencies[0].keys()).sort()
        expected_keys = ['short_name', 'title', 'icon'].sort()
        self.assertEqual(keys, expected_keys)

        contact_types = metadata['contact_types']
        keys = list(contact_types[0].keys()).sort()
        expected_keys = ['required', 'name'].sort()
        self.assertEqual(keys, expected_keys)

        intents = metadata['intents']
        keys = list(intents[0].keys()).sort()
        expected_keys = ['label', 'action', 'media_type', 'icon'].sort()
        self.assertEqual(keys, expected_keys)

        listing_types = metadata['listing_types']
        keys = list(listing_types[0].keys()).sort()
        expected_keys = ['title', 'description'].sort()
        self.assertEqual(keys, expected_keys)

