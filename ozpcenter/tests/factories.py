"""
Factories for creating test data via

Factory Boy:
"As a fixtures replacement tool, it aims to replace static, hard to maintain
fixtures with easy-to-use factories for creating complex objects"

https://factoryboy.readthedocs.org/en/latest/index.html
"""
import factory
from faker import Factory
import ozpcenter.models as models

fake = Factory.create()

class UserFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.Profile

	username = fake.user_name()
	display_name = fake.name()
	email = fake.email()
	bio = fake.text(max_nb_chars=1000)

class AgencyFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = models.Agency

	title = "Three Letter Agency"
	icon_url = 'https://someplace.com/icon'
	short_name = 'TLA'