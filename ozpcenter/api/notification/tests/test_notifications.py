"""
Notification tests
"""
from django.test import override_settings
from django.test import TestCase

# from ozpcenter import models
# from ozpcenter.models import Notification
from ozpcenter.scripts import sample_data_generator as data_gen
# import ozpcenter.api.notification.model_access as model_access

# TODO: Add More Tests


@override_settings(ES_ENABLED=False)
class NotificationTest(TestCase):

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

    def test_get_self_notifications(self):
        # models.Notifications
        # create three system-wide notifications (not listing-specific). Make
        # one of them expire in the past

        # create one listing-specific notification for a listing in our library
        # that expires in the future, and one that expires in the past

        # create one listing-specific notification for a listing NOT in our
        # library that expires in the future, and one that expires in the past

        # get all notifications. ensure we get:
        #   * 2 system wide (unexpired) notifications
        #   * 1 listing-specific (unexpired) notification for the listing in
        #       our library
        #   * nothing else

        # mark one system wide notification and the one unexpired
        # listing-specific notification as dismissed

        # get all notifications. ensure we get:
        #   * 1 unexpired, undismissed system-wide notification
        #   * nothing else
        pass

    def test_get_profile_target_list_system(self):
        pass
        # actual_profiles_len = len(model_access.get_profile_target_list(Notification.SYSTEM,
        #                                      Notification.ALL,
        #                                      None))
        #
        # expected_profiles_len = len(models.Profile.objects.all())
        #
        # self.assertEqual(expected_profiles_len, actual_profiles_len)

    def test_get_profile_target_list_agency(self):
        pass

    def test_get_profile_target_list_listing(self):
        pass

    def test_get_profile_target_list_listing_owners(self):
        pass

    def test_get_profile_target_list_listing_org_stewards(self):
        pass

    def test_get_profile_target_list_peer(self):
        pass
