"""
Tests for data.api utility functions
"""
from django.test import TestCase

from django.test import override_settings
from ozpcenter.scripts import sample_data_generator as data_gen
import ozpiwc.api.data.model_access as model_access


@override_settings(ES_ENABLED=False)
class DataTest(TestCase):

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

    def test_get_all_keys(self):
        keys = model_access.get_all_keys('wsmith')  # flake8: noqa
        # TODO: Finish Unit Tests
