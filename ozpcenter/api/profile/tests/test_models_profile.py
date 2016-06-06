"""
Profile model tests

Note: This is more verbose than most model tests, as it also serves as
examples for how to test various things
"""
import json

from django.test import TestCase
from django.db.utils import IntegrityError
from django.db import transaction

from ozpcenter import models
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
        f.GroupFactory.create(name='USER')
        f.GroupFactory.create(name='ORG_STEWARD')
        f.GroupFactory.create(name='APPS_MALL_STEWARD')
        f.ProfileFactory.create(user__username='bob', display_name='Bob B',
            user__email='bob@bob.com', dn='bob')
        f.ProfileFactory.create(user__username='alice')
        unclass = 'UNCLASSIFIED'

        img_type = models.ImageType(name='listing_small_icon')
        img_type.save()

        icon = models.Image(file_extension='png',
            security_marking=unclass,
            image_type=models.ImageType.objects.get(name='listing_small_icon'))
        icon.save()

        f.AgencyFactory.create(title='Three Letter Agency', short_name='TLA',
            icon=icon)

    def test_unique_constraints(self):
        # example of how to test that exceptions are raised:
        # http://stackoverflow.com/questions/21458387/transactionmanagementerror-you-cant-execute-queries-until-the-end-of-the-atom
        try:
            with transaction.atomic():
                f.ProfileFactory.create(user__username='bob')
            self.assertTrue(0, 'Duplicate username allowed')
        except IntegrityError:
            # this is expected
            pass

        # email nor display name need be unique, so this should pass
        f.ProfileFactory.create(user__username='bob2', display_name='Bob B',
            user__email='bob@bob.com', dn='bob2')

    def test_non_factory_save(self):
        """
        Shows how the standard save() method may be invoked on a model objects

        More importantly, this demonstrates a common misconception with django
        model validation. The Profile model requires that the organizations and
        bio fields be present, yet we can save a model without them.

        This is because "constraints" like blank=False apply only to form
        validation, not to the actual database
        """
        test_user = models.Profile.create_user(username='myname',
            display_name='My Name',
            email='myname@me.com',
            access_control=json.dumps({'clearances': ['SOMETHING'], 'formal_accesses': ['ABC']}))
        test_user.save()
        # check that it was saved
        user_found = models.Profile.objects.filter(user__username='myname').count()
        self.assertEqual(1, user_found)
        # note that the model object was saved successfully even though some
        # "required" fields were not present

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
                test_user = models.Profile.create_user(username=uname_long,
                    access_control=json.dumps({'clearances': ['U'], 'formal_accesses': ['ABC']}))
                # this passes if we're using SQLite
                test_user.save()
            # self.assertTrue(0, 'username of excess length allowed')
        except IntegrityError:
            # this is expected for PostgreSQL and MySQL
            pass

    def test_created_date(self):
        pass

    def test_highest_role(self):
        test_user = models.Profile.create_user(username='newguy',
            access_control=json.dumps({'clearances': ['U'], 'formal_accesses': ['ABC']}))
        test_user.save()
        test_user = models.Profile.objects.get(user__username='newguy',
            access_control=json.dumps({'clearances': ['U'], 'formal_accesses': ['ABC']}))
        self.assertEqual(test_user.highest_role(), 'USER')
