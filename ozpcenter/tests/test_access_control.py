"""
Tests for access control utility functions
"""
import json
import unittest

from django.test import TestCase

import ozpcenter.access_control as access_control

class AccessControlTest(TestCase):

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
        pass

    def test_has_access_unclass(self):
        user_accesses_json = json.dumps(
            {
                "clearances": ["U"],
                "formal_accesses": ["FOUO", "ABC"],
                "visas": []
            }
        )
        marking = 'UNCLASSIFIED//FOUO//ABC'
        self.assertTrue(access_control.has_access(user_accesses_json, marking))


        user_accesses_json = json.dumps(
            {
                "clearances": ["U"],
                "formal_accesses": [],
                "visas": []
            }
        )
        marking = 'UNCLASSIFIED'
        self.assertTrue(access_control.has_access(user_accesses_json, marking))

        user_accesses_json = json.dumps(
            {
                "clearances": ["U"],
                "formal_accesses": ["FOUO"],
                "visas": []
            }
        )
        marking = 'UNCLASSIFIED//FOUO//ABC'
        self.assertFalse(access_control.has_access(user_accesses_json, marking))
        user_accesses_json = json.dumps(
            {
                "clearances": ["U"],
                "formal_accesses": ["FOUO"],
                "visas": []
            }
        )
        marking = 'CONFIDENTIAL'
        self.assertFalse(access_control.has_access(user_accesses_json, marking))
        marking = 'SECRET'
        self.assertFalse(access_control.has_access(user_accesses_json, marking))
        marking = 'TOP SECRET'
        self.assertFalse(access_control.has_access(user_accesses_json, marking))
        marking = 'INVALID LEVEL'
        self.assertFalse(access_control.has_access(user_accesses_json, marking))

    def test_has_access_confidential(self):
        user_accesses_json = json.dumps(
            {
                "clearances": ["U", "C"],
                "formal_accesses": ["FOUO", "ABC"],
                "visas": []
            }
        )
        marking = 'UNCLASSIFIED//FOUO//ABC'
        self.assertTrue(access_control.has_access(user_accesses_json, marking))
        user_accesses_json = json.dumps(
            {
                "clearances": ["U", "C"],
                "formal_accesses": [],
                "visas": []
            }
        )
        marking = 'CONFIDENTIAL'
        self.assertTrue(access_control.has_access(user_accesses_json, marking))
        user_accesses_json = json.dumps(
            {
                "clearances": ["U", "C"],
                "formal_accesses": ["FOUO", "ABC"],
                "visas": []
            }
        )
        marking = 'CONFIDENTIAL//FOUO//ABC'
        self.assertTrue(access_control.has_access(user_accesses_json, marking))

        user_accesses_json = json.dumps(
            {
                "clearances": ["U"],
                "formal_accesses": ["FOUO"],
                "visas": []
            }
        )
        marking = 'CONFIDENTIAL'
        self.assertFalse(access_control.has_access(user_accesses_json, marking))
        marking = 'SECRET'
        self.assertFalse(access_control.has_access(user_accesses_json, marking))
        marking = 'TOP SECRET'
        self.assertFalse(access_control.has_access(user_accesses_json, marking))
        marking = 'INVALID LEVEL'
        self.assertFalse(access_control.has_access(user_accesses_json, marking))

    def test_has_access_secret(self):
        user_accesses_json = json.dumps(
            {
                "clearances": ["U", "C", "S"],
                "formal_accesses": ["FOUO", "ABC"],
                "visas": []
            }
        )
        marking = 'UNCLASSIFIED//FOUO//ABC'
        self.assertTrue(access_control.has_access(user_accesses_json, marking))
        user_accesses_json = json.dumps(
            {
                "clearances": ["U", "C", "S"],
                "formal_accesses": ["FOUO", "ABC"],
                "visas": []
            }
        )
        marking = 'CONFIDENTIAL//FOUO//ABC'
        self.assertTrue(access_control.has_access(user_accesses_json, marking))
        user_accesses_json = json.dumps(
            {
                "clearances": ["U", "C", "S"],
                "formal_accesses": [],
                "visas": []
            }
        )
        marking = 'SECRET'
        self.assertTrue(access_control.has_access(user_accesses_json, marking))
        user_accesses_json = json.dumps(
            {
                "clearances": ["U", "C", "S"],
                "formal_accesses": ["FOUO", "ABC"],
                "visas": []
            }
        )
        marking = 'SECRET//FOUO//ABC'
        self.assertTrue(access_control.has_access(user_accesses_json, marking))

        user_accesses_json = json.dumps(
            {
                "clearances": ["U", "C", "S"],
                "formal_accesses": ["FOUO", "ABC"],
                "visas": []
            }
        )
        marking = 'TOP SECRET//FOUO//ABC'
        self.assertFalse(access_control.has_access(user_accesses_json, marking))
        marking = 'SECRET//FOUO//ABC/XYZ'
        self.assertFalse(access_control.has_access(user_accesses_json, marking))

        marking = 'INVALID LEVEL'
        self.assertFalse(access_control.has_access(user_accesses_json, marking))

    def test_has_access_top_secret(self):
        user_accesses_json = json.dumps(
            {
                "clearances": ["U", "C", "S", "TS"],
                "formal_accesses": ["FOUO", "ABC"],
                "visas": []
            }
        )
        marking = 'UNCLASSIFIED//FOUO//ABC'
        self.assertTrue(access_control.has_access(user_accesses_json, marking))
        marking = 'CONFIDENTIAL//FOUO//ABC'
        self.assertTrue(access_control.has_access(user_accesses_json, marking))
        marking = 'SECRET//FOUO//ABC'
        self.assertTrue(access_control.has_access(user_accesses_json, marking))
        marking = 'TOP SECRET//FOUO//ABC'
        self.assertTrue(access_control.has_access(user_accesses_json, marking))
        user_accesses_json = json.dumps(
            {
                "clearances": ["U", "C", "S", "TS"],
                "formal_accesses": [],
                "visas": []
            }
        )
        marking = 'TOP SECRET'
        self.assertTrue(access_control.has_access(user_accesses_json, marking))

        user_accesses_json = json.dumps(
            {
                "clearances": ["U", "C", "S", "TS"],
                "formal_accesses": ["FOUO", "ABC"],
                "visas": []
            }
        )
        marking = 'SECRET//FOUO//ABC/XYZ'
        self.assertFalse(access_control.has_access(user_accesses_json, marking))
        marking = 'UNCLASSIFIED//FOUO//ABC/XYZ'
        self.assertFalse(access_control.has_access(user_accesses_json, marking))
        marking = 'INVALID LEVEL'
        self.assertFalse(access_control.has_access(user_accesses_json, marking))