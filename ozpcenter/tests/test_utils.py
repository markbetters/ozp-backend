"""
Utils tests
"""
from django.test import TestCase
from django.db.utils import IntegrityError
from django.db import transaction

from ozpcenter import models as models
from ozpcenter import utils as utils
from ozpcenter.scripts import sample_data_generator as data_gen

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

    def test_make_keysafe(self):
        name = 'Test @string\'s !'
        key_name = utils.make_keysafe(name)
        self.assertEqual('teststrings', key_name)
