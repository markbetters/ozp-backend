"""
Tests for base_authorization
"""
import datetime
import pytz
import unittest

from django.test import TestCase

from ozpcenter.scripts import sample_data_generator as data_gen
import ozpcenter.auth.base_authorization as base_authorization
import ozpcenter.models as models
import ozpcenter.model_access as model_access

class BaseAuthorizationTest(TestCase):

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

    @unittest.skip
    def test_valid_auth_cache(self):
        auth = base_authorization.BaseAuthorization()
        profile = model_access.get_profile('jones')
        # set auth cache to expire in 2 days (against the rules!)
        profile.auth_expires = datetime.datetime.now(pytz.utc) + datetime.timedelta(days=3)
        print('setting profile to expire at %s' % profile.auth_expires)
        profile.save()
        u = auth.authorization_update('jones')
        self.assertTrue(u == True)