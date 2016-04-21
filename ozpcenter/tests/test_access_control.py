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

    def test_split_tokens(self):
        marking = 'UNCLASSIFIED//FOUO//ABC'
        tokens = access_control._split_tokens(marking)

        actual_value = str(tokens)
        expected_value = '[ClassificationToken(Unclassified), DisseminationControlToken(FOR OFFICIAL USE ONLY), UnknownToken(ABC)]'

        self.assertEquals(actual_value, expected_value)

        marking = 'UNCLASSIFIED'
        tokens = access_control._split_tokens(marking)

        actual_value = str(tokens)
        expected_value = '[ClassificationToken(Unclassified)]'

        self.assertEquals(actual_value, expected_value)

        marking = 'UNcLaSsIfied'
        tokens = access_control._split_tokens(marking)

        actual_value = str(tokens)
        expected_value = '[ClassificationToken(Unclassified)]'

        self.assertEquals(actual_value, expected_value)


    def test_validate_marking(self):
        marking = 'UNCLASSIFIED'
        validated = access_control.validate_marking(marking)
        self.assertTrue(validated)

        marking = 'UNCLASSIFIED//FOUO//ABC'
        validated = access_control.validate_marking(marking)
        self.assertTrue(validated)

        marking = 'Invalid//FOUO//ABC'
        validated = access_control.validate_marking(marking)
        self.assertFalse(validated)

        marking = ''
        validated = access_control.validate_marking(marking)
        self.assertFalse(validated)

        marking = None
        validated = access_control.validate_marking(marking)
        self.assertFalse(validated)

    def test_has_access_unclass(self):
        user_accesses_json = json.dumps(
            {
                "clearances": ["UNCLASSIFIED"],
                "formal_accesses": ["FOUO", "ABC"],
                "visas": []
            }
        )
        marking = 'UNCLASSIFIED//FOUO//ABC'
        self.assertTrue(access_control.future_has_access(user_accesses_json, marking))


        user_accesses_json = json.dumps(
            {
                "clearances": ["UNCLASSIFIED"],
                "formal_accesses": [],
                "visas": []
            }
        )
        marking = 'UNCLASSIFIED'
        self.assertTrue(access_control.future_has_access(user_accesses_json, marking))

        user_accesses_json = json.dumps(
            {
                "clearances": ["UNCLASSIFIED"],
                "formal_accesses": ["FOUO"],
                "visas": []
            }
        )
        marking = 'UNCLASSIFIED//FOUO//ABC'
        self.assertFalse(access_control.future_has_access(user_accesses_json, marking))
        user_accesses_json = json.dumps(
            {
                "clearances": ["UNCLASSIFIED"],
                "formal_accesses": ["FOUO"],
                "visas": []
            }
        )
        marking = 'CONFIDENTIAL'
        self.assertFalse(access_control.future_has_access(user_accesses_json, marking))
        marking = 'SECRET'
        self.assertFalse(access_control.future_has_access(user_accesses_json, marking))
        marking = 'TOP SECRET'
        self.assertFalse(access_control.future_has_access(user_accesses_json, marking))
        marking = 'INVALID LEVEL'
        self.assertFalse(access_control.future_has_access(user_accesses_json, marking))

    def test_has_access_confidential(self):
        user_accesses_json = json.dumps(
            {
                "clearances": ["UNCLASSIFIED", "CONFIDENTIAL"],
                "formal_accesses": ["FOUO", "ABC"],
                "visas": []
            }
        )
        marking = 'UNCLASSIFIED//FOUO//ABC'
        self.assertTrue(access_control.future_has_access(user_accesses_json, marking))
        user_accesses_json = json.dumps(
            {
                "clearances": ["UNCLASSIFIED", "CONFIDENTIAL"],
                "formal_accesses": [],
                "visas": []
            }
        )
        marking = 'CONFIDENTIAL'
        self.assertTrue(access_control.future_has_access(user_accesses_json, marking))
        user_accesses_json = json.dumps(
            {
                "clearances": ["UNCLASSIFIED", "CONFIDENTIAL"],
                "formal_accesses": ["FOUO", "ABC"],
                "visas": []
            }
        )
        marking = 'CONFIDENTIAL//FOUO//ABC'
        self.assertTrue(access_control.future_has_access(user_accesses_json, marking))

        user_accesses_json = json.dumps(
            {
                "clearances": ["UNCLASSIFIED"],
                "formal_accesses": ["FOUO"],
                "visas": []
            }
        )
        marking = 'CONFIDENTIAL'
        self.assertFalse(access_control.future_has_access(user_accesses_json, marking))
        marking = 'SECRET'
        self.assertFalse(access_control.future_has_access(user_accesses_json, marking))
        marking = 'TOP SECRET'
        self.assertFalse(access_control.future_has_access(user_accesses_json, marking))
        marking = 'INVALID LEVEL'
        self.assertFalse(access_control.future_has_access(user_accesses_json, marking))

    def test_has_access_secret(self):
        user_accesses_json = json.dumps(
            {
                "clearances": ["UNCLASSIFIED", "CONFIDENTIAL", "SECRET"],
                "formal_accesses": ["FOUO", "ABC"],
                "visas": []
            }
        )
        marking = 'UNCLASSIFIED//FOUO//ABC'
        self.assertTrue(access_control.future_has_access(user_accesses_json, marking))
        user_accesses_json = json.dumps(
            {
                "clearances": ["UNCLASSIFIED", "CONFIDENTIAL", "SECRET"],
                "formal_accesses": ["FOUO", "ABC"],
                "visas": []
            }
        )
        marking = 'CONFIDENTIAL//FOUO//ABC'
        self.assertTrue(access_control.future_has_access(user_accesses_json, marking))
        user_accesses_json = json.dumps(
            {
                "clearances": ["UNCLASSIFIED", "CONFIDENTIAL", "SECRET"],
                "formal_accesses": [],
                "visas": []
            }
        )
        marking = 'SECRET'
        self.assertTrue(access_control.future_has_access(user_accesses_json, marking))
        user_accesses_json = json.dumps(
            {
                "clearances": ["UNCLASSIFIED", "CONFIDENTIAL", "SECRET"],
                "formal_accesses": ["FOUO", "ABC"],
                "visas": []
            }
        )
        marking = 'SECRET//FOUO//ABC'
        self.assertTrue(access_control.future_has_access(user_accesses_json, marking))

        user_accesses_json = json.dumps(
            {
                "clearances": ["UNCLASSIFIED", "CONFIDENTIAL", "SECRET"],
                "formal_accesses": ["FOUO", "ABC"],
                "visas": []
            }
        )
        marking = 'TOP SECRET//FOUO//ABC'
        self.assertFalse(access_control.future_has_access(user_accesses_json, marking))
        marking = 'SECRET//FOUO//ABC/XYZ'
        self.assertFalse(access_control.future_has_access(user_accesses_json, marking))

        marking = 'INVALID LEVEL'
        self.assertFalse(access_control.future_has_access(user_accesses_json, marking))

    def test_has_access_top_secret(self):
        user_accesses_json = json.dumps(
            {
                "clearances": ["UNCLASSIFIED", "CONFIDENTIAL", "SECRET", "TOP SECRET"],
                "formal_accesses": ["FOUO", "ABC"],
                "visas": []
            }
        )
        marking = 'UNCLASSIFIED//FOUO//ABC'
        self.assertTrue(access_control.future_has_access(user_accesses_json, marking))
        marking = 'CONFIDENTIAL//FOUO//ABC'
        self.assertTrue(access_control.future_has_access(user_accesses_json, marking))
        marking = 'SECRET//FOUO//ABC'
        self.assertTrue(access_control.future_has_access(user_accesses_json, marking))
        marking = 'TOP SECRET//FOUO//ABC'
        self.assertTrue(access_control.future_has_access(user_accesses_json, marking))
        user_accesses_json = json.dumps(
            {
                "clearances": ["UNCLASSIFIED", "CONFIDENTIAL", "SECRET", "TOP SECRET"],
                "formal_accesses": [],
                "visas": []
            }
        )
        marking = 'TOP SECRET'
        self.assertTrue(access_control.future_has_access(user_accesses_json, marking))

        user_accesses_json = json.dumps(
            {
                "clearances": ["UNCLASSIFIED", "CONFIDENTIAL", "SECRET", "TOP SECRET"],
                "formal_accesses": ["FOUO", "ABC"],
                "visas": []
            }
        )
        marking = 'SECRET//FOUO//ABC/XYZ'
        self.assertFalse(access_control.future_has_access(user_accesses_json, marking))
        marking = 'UNCLASSIFIED//FOUO//ABC/XYZ'
        self.assertFalse(access_control.future_has_access(user_accesses_json, marking))
        marking = 'INVALID LEVEL'
        self.assertFalse(access_control.future_has_access(user_accesses_json, marking))
