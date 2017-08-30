"""
Tests that the sample data was created correctly
"""
from django.test import override_settings
from django.test import TestCase

from ozpcenter import models
from ozpcenter.scripts import sample_data_generator as data_gen


@override_settings(ES_ENABLED=False)
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
        categories = list(models.Category.objects.values_list('title', flat=True))
        expected_categories = ['Accessories', 'Books and Reference', 'Business', 'Communication', 'Education',
                               'Entertainment', 'Finance', 'Health and Fitness', 'Media and Video',
                               'Music and Audio', 'News', 'Productivity', 'Shopping', 'Sports', 'Tools', 'Weather']

        self.assertListEqual(categories, expected_categories)

    def test_stewards(self):
        # william smith should be an org steward for the Ministry of Truth
        # first, get from profile
        ministry_of_truth_stewards = list(models.Profile.objects.filter(stewarded_organizations__title='Ministry of Truth').values_list('user__username', flat=True))
        expected_ministry_of_truth_stewards = ['bettafish', 'wsmith', 'julia']

        self.assertListEqual(ministry_of_truth_stewards, expected_ministry_of_truth_stewards)

        # for kicks, also test by getting this from the Agency model
        a = models.Agency.objects.filter(stewarded_profiles__user__username='wsmith')
        self.assertEquals(len(a), 1)
        a = a[0]
        self.assertEquals(a.title, 'Ministry of Truth')

        # find pboss, the Apps Mall Steward
        p = models.Profile.objects.get(user__username='bigbrother')
        self.assertEqual(p.highest_role(), 'APPS_MALL_STEWARD')
