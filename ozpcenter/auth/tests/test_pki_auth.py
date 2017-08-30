"""
Tests for (most) of the PkiAuthentication mechanism
"""
from django.test import override_settings
from django.test import TestCase

from ozpcenter import models
from ozpcenter.scripts import sample_data_generator as data_gen
import ozpcenter.auth.pkiauth as pkiauth
import ozpcenter.model_access as model_access


@override_settings(ES_ENABLED=False)
class PkiAuthenticationTest(TestCase):

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

    def test_existing_profile(self):
        profile_before_count = models.Profile.objects.count()
        profile = pkiauth._get_profile_by_dn('Jones jones')
        profile_after_count = models.Profile.objects.count()
        self.assertEqual(profile.user.username, 'jones')
        self.assertEqual(profile_before_count, profile_after_count)

    def test_disabled_profile(self):
        profile = model_access.get_profile('jones')
        profile.user.is_active = False
        profile.user.save()
        profile = pkiauth._get_profile_by_dn('Jones jones')
        self.assertEqual(profile, None)

    def test_new_user(self):
        # with name longer than 30 chars
        dn = 'This guy has a really really really long DN'
        profile = pkiauth._get_profile_by_dn(dn)
        self.assertEqual(profile.user.username, 'this_guy_has_a_really_really_r')

    def test_duplicate_username(self):
        """
        Tests case where a user with a given DN doesn't exist, but when one is
        created using the sanitization rules (30 chars or less, spaces = _, etc)
        for the given dn, it maps to one that already exists
        """
        # create a new user
        profile = pkiauth._get_profile_by_dn('Jones_jones')
        self.assertEqual(profile.user.username, 'jones_jones')

        # this dn has an "'" in it, but that gets stripped out before creating
        # the new user
        profile = pkiauth._get_profile_by_dn('jones jones\'')
        self.assertEqual(profile.user.username, 'jones_jones_2')

    def test_case_username(self):
        # DN with mixed case should match
        profile = pkiauth._get_profile_by_dn('JoNeS jOnEs')
        self.assertEqual(profile.user.username, 'jones')

    def test_preprocess_dn(self):
        dn = '/THIRD=c/SECOND=b/FIRST=a'
        dn = pkiauth._preprocess_dn(dn)
        self.assertEqual(dn, 'FIRST=a, SECOND=b, THIRD=c')
