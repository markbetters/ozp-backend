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

    def test_log_activity_modify(self):
        username = 'wsmith'
        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')

        # fields to change
        changes = [
            {'old_value': '', 'new_value': 'lots of things',
                'field_name': 'what_is_new'},
            {'old_value': 'Ministry of Truth', 'new_value': 'Ministry of Love',
                'field_name': 'agency'}
        ]
        model_access.log_activity_modify(username, air_mail.id, changes)

        listing_activities = air_mail.listing_activities.filter(
            action=models.Action.MODIFIED)

        modified_activity = listing_activities[0]
        self.assertEqual(modified_activity.author.user.username, username)
        change_details = modified_activity.change_details.all()
        self.assertEqual(len(change_details), 2)

        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')
        self.assertEqual(air_mail.last_activity, modified_activity)

    def test_log_activity_submit(self):
        username = 'wsmith'
        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')

        model_access.log_activity_submit(username, air_mail.id)

        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')
        self.assertEqual(air_mail.last_activity.action,
            models.Action.SUBMITTED)

        listing_activities = air_mail.listing_activities.filter(
            action=models.Action.SUBMITTED)
        submitted_activity = listing_activities[0]
        self.assertEqual(submitted_activity.author.user.username, username)

    def test_log_activity_approve_org(self):
        username = 'wsmith'
        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')

        model_access.log_activity_org_approve(username, air_mail.id)

        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')
        self.assertEqual(air_mail.last_activity.action,
            models.Action.APPROVED_ORG)

        listing_activities = air_mail.listing_activities.filter(
            action=models.Action.APPROVED_ORG)
        approved_org_activity = listing_activities[0]
        self.assertEqual(approved_org_activity.author.user.username, username)

    def test_log_activity_approve(self):
        username = 'wsmith'
        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')

        model_access.log_activity_approve(username, air_mail.id)

        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')
        self.assertEqual(air_mail.last_activity.action,
            models.Action.APPROVED)

        listing_activities = air_mail.listing_activities.filter(
            action=models.Action.APPROVED)
        approved_activity = listing_activities[0]
        self.assertEqual(approved_activity.author.user.username, username)

    def test_log_activity_reject(self):
        username = 'wsmith'
        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')

        description = 'this app is bad'
        model_access.log_activity_reject(username, air_mail.id,
            description)

        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')
        self.assertEqual(air_mail.last_activity.action,
            models.Action.REJECTED)

        listing_activities = air_mail.listing_activities.filter(
            action=models.Action.REJECTED)
        rejected_activity = listing_activities[0]
        self.assertEqual(rejected_activity.author.user.username, username)
        self.assertEqual(rejected_activity.description, description)

    def test_log_activity_enable(self):
        username = 'wsmith'
        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')

        model_access.log_activity_enable(username, air_mail.id)

        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')
        self.assertEqual(air_mail.last_activity.action,
            models.Action.ENABLED)

        listing_activities = air_mail.listing_activities.filter(
            action=models.Action.ENABLED)
        enabled_activity = listing_activities[0]
        self.assertEqual(enabled_activity.author.user.username, username)
        self.assertTrue(air_mail.is_enabled)

    def test_log_activity_disable(self):
        username = 'wsmith'
        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')

        model_access.log_activity_disable(username, air_mail.id)

        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')
        self.assertEqual(air_mail.last_activity.action,
            models.Action.DISABLED)

        listing_activities = air_mail.listing_activities.filter(
            action=models.Action.DISABLED)
        enabled_activity = listing_activities[0]
        self.assertEqual(enabled_activity.author.user.username, username)
        self.assertFalse(air_mail.is_enabled)

    def test_log_activity_review_edit(self):
        username = 'wsmith'
        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')

        change_details = [
            {
                'field_name': 'rate',
                'old_value': 5,
                'new_value': 3
            },
            {
                'field_name': 'text',
                'old_value': 'this app is the best',
                'new_value': 'this app is just ok'
            }
        ]
        model_access.log_activity_review_edit(username, air_mail.id,
            change_details)

        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')
        self.assertEqual(air_mail.last_activity.action,
            models.Action.REVIEW_EDITED)

        listing_activities = air_mail.listing_activities.filter(
            action=models.Action.REVIEW_EDITED)
        enabled_activity = listing_activities[0]
        self.assertEqual(enabled_activity.author.user.username, username)

    def test_log_activity_review_delete(self):
        username = 'wsmith'
        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')

        change_details = [
            {
                'field_name': 'rate',
                'old_value': 5,
                'new_value': 'N/A'
            },
            {
                'field_name': 'text',
                'old_value': 'this app is the best',
                'new_value': 'N/A'
            }
        ]
        model_access.log_activity_review_delete(username, air_mail.id,
            change_details)

        air_mail = models.Listing.objects.for_user(username).get(
            title='Air Mail')
        self.assertEqual(air_mail.last_activity.action,
            models.Action.REVIEW_DELETED)

        listing_activities = air_mail.listing_activities.filter(
            action=models.Action.REVIEW_DELETED)
        enabled_activity = listing_activities[0]
        self.assertEqual(enabled_activity.author.user.username, username)
