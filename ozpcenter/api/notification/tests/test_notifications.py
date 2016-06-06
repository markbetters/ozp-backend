"""
Notification tests
"""
from django.test import TestCase

# from ozpcenter import models
from ozpcenter.scripts import sample_data_generator as data_gen
# import ozpcenter.api.notification.model_access as model_access


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

    # TODO: Add More Tests
