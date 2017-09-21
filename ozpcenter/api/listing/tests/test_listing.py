"""
Listing tests
"""
from django.test import override_settings
from django.test import TestCase

from ozpcenter.scripts import sample_data_generator as data_gen
import ozpcenter.api.listing.model_access as model_access
from ozpcenter import errors
import ozpcenter.model_access as generic_model_access
from ozpcenter import models
from ozpcenter.tests.helper import ListingFile


@override_settings(ES_ENABLED=False)
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

    def test_get_listings_for_user(self):
        username = 'wsmith'
        listings = model_access.get_listings(username)
        self.assertTrue(len(listings) >= 2)

    def test_get_all_listings(self):
        all_listings = models.Listing.objects.all()
        self.assertEqual(len(all_listings), len(ListingFile.listings_titles()))

    def test_filter_listings(self):
        username = 'wsmith'
        filter_params = {
            'categories': ['Business'],
            'agencies': ['Ministry of Truth'],
            'listing_types': ['Web Application'],
            'offset': 0,
            'limit': 24
        }
        listings = model_access.filter_listings(username, filter_params)  # flake8: noqa TODO: Is Necessary? - Variable not being used in method

        #  TODO: Finish Unit Test

    def test_get_reviews(self):
        username = 'wsmith'
        reviews = model_access.get_reviews(username)
        self.assertTrue(len(reviews) > 1)
        # we should have at least one review from Air Mail and one from
        # bread basket
        listings_with_reviews = [i.listing.title for i in reviews]
        self.assertTrue('Air Mail' in listings_with_reviews)
        self.assertTrue('Bread Basket' in listings_with_reviews)
        # now make a request with a user that doesn't have access to
        # Bread Basket
        username = 'obrien'
        reviews = model_access.get_reviews(username)
        self.assertTrue(len(reviews) > 1)
        # make sure Air Mail is present but not Bread Basket
        listings_with_reviews = [i.listing.title for i in reviews]
        self.assertTrue('Air Mail' in listings_with_reviews)
        self.assertTrue('Bread Basket' not in listings_with_reviews)

    def test_duplicate_review(self):
        # TODO
        pass

    def test_create_listing(self):
        author = generic_model_access.get_profile('wsmith')
        air_mail = models.Listing.objects.for_user(author.user.username).get(title='Air Mail')
        model_access.create_listing(author, air_mail)

        air_mail = models.Listing.objects.for_user(author.user.username).get(title='Air Mail')
        self.assertEqual(air_mail.last_activity.action, models.ListingActivity.CREATED)
        self.assertEqual(air_mail.approval_status, models.Listing.IN_PROGRESS)

    def test_log_listing_modification(self):
        author = generic_model_access.get_profile('wsmith')
        air_mail = models.Listing.objects.for_user(author.user.username).get(title='Air Mail')

        # fields to change
        change_details = [
            {'old_value': '', 'new_value': 'lots of things', 'field_name': 'what_is_new'},
            {'old_value': 'Ministry of Truth', 'new_value': 'Ministry of Love', 'field_name': 'agency'}
        ]
        model_access.log_listing_modification(author, air_mail, change_details)

        listing_activities = air_mail.listing_activities.filter(action=models.ListingActivity.MODIFIED)

        modified_activity = listing_activities[0]
        self.assertEqual(modified_activity.author.user.username, author.user.username)

        change_details = modified_activity.change_details.all()
        self.assertEqual(len(change_details), 2)

        air_mail = models.Listing.objects.for_user(author.user.username).get(title='Air Mail')
        self.assertEqual(air_mail.last_activity, modified_activity)

    def test_submit_listing(self):
        author = generic_model_access.get_profile('wsmith')
        air_mail = models.Listing.objects.for_user(author.user.username).get(title='Air Mail')

        model_access.submit_listing(author, air_mail)

        air_mail = models.Listing.objects.for_user(author.user.username).get(title='Air Mail')
        self.assertEqual(air_mail.last_activity.action, models.ListingActivity.SUBMITTED)

        listing_activities = air_mail.listing_activities.filter(action=models.ListingActivity.SUBMITTED)
        submitted_activity = listing_activities[0]
        self.assertEqual(submitted_activity.author.user.username,
            author.user.username)

    def test_approve_listing_by_org_steward(self):
        org_steward = generic_model_access.get_profile('wsmith')
        username = org_steward.user.username
        air_mail = models.Listing.objects.for_user(username).get(title='Air Mail')

        model_access.approve_listing_by_org_steward(org_steward, air_mail)

        air_mail = models.Listing.objects.for_user(username).get(title='Air Mail')
        self.assertEqual(air_mail.last_activity.action, models.ListingActivity.APPROVED_ORG)

        listing_activities = air_mail.listing_activities.filter(action=models.ListingActivity.APPROVED_ORG)
        approved_org_activity = listing_activities[0]
        self.assertEqual(approved_org_activity.author.user.username, username)

    def test_approve_listing(self):
        apps_mall_steward = generic_model_access.get_profile('wsmith')
        username = apps_mall_steward.user.username
        air_mail = models.Listing.objects.for_user(username).get(title='Air Mail')

        model_access.approve_listing(apps_mall_steward, air_mail)

        air_mail = models.Listing.objects.for_user(username).get(title='Air Mail')
        self.assertEqual(air_mail.last_activity.action, models.ListingActivity.APPROVED)

        listing_activities = air_mail.listing_activities.filter(action=models.ListingActivity.APPROVED)
        approved_org_activity = listing_activities[0]
        self.assertEqual(approved_org_activity.author.user.username, username)

    def test_reject_listing(self):
        steward = generic_model_access.get_profile('wsmith')
        username = steward.user.username
        air_mail = models.Listing.objects.for_user(username).get(title='Air Mail')

        description = 'this app is bad'
        model_access.reject_listing(steward, air_mail, description)

        air_mail = models.Listing.objects.for_user(username).get(title='Air Mail')
        self.assertEqual(air_mail.last_activity.action, models.ListingActivity.REJECTED)

        listing_activities = air_mail.listing_activities.filter(action=models.ListingActivity.REJECTED)
        rejected_activity = listing_activities[0]
        self.assertEqual(rejected_activity.author.user.username, username)
        self.assertEqual(rejected_activity.description, description)

    def test_enable_listing(self):
        user = generic_model_access.get_profile('wsmith')
        username = user.user.username
        air_mail = models.Listing.objects.for_user(username).get(title='Air Mail')

        model_access.enable_listing(user, air_mail)
        self.assertEqual(air_mail.last_activity.action, models.ListingActivity.ENABLED)

        listing_activities = air_mail.listing_activities.filter(action=models.ListingActivity.ENABLED)
        enabled_activity = listing_activities[0]
        self.assertEqual(enabled_activity.author.user.username, username)
        self.assertTrue(air_mail.is_enabled)

    def test_disable_listing(self):
        user = generic_model_access.get_profile('wsmith')
        username = user.user.username
        air_mail = models.Listing.objects.for_user(username).get(title='Air Mail')

        model_access.disable_listing(user, air_mail)
        self.assertEqual(air_mail.last_activity.action, models.ListingActivity.DISABLED)

        listing_activities = air_mail.listing_activities.filter(action=models.ListingActivity.DISABLED)
        enabled_activity = listing_activities[0]
        self.assertEqual(enabled_activity.author.user.username, username)
        self.assertFalse(air_mail.is_enabled)

    def test_edit_listing_review(self):
        username = 'charrington'
        air_mail = models.Listing.objects.for_user(username).get(title='Air Mail')
        review = models.Review.objects.get(listing=air_mail, author__user__username=username)

        model_access.edit_listing_review(username, review, 2, 'not great')
        air_mail = models.Listing.objects.for_user(username).get(title='Air Mail')
        self.assertEqual(air_mail.last_activity.action, models.ListingActivity.REVIEW_EDITED)

        listing_activities = air_mail.listing_activities.filter(action=models.ListingActivity.REVIEW_EDITED)
        enabled_activity = listing_activities[0]
        self.assertEqual(enabled_activity.author.user.username, username)

        # Editing listing by another user should fail
        self.assertRaises(errors.PermissionDenied, model_access.edit_listing_review, 'wsmith', review, 2, 'still not great')

    def test_delete_listing_review(self):
        username = 'charrington'
        air_mail = models.Listing.objects.for_user(username).get(title='Air Mail')
        review = models.Review.objects.get(listing=air_mail, author__user__username=username)

        model_access.delete_listing_review(username, review)
        air_mail = models.Listing.objects.for_user(username).get(title='Air Mail')
        self.assertEqual(air_mail.last_activity.action, models.ListingActivity.REVIEW_DELETED)

        listing_activities = air_mail.listing_activities.filter(action=models.ListingActivity.REVIEW_DELETED)
        enabled_activity = listing_activities[0]
        self.assertEqual(enabled_activity.author.user.username, username)

    def test_delete_listing(self):
        username = 'wsmith'
        air_mail = models.Listing.objects.for_user(username).get(title='Air Mail')
        model_access.delete_listing(username, air_mail)
        self.assertEquals(1, models.Listing.objects.for_user(username).filter(title='Air Mail').count())
        self.assertTrue(models.Listing.objects.for_user(username).filter(title='Air Mail').first().is_deleted)

    def test_delete_listing_no_permission(self):
        username = 'jones'
        air_mail = models.Listing.objects.for_user(username).get(title='Air Mail')
        self.assertRaises(errors.PermissionDenied, model_access.delete_listing, username, air_mail)
        self.assertEquals(1, models.Listing.objects.for_user(username).filter(title='Air Mail').count())

    def test_doc_urls_to_string_dict(self):
        doc_urls = [
            {"name": "wiki", "url": "http://www.wiki.com"},
            {"name": "guide", "url": "http://www.guide.com"}
        ]
        out = model_access.doc_urls_to_string(doc_urls)
        self.assertEqual(out, "[('guide', 'http://www.guide.com'), ('wiki', 'http://www.wiki.com')]")

    def test_doc_urls_to_string_object(self):
        doc_urls = models.DocUrl.objects.filter(listing__unique_name='ozp.test.air_mail')
        out = model_access.doc_urls_to_string(doc_urls, True)
        self.assertEqual(out, "[('guide', 'http://www.google.com/guide'), ('wiki', 'http://www.google.com/wiki')]")

    def test_screenshots_to_string_dict(self):
        screenshots = [
            {
                "order": 0,
                "small_image": {
                    "url": "http://localhost:8000/api/image/1/",
                    "id": 1,
                    "security_marking": "UNCLASSIFIED"
                },
                "large_image": {
                    "url": "http://localhost:8000/api/image/2/",
                    "id": 2,
                    "security_marking": "UNCLASSIFIED"
                },
                "description": "Test Description"
            }
        ]

        out = model_access.screenshots_to_string(screenshots)
        self.assertEqual(out, "[(0, 1, 'UNCLASSIFIED', 2, 'UNCLASSIFIED', 'Test Description')]")

    def test_screenshots_to_string_object(self):
        screenshots = models.Screenshot.objects.filter(listing__unique_name='ozp.test.air_mail')
        screenshots_ids = [{'small_image_id': screenshot.small_image.id, 'large_image_id': screenshot.large_image.id} for screenshot in screenshots]

        out = model_access.screenshots_to_string(screenshots, True)
        self.assertEqual(out, str([(0, screenshots_ids[0]['small_image_id'], 'UNCLASSIFIED', screenshots_ids[0]['large_image_id'], 'UNCLASSIFIED', 'airmail screenshot set 1'),
                                   (1, screenshots_ids[1]['small_image_id'], 'UNCLASSIFIED', screenshots_ids[1]['large_image_id'], 'UNCLASSIFIED', 'airmail screenshot set 2')]))

    def test_image_to_string_dict(self):
        image = {
            "url": "http://localhost:8000/api/image/2/",
            "id": 2,
            "security_marking": "UNCLASSIFIED"
            }

        out = model_access.image_to_string(image)
        self.assertEqual(out, "2.UNCLASSIFIED")

    def test_image_to_string_object(self):
        listing_banner_icon_id = models.Listing.objects.get(unique_name='ozp.test.air_mail').banner_icon.id
        image = models.Image.objects.get(id=listing_banner_icon_id)
        out = model_access.image_to_string(image, True)
        self.assertEqual(out, "{}.UNCLASSIFIED".format(listing_banner_icon_id))

    def test_contacts_to_string_dict(self):
        contacts = [
            {
                "contact_type": {"name": "Government"},
                "secure_phone": "111-222-3434",
                "unsecure_phone": "444-555-4545",
                "email": "me@google.com",
                "name": "me",
                "organization": None
            },
            {
                "contact_type": {"name": "Military"},
                "secure_phone": "111-222-3434",
                "unsecure_phone": "444-555-4545",
                "email": "you@google.com",
                "name": "you",
                "organization": None
            }
        ]

        out = model_access.contacts_to_string(contacts)
        ext = str([('me', 'me@google.com', '111-222-3434', '444-555-4545', None, 'Government'),
                   ('you', 'you@google.com', '111-222-3434', '444-555-4545', None, 'Military')])
        self.assertEqual(out, ext)

    def test_contacts_to_string_object(self):
        contacts = models.Contact.objects.filter(organization='House Stark')
        out = model_access.contacts_to_string(contacts, True)

        ext = str([('Brienne Tarth', 'brienne@stark.com', '741-774-7414', '222-324-3846', 'House Stark', 'Military'),
                   ('Osha', 'osha@stark.com', '741-774-7414', '321-123-7894', 'House Stark', 'Civilian')])

        self.assertEqual(out, ext)

    def test_categories_to_string_dict(self):
        categories = [
            {"title": "Business"},
            {"title": "Education"}
        ]

        out = model_access.categories_to_string(categories)
        self.assertEqual(out, str(['Business', 'Education']))

    def test_categories_to_string_object(self):
        categories = models.Category.objects.filter(title__istartswith='b')
        out = model_access.categories_to_string(categories, True)
        self.assertEqual(out, str(['Books and Reference', 'Business']))

    def test_tags_to_string_dict(self):
        tags = [
            {"name": "test tag one"},
            {"name": "test tag two"}
        ]

        out = model_access.tags_to_string(tags)
        self.assertEqual(out, str(['test tag one', 'test tag two']))

    def test_tags_to_string_object(self):
        tags = models.Tag.objects.order_by('name').all()
        out = model_access.tags_to_string(tags, True)

        self.assertEqual(out, str(ListingFile.listings_tags()))

    def test_owners_to_string_dict(self):
        owners = [
            {"user": {"username": "jack"}},
            {"user": {"username": "jill"}}
        ]

        out = model_access.owners_to_string(owners)
        self.assertEqual(out, str(['jack', 'jill']))

    def test_owners_to_string_object(self):
        owners = models.Profile.objects.filter(user__username__istartswith='j')
        out = model_access.owners_to_string(owners, True)
        self.assertEqual(out, "['johnson', 'jones', 'jsnow', 'julia']")

    def test_put_counts_in_listings_endpoint(self):
        queryset = models.Listing.objects.all()
        data = model_access.put_counts_in_listings_endpoint(queryset)
        self.assertTrue(data['total'] > 5)
        self.assertTrue(data['enabled'] > 2)
        self.assertTrue(data['organizations']['1'] > 2)
        self.assertTrue(data['IN_PROGRESS'] >= 0)
        self.assertTrue(data['PENDING'] >= 0)
        self.assertTrue(data['REJECTED'] >= 0)
        self.assertTrue(data['APPROVED_ORG'] >= 0)
        self.assertTrue(data['APPROVED'] >= 0)
        self.assertTrue(data['DELETED'] >= 0)
