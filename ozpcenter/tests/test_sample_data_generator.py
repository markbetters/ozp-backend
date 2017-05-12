"""
Tests that the sample data was created correctly
"""
from django.test import TestCase

from ozpcenter import models
from ozpcenter.scripts import sample_data_generator as data_gen


class SampleDataGeneratorTest(TestCase):

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

    def test_categories(self):
        categories = models.Category.objects.values_list('title', flat=True)
        expected_categories = ['Books and Reference', 'Business', 'Education',
            'Entertainment', 'Tools']
        for i in expected_categories:
            self.assertIn(i, categories)

    def test_stewards(self):
        # william smith should be an org steward for the Ministry of Truth
        # first, get from profile
        u = models.Profile.objects.filter(stewarded_organizations__title='Ministry of Truth')
        self.assertEquals(len(u), 3)
        u = u[0]
        self.assertEquals(u.user.username, 'wsmith')
        # for kicks, also test by getting this from the Agency model
        a = models.Agency.objects.filter(stewarded_profiles__user__username='wsmith')
        self.assertEquals(len(a), 1)
        a = a[0]
        self.assertEquals(a.title, 'Ministry of Truth')

        # find pboss, the Apps Mall Steward
        p = models.Profile.objects.get(user__username='bigbrother')
        self.assertEqual(p.highest_role(), 'APPS_MALL_STEWARD')
