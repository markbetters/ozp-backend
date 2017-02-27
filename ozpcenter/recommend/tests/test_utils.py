"""
Tests for (most) of the PkiAuthentication mechanism
"""
from django.test import TestCase

from ozpcenter.scripts import sample_data_generator as data_gen
from ozpcenter.recommend import utils


class UtilsTest(TestCase):

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

    def test_map_numbers(self):
        input_num = 500
        in_min = 1
        in_max = 500
        out_min = 10
        out_max = 20

        results = utils.map_numbers(input_num, in_min, in_max, out_min, out_max)
        self.assertEqual(results, 20)

    def test_map_numbers_1(self):
        input_num = 2
        in_min = 1
        in_max = 500
        out_min = 10
        out_max = 20

        results = utils.map_numbers(input_num, in_min, in_max, out_min, out_max)
        self.assertEqual(results, 10.02004008016032)
