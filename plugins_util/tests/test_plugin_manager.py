"""
Tests for base_authorization
"""
import datetime
import pytz
import unittest
import sys
import os
from django.conf import settings
from django.test import TestCase

from plugins_util.plugin_manager import dynamic_importer
from plugins_util.plugin_manager import dynamic_directory_importer
from plugins_util.plugin_manager import dynamic_mock_service_importer
from plugins_util.plugin_manager import plugin_manager_instance


TEST_PLUGIN_DIRECTORY = ('%s/%s') % (os.path.realpath(os.path.join(os.path.dirname(__file__), './')), 'plugins')


class PluginManagerTest(TestCase):

    def setUp(self):
        """
        setUp is invoked before each test method
        """
        # Store the orginal value of USE_AUTH_SERVER
        self.USE_AUTH_SERVER_ORGINAL = settings.OZP['USE_AUTH_SERVER']
        # Setting USE_AUTH_SERVER to True makes the test run
        settings.OZP['USE_AUTH_SERVER'] = True

    def tearDown(self):
        """
        tearDown is invoked after each test method
        """
        # Set the value of USE_AUTH_SERVER to the orginal value
        settings.OZP['USE_AUTH_SERVER'] = self.USE_AUTH_SERVER_ORGINAL

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the whole TestCase (only run once for the TestCase)
        """
        #data_gen.run()

    # TODO FINISH UNIT TEST
    # def test_invalid_auth_cache(self):
    #     """
    #     If user's auth_expires is set too far ahead, authorization should fail
    #     """
    #     print(plugin_manager_instance)
    #
    #
    #     self.assertTrue(False)
    #
    # def test_dynamic_importer(self):
    #     current_tuple = dynamic_importer('plugins.default_access_control.main', 'PluginMain')
    #     print(current_tuple)
    #     self.assertTrue(False)

    # def test_dynamic_directory_importer(self):
    #     print(TEST_PLUGIN_DIRECTORY)
    #     current_tuple = dynamic_directory_importer(TEST_PLUGIN_DIRECTORY)
    #     print(str(current_tuple))
    #     self.assertTrue(False)

    # def test_dynamic_directory_importer(self):
    #     print(TEST_PLUGIN_DIRECTORY)
    #     current_tuple = dynamic_mock_service_importer(TEST_PLUGIN_DIRECTORY)
    #     print(str(current_tuple))
    #     self.assertTrue(False)

    # def test_dynamic_instance(self):
    #     print(TEST_PLUGIN_DIRECTORY)
    #     #current_tuple =
    #     plugin_manager_instance._load(path=TEST_PLUGIN_DIRECTORY)
    #     #print(str(current_tuple))
    #     self.assertTrue(False)
