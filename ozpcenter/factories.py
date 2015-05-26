"""
Factories for creating test data
"""
import factory
from faker import Factory
import ozpcenter.models as models

fake = Factory.create()

class UserFactory(factory.Factory):
	class Meta:
		model = models.Profile

	username = fake.user_name()
	display_name = fake.name()
	email = fake.email()
	bio = fake.text(max_nb_chars=1000)