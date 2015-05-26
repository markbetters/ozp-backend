from django.test import TestCase

from django import forms
from ozpcenter import models as models

import ozpcenter.factories as f

class ProfileTest(TestCase):
	fixtures = ['ozpcenter/fixtures/base.json']	# loads fixture

	def setUp(self):
		self.user1 = f.UserFactory.create(username='joe')
		self.user2 = f.UserFactory.create()

	def test_basic_profile_constraints(self):
		self.assertIsNotNone(self.user1.username)
		self.user3 = f.UserFactory.create(username='joe')
		self.user4 = f.UserFactory.create(username='joe')
		print('user1.username: ' + self.user1.username)

	def test_model_form_validation(self):
		data = {
			'username': 'joey',
			'display_name': 'joey m',
			'email': 'joe@asdf.com',
			'bio': 'something about joe'
		}
		bound_form = models.ProfileForm(data=data)
		bound_form.is_valid()
		print('errors: ' + bound_form.errors.as_json())

