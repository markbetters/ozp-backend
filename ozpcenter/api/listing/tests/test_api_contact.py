"""
Tests for listing endpoints
"""
from rest_framework.test import APITestCase

from ozpcenter.scripts import sample_data_generator as data_gen


class ContactApiTest(APITestCase):

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

    # TODO: Add more Unit Test (rivera 20160727)
