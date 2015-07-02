"""
Tests for access control utility functions
"""
from django.test import TestCase

import ozpcenter.access_control as access_control

class ModelAccessTest(TestCase):

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

	def test_generate_access_controls(self):
		entitlement_data = {
			'clearance': ['UNCLASSIFIED', 'SECRET', 'CONFIDENTIAL'],
			'accesses': ['AB', 'CDY'],
			'legacy_accesses': ['QQ', 'RAY'],
			'visa': ['USA', 'ARG']
		}
		access_str = access_control.generate_access_control(entitlement_data)
		access_control_list = access_str.split('//')
		self.assertEqual(access_control_list[0], 'SECRET')
		controls = entitlement_data['accesses'] + entitlement_data['legacy_accesses'] + entitlement_data['visa']
		gen_controls = access_control_list[1:]
		controls.sort()
		gen_controls.sort()
		self.assertEqual(gen_controls, controls)

	def test_has_access_unclass(self):
		user = 'UNCLASSIFIED//FOUO//ABC'
		required = 'UNCLASSIFIED//FOUO//ABC'
		self.assertTrue(access_control.has_access(user, required))
		user = 'UNCLASSIFIED'
		required = 'UNCLASSIFIED'
		self.assertTrue(access_control.has_access(user, required))

		user = 'UNCLASSIFIED//FOUO'
		required = 'UNCLASSIFIED//FOUO//ABC'
		self.assertFalse(access_control.has_access(user, required))
		user = 'UNCLASSIFIED//FOUO'
		required = 'CONFIDENTIAL'
		self.assertFalse(access_control.has_access(user, required))
		required = 'SECRET'
		self.assertFalse(access_control.has_access(user, required))
		required = 'TOP SECRET'
		self.assertFalse(access_control.has_access(user, required))
		required = 'INVALID LEVEL'
		self.assertFalse(access_control.has_access(user, required))

	def test_has_access_confidential(self):
		user = 'CONFIDENTIAL//FOUO//ABC'
		required = 'UNCLASSIFIED//FOUO//ABC'
		self.assertTrue(access_control.has_access(user, required))
		user = 'CONFIDENTIAL'
		required = 'CONFIDENTIAL'
		self.assertTrue(access_control.has_access(user, required))
		user = 'CONFIDENTIAL//FOUO//ABC'
		required = 'CONFIDENTIAL//FOUO//ABC'
		self.assertTrue(access_control.has_access(user, required))

		user = 'UNCLASSIFIED//FOUO/ABC'
		required = 'CONFIDENTIAL//FOUO//ABC'
		self.assertFalse(access_control.has_access(user, required))
		user = 'UNCLASSIFIED//FOUO'
		required = 'CONFIDENTIAL'
		self.assertFalse(access_control.has_access(user, required))
		required = 'SECRET'
		self.assertFalse(access_control.has_access(user, required))
		required = 'TOP SECRET'
		self.assertFalse(access_control.has_access(user, required))
		required = 'INVALID LEVEL'
		self.assertFalse(access_control.has_access(user, required))

	def test_has_access_secret(self):
		user = 'SECRET//FOUO//ABC'
		required = 'UNCLASSIFIED//FOUO//ABC'
		self.assertTrue(access_control.has_access(user, required))
		user = 'SECRET//FOUO//ABC'
		required = 'CONFIDENTIAL//FOUO//ABC'
		self.assertTrue(access_control.has_access(user, required))
		user = 'SECRET'
		required = 'SECRET'
		self.assertTrue(access_control.has_access(user, required))
		user = 'SECRET//FOUO//ABC'
		required = 'SECRET//FOUO//ABC'
		self.assertTrue(access_control.has_access(user, required))

		user = 'SECRET//FOUO//ABC'
		required = 'TOP SECRET//FOUO//ABC'
		self.assertFalse(access_control.has_access(user, required))

		user = 'SECRET//FOUO//ABC'
		required = 'SECRET//FOUO//ABC/XYZ'
		self.assertFalse(access_control.has_access(user, required))

		required = 'INVALID LEVEL'
		self.assertFalse(access_control.has_access(user, required))

	def test_has_access_top_secret(self):
		user = 'TOP SECRET//FOUO//ABC'
		required = 'UNCLASSIFIED//FOUO//ABC'
		self.assertTrue(access_control.has_access(user, required))
		required = 'CONFIDENTIAL//FOUO//ABC'
		self.assertTrue(access_control.has_access(user, required))
		required = 'SECRET//FOUO//ABC'
		self.assertTrue(access_control.has_access(user, required))
		required = 'TOP SECRET//FOUO//ABC'
		self.assertTrue(access_control.has_access(user, required))
		user = 'TOP SECRET'
		required = 'TOP SECRET'
		self.assertTrue(access_control.has_access(user, required))

		user = 'TOP SECRET//FOUO//ABC'
		required = 'SECRET//FOUO//ABC/XYZ'
		self.assertFalse(access_control.has_access(user, required))

		user = 'TOP SECRET//FOUO//ABC'
		required = 'UNCLASSIFIED//FOUO//ABC/XYZ'
		self.assertFalse(access_control.has_access(user, required))

		required = 'INVALID LEVEL'
		self.assertFalse(access_control.has_access(user, required))