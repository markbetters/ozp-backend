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

    def test_get_item_comments(self):
        username = 'wsmith'
        comments = model_access.get_item_comments(username)
        self.assertTrue(len(comments) > 1)
        # we should have at least one review from Air Mail and one from
        # bread basket
        listings_with_comments = [i.listing.title for i in comments]
        self.assertTrue('Air Mail' in listings_with_comments)
        self.assertTrue('Bread Basket' in listings_with_comments)
        # now make a request with a user that doesn't have access to
        # Bread Basket
        username = 'obrien'
        comments = model_access.get_item_comments(username)
        self.assertTrue(len(comments) > 1)
        # make sure Air Mail is present but not Bread Basket
        listings_with_comments = [i.listing.title for i in comments]
        self.assertTrue('Air Mail' in listings_with_comments)
        self.assertTrue('Bread Basket' not in listings_with_comments)

    def test_duplicate_review(self):
        # TODO
        pass

    def test_log_activity_create(self):
        username = 'wsmith'
        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')
        self.assertEqual(air_mail.approval_status,
            models.ApprovalStatus.APPROVED)
        model_access.log_activity_create(username, air_mail.id)

        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')
        self.assertEqual(air_mail.last_activity.action,
            models.Action.CREATED)

