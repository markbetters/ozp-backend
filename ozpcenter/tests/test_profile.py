"""
Profile model tests

Note: This is more verbose than most model tests, as it also serves as
examples for how to test various things
"""

from django.test import TestCase
from django.db.utils import IntegrityError
from django.db import transaction

from django import forms
from ozpcenter import models as models
from ozpcenter import model_forms as model_forms

import ozpcenter.tests.factories as f

class ProfileTest(TestCase):

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
		f.UserFactory.create(username='bob', display_name='Bob B',
			email='bob@bob.com')
		f.UserFactory.create(username='alice')
		f.AgencyFactory.create(title='Three Letter Agency', short_name='TLA')


	def test_unique_constraints(self):
		# example of how to test that exceptions are raised:
		# http://stackoverflow.com/questions/21458387/transactionmanagementerror-you-cant-execute-queries-until-the-end-of-the-atom
		try:
			with transaction.atomic():
				f.UserFactory.create(username='bob')
			self.assertTrue(0, 'Duplicate username allowed')
		except IntegrityError:
			# this is expected
			pass

		# email nor display name need be unique, so this should pass
		f.UserFactory.create(username='bob2', display_name='Bob B',
			email='bob@bob.com')

	def test_non_factory_save(self):
		"""
		Shows how the standard save() method may be invoked on a model objects

		More importantly, this demonstrates a common misconception with django
		model validation. The Profile model requires that the organizations and
		bio fields be present, yet we can save a model without them.

		This is because "constraints" like blank=False apply only to form
		validation, not to the actual database
		"""
		testUser = models.Profile(username='myname', display_name='My Name',
			email='myname@me.com')
		testUser.save()
		# check that it was saved
		user_found = models.Profile.objects.filter(username='myname').count()
		self.assertEqual(1, user_found)
		# note that the model object was saved successfully even though some
		# "required" fields were not present

	def test_model_form_validation(self):
		"""
		Demonstrates how to use a ModelForm for validation purposes, even
		though it is never rendered in a template to the client
		"""
		agency = models.Agency.objects.get(short_name='TLA')
		# first, leave off the bio
		data = {
			'username': 'joey',
			'display_name': 'joey m',
			'email': 'joe@joe.com',
			'highest_role': models.Roles.USER,
			'organizations': [agency.id]
		}
		bound_form = model_forms.ProfileForm(data=data)
		self.assertFalse(bound_form.is_valid())
		# print('errors: ' + bound_form.errors.as_json())
		# after setting the bio, the form should be valid
		data['bio'] = 'Some things about joe'
		bound_form = model_forms.ProfileForm(data=data)
		print('errors: ' + bound_form.errors.as_json())
		self.assertTrue(bound_form.is_valid())
		bound_form.save()

		# check that the many-to-many relationships worked correctly
		user_joey = models.Profile.objects.get(username='joey')
		self.assertIn(agency, user_joey.organizations.all())
		# check that the agency's profiles relationship
		agency = models.Agency.objects.get(short_name='TLA')
		self.assertIn(user_joey, agency.profiles.all())

	def test_basic_profile_form(self):
		"""
		Similar to the previous example, but demonstrating how ModelForms
		can be created that contain only a subset of the total model fields.

		This has no impact on the database itself, it just controls which
		fields get validated
		"""
		data = {
			'username': 'roy',
			'email': 'roy@roy.com',
		}
		bound_form = model_forms.BasicProfileForm(data=data)
		self.assertTrue(bound_form.is_valid())

		# but if we remove a field that the ModelForm expects...
		data = {
			'username': 'roy'
		}
		bound_form = model_forms.BasicProfileForm(data=data)
		self.assertFalse(bound_form.is_valid())

	def test_max_field_size(self):
		"""
		Although the max_length constraint is enforced at both the
		database and validation levels, SQLite does not enforce the length of a
		VARCHAR, hence a test to try and validate that without using a
		ModelForm (or explicitly calling the model's full_clean() method) will
		not succeed
		"""
		try:
			with transaction.atomic():
				uname_long = 'x' * 256
				testUser = models.Profile(username=uname_long)
				# this passes if we're using SQLite
				testUser.save()
			# self.assertTrue(0, 'username of excess length allowed')
		except IntegrityError:
			# this is expected for PostgreSQL and MySQL
			pass

	def test_created_date(self):
		pass

	def test_highest_role(self):
		testUser = models.Profile(username='newguy')
		testUser.save()
		testUser = models.Profile.objects.get(username='newguy')
		self.assertEqual(testUser.highest_role, models.Roles.USER)

