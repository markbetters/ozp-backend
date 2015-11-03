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
import ozpcenter.errors as errors

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

    def test_invalid_auth_cache(self):
        """
        If user's auth_expires is set too far ahead, authorization should fail
        """
        auth = base_authorization.BaseAuthorization()
        profile = model_access.get_profile('jones')
        # set auth cache to expire in 1+ days (against the rules!)
        profile.auth_expires = datetime.datetime.now(pytz.utc) + datetime.timedelta(days=1, seconds=2)
        profile.save()
        self.assertRaises(errors.AuthorizationFailure,
            auth.authorization_update, 'jones')

    def test_valid_cache(self):
        auth = base_authorization.BaseAuthorization()
        profile = model_access.get_profile('jones')
        # set auth cache to expire in 1 day
        profile.auth_expires = datetime.datetime.now(pytz.utc) + datetime.timedelta(days=1)
        profile.save()
        self.assertEqual(auth.authorization_update('jones'), True)

        # try again with cache almost expired
        profile.auth_expires = datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=2)
        profile.save()
        self.assertEqual(auth.authorization_update('jones'), True)

    def test_update_cache(self):
        auth = base_authorization.BaseAuthorization()
        profile = model_access.get_profile('jones')
        profile.auth_expires = datetime.datetime.now(pytz.utc)
        profile.save()
        auth_data = {
            'dn': 'Jones jones',
            'cn': 'Jones',
            'clearances': ['U', 'C', 'S'],
            'formal_accesses': [],
            'visas': ['NOVEMBER'],
            'duty_org': 'Minitrue',
            'is_org_steward': False,
            'is_apps_mall_steward': False,
            'is_metrics_user': False
        }
        a = auth.authorization_update('jones', auth_data)
        self.assertEqual(a, True)
        # auth_expires should be rest to ~1 day from now
        profile = model_access.get_profile('jones')
        auth_expires_in = profile.auth_expires - datetime.datetime.now(pytz.utc)
        # 86,400 seconds in a day
        self.assertTrue(86398 < auth_expires_in.seconds < 86400)

        # TODO: test access_control

    def test_org_change(self):
        """
        A user's agency (organization) changes
        """
        auth = base_authorization.BaseAuthorization()
        profile = model_access.get_profile('rutherford')
        profile.auth_expires = datetime.datetime.now(pytz.utc)
        profile.save()
        org = profile.organizations.values_list('title', flat=True)[0]
        self.assertEqual(org, 'Ministry of Plenty')
        auth_data = {
            'dn': 'Rutherford rutherford',
            'cn': 'Rutherford',
            'clearances': ['U', 'C', 'S'],
            'formal_accesses': [],
            'visas': [],
            'duty_org': 'Miniluv',
            'is_org_steward': False,
            'is_apps_mall_steward': False,
            'is_metrics_user': False
        }
        a = auth.authorization_update('rutherford', auth_data)
        profile = model_access.get_profile('rutherford')
        org = profile.organizations.values_list('title', flat=True)[0]
        self.assertEqual(org, 'Ministry of Love')

    def test_org_steward_to_user(self):
        """
        A user who was an org steward is now a regular user
        """
        auth = base_authorization.BaseAuthorization()
        profile = model_access.get_profile('wsmith')
        profile.auth_expires = datetime.datetime.now(pytz.utc)
        profile.save()
        stewarded_orgs = profile.stewarded_organizations.values_list('title', flat=True)
        self.assertTrue('Ministry of Truth' in stewarded_orgs)
        self.assertEqual(profile.highest_role(), 'ORG_STEWARD')
        groups = profile.user.groups.values_list('name', flat=True)
        self.assertTrue('ORG_STEWARD' in groups)
        auth_data = {
            'dn': 'Winston Smith wsmith',
            'cn': 'Winston Smith',
            'clearances': ['U', 'C', 'S', 'TS'],
            'formal_accesses': [],
            'visas': [],
            'duty_org': 'Minitrue',
            'is_org_steward': False,
            'is_apps_mall_steward': False,
            'is_metrics_user': False
        }
        a = auth.authorization_update('wsmith', auth_data)
        profile = model_access.get_profile('wsmith')
        stewarded_orgs = profile.stewarded_organizations.values_list('title', flat=True)
        self.assertTrue(len(stewarded_orgs) == 0)
        groups = profile.user.groups.values_list('name', flat=True)
        self.assertTrue('USER' in groups)
        self.assertTrue(len(groups) == 1)
        self.assertEqual(profile.highest_role(), 'USER')

    def test_apps_mall_steward_to_user(self):
        """
        A user who was an apps mall steward is now a regular user
        """
        auth = base_authorization.BaseAuthorization()
        profile = model_access.get_profile('bigbrother')
        profile.auth_expires = datetime.datetime.now(pytz.utc)
        profile.save()

        groups = profile.user.groups.values_list('name', flat=True)
        self.assertTrue('APPS_MALL_STEWARD' in groups)
        self.assertEqual(profile.highest_role(), 'APPS_MALL_STEWARD')
        auth_data = {
            'dn': 'Big Brother bigbrother',
            'cn': 'Big Brother',
            'clearances': ['U', 'C', 'S', 'TS'],
            'formal_accesses': [],
            'visas': [],
            'duty_org': 'Minitrue',
            'is_org_steward': False,
            'is_apps_mall_steward': False,
            'is_metrics_user': False
        }
        a = auth.authorization_update('bigbrother', auth_data)
        profile = model_access.get_profile('bigbrother')
        groups = profile.user.groups.values_list('name', flat=True)
        self.assertTrue('USER' in groups)
        self.assertTrue(len(groups) == 1)
        self.assertEqual(profile.highest_role(), 'USER')

    def test_apps_mall_steward_to_org_steward(self):
        """
        A user who was an apps mall steward is now an org steward
        """
        auth = base_authorization.BaseAuthorization()
        profile = model_access.get_profile('bigbrother')
        profile.auth_expires = datetime.datetime.now(pytz.utc)
        profile.save()

        groups = profile.user.groups.values_list('name', flat=True)
        self.assertTrue('APPS_MALL_STEWARD' in groups)
        self.assertEqual(profile.highest_role(), 'APPS_MALL_STEWARD')
        auth_data = {
            'dn': 'Big Brother bigbrother',
            'cn': 'Big Brother',
            'clearances': ['U', 'C', 'S', 'TS'],
            'formal_accesses': [],
            'visas': [],
            'duty_org': 'Minitrue',
            'is_org_steward': True,
            'is_apps_mall_steward': False,
            'is_metrics_user': False
        }
        a = auth.authorization_update('bigbrother', auth_data)
        profile = model_access.get_profile('bigbrother')
        groups = profile.user.groups.values_list('name', flat=True)
        self.assertTrue('ORG_STEWARD' in groups)
        self.assertEqual(profile.highest_role(), 'ORG_STEWARD')

    def test_org_steward_to_apps_mall_steward_only(self):
        """
        A user who was an org steward is now an apps mall steward
        """
        auth = base_authorization.BaseAuthorization()
        profile = model_access.get_profile('wsmith')
        profile.auth_expires = datetime.datetime.now(pytz.utc)
        profile.save()
        stewarded_orgs = profile.stewarded_organizations.values_list('title', flat=True)
        self.assertTrue('Ministry of Truth' in stewarded_orgs)
        self.assertEqual(profile.highest_role(), 'ORG_STEWARD')
        groups = profile.user.groups.values_list('name', flat=True)
        self.assertTrue('ORG_STEWARD' in groups)
        auth_data = {
            'dn': 'Winston Smith wsmith',
            'cn': 'Winston Smith',
            'clearances': ['U', 'C', 'S', 'TS'],
            'formal_accesses': [],
            'visas': [],
            'duty_org': 'Minitrue',
            'is_org_steward': False,
            'is_apps_mall_steward': True,
            'is_metrics_user': False
        }
        a = auth.authorization_update('wsmith', auth_data)
        profile = model_access.get_profile('wsmith')
        stewarded_orgs = profile.stewarded_organizations.values_list('title', flat=True)
        self.assertTrue(len(stewarded_orgs) == 0)
        groups = profile.user.groups.values_list('name', flat=True)
        self.assertTrue('APPS_MALL_STEWARD' in groups)
        self.assertTrue('ORG_STEWARD' not in groups)
        self.assertEqual(profile.highest_role(), 'APPS_MALL_STEWARD')

    def test_org_steward_to_apps_mall_steward(self):
        """
        A user who was an org steward is now also an apps mall steward
        """
        auth = base_authorization.BaseAuthorization()
        profile = model_access.get_profile('wsmith')
        profile.auth_expires = datetime.datetime.now(pytz.utc)
        profile.save()
        stewarded_orgs = profile.stewarded_organizations.values_list('title', flat=True)
        self.assertTrue('Ministry of Truth' in stewarded_orgs)
        self.assertEqual(profile.highest_role(), 'ORG_STEWARD')
        groups = profile.user.groups.values_list('name', flat=True)
        self.assertTrue('ORG_STEWARD' in groups)
        auth_data = {
            'dn': 'Winston Smith wsmith',
            'cn': 'Winston Smith',
            'clearances': ['U', 'C', 'S', 'TS'],
            'formal_accesses': [],
            'visas': [],
            'duty_org': 'Minitrue',
            'is_org_steward': True,
            'is_apps_mall_steward': True,
            'is_metrics_user': False
        }
        a = auth.authorization_update('wsmith', auth_data)
        profile = model_access.get_profile('wsmith')
        stewarded_orgs = profile.stewarded_organizations.values_list('title', flat=True)
        self.assertTrue('Ministry of Truth' in stewarded_orgs)
        groups = profile.user.groups.values_list('name', flat=True)
        self.assertTrue('APPS_MALL_STEWARD' in groups)
        self.assertTrue('ORG_STEWARD' in groups)
        self.assertEqual(profile.highest_role(), 'APPS_MALL_STEWARD')