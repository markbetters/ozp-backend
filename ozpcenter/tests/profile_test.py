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

import ozpcenter.test.factories as f

class ProfileTest(TestCase):
	# TODO: load a basic fixture
	fixtures = ['ozpcenter/test/fixtures/base.json']	# loads fixture

	def setUp(self):
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
		testUser = models.Profile(username='myname', display_name='My Name',
			email='myname@me.com')
		testUser.save()
		# check that it was saved
		user_found = models.Profile.objects.filter(username='myname').count()
		self.assertEqual(1, user_found)

	def test_model_form_validation(self):
		# agency = models.Agency.objects.get(short_name='TLA')
		# ag = f.AgencyFactory.build()
		# ag.save()
		agency = models.Agency.objects.get(short_name='TLA')
		print('agency id: ' + str(agency.id))
		print(str(agency))
		data = {
			'username': 'joey',
			'display_name': 'joey m',
			'email': 'joe@asdf.com',
			'bio': 'something about joe',
			'highest_role': models.Roles.USER,
			'organizations': [agency.id]
		}
		bound_form = models.ProfileForm(data=data)
		bound_form.is_valid()
		print('errors: ' + bound_form.errors.as_json())
		bound_form.save()
		# check this
		user_joey = models.Profile.objects.get(username='joey')
		print('user_joey: ' + str(user_joey.id))
		print('joeys orgs: ' + str(user_joey.organizations.all()))
		# check other one
		agency = models.Agency.objects.get(short_name='TLA')
		print('agency profiles: ' + str(agency.profiles.all()))

