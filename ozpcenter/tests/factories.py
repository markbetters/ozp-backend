"""
Factories for creating test data via

Factory Boy:
"As a fixtures replacement tool, it aims to replace static, hard to maintain
fixtures with easy-to-use factories for creating complex objects"

https://factoryboy.readthedocs.org/en/latest/index.html
"""
import factory
from faker import Factory
import django.contrib.auth
import ozpcenter.models as models

fake = Factory.create()


class GroupFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = django.contrib.auth.models.Group
        # http://joequery.me/code/factory-boy-handle-unique-constraints/
        django_get_or_create = ('name',)

    name = 'USER'


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = django.contrib.auth.models.User
        # http://joequery.me/code/factory-boy-handle-unique-constraints/
        django_get_or_create = ('username', 'email')

    username = fake.user_name()
    email = fake.email()


class ProfileFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Profile

    display_name = fake.name()
    bio = fake.text(max_nb_chars=1000)
    user = factory.SubFactory(UserFactory)


class AgencyFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Agency

    title = "Three Letter Agency"
    short_name = 'TLA'
