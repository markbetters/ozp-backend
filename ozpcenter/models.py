"""
model definitions for ozpcenter

Regarding __str__():
It’s important to add __str__() methods to your models, not only for your own
convenience when dealing with the interactive prompt, but also because objects’
representations are used throughout Django’s automatically-generated admin.
Note that on Python 2, __unicode__() should be defined instead.

By default, fields cannot be null or blank

"""

from enum import Enum
import uuid
import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

import ozpcenter.constants as constants

# User (Profile) roles
class Roles(Enum):
    USER = 1
    ORG_STEWARD = 2
    APPS_MALL_STEWARD = 3


# Listing approval statuses
class ApprovalStatus(Enum):
    IN_PROGRESS = 'In Progress'
    PENDING = 'Pending'
    APPROVED_ORG = 'Approved by Organization'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'


# Action for a Listing Activity
# TODO: Actions also have a description
class Action(Enum):
    CREATED = 'Created'
    MODIFIED = 'Modified'
    SUBMITTED = 'Submitted'
    APPROVED_ORG = 'Approved by Organization'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'
    ENABLED = 'Enabled'
    DISABLED = 'Disabled'
    ADD_RELATED_TO_ITEM = 'Adds as a requirement'
    REMOVE_RELATED_TO_ITEM = 'Removed as a requirement'
    ADD_RELATED_ITEMS = 'New requirements added'
    REMOVE_RELATED_ITEMS = 'Requirements removed'
    REVIEW_EDITED = 'Review Edited'
    REVIEW_DELETED = 'Review Deleted'

    # AML-924 Inside/Outside
    INSIDE = 'Inside'
    OUTSIDE = 'Outside'

class Agency(models.Model):
	"""
	Agency (like of the three letter variety)

	TODO: Auditing for create, update, delete

	Additional db.relationships:
	    * profiles
	    * steward_profiles
	"""
	title = models.CharField(max_length=255, unique=True)
	icon_url = models.CharField(
		max_length=constants.MAX_URL_SIZE,
		validators=[
			RegexValidator(
				regex=constants.URL_REGEX,
				message='icon_url must be a url',
				code='invalid url')]
	)
	short_name = models.CharField(max_length=8, unique=True)
	# listings = db.relationship('Listing', backref='agency')

	def __repr__(self):
		return self.title

	def __str__(self):
		return self.title


class ApplicationLibraryEntry(models.Model):
	"""
	A Listing that a user (Profile) has in their 'application library'/bookmarks

	TODO: Auditing for create, update, delete

	Additional db.relationships:
	    * owner

	TODO: folder seems HUD-specific
	"""
	folder = models.CharField(max_length=255, unique=True)
	owner = models.ForeignKey('Profile', related_name='application_library_entries')
	listing = models.ForeignKey('Listing', related_name='application_library_entries')


class Category(models.Model):
	"""
	Categories for Listings

	TODO: Auditing for create, update, delete
	"""
	title = models.CharField(max_length=50, unique=True)
	desciption = models.CharField(max_length=255)

	def __repr__(self):
	    return self.title

	def __str__(self):
		return self.title


class ChangeDetail(models.Model):
	"""
	A change made to a field of a Listing

	Every time a Listing is modified, a ChangeDetail is created for each field
	that was modified

	Additional db.relationships:
	"""
	field_name = models.CharField(max_length=255)
	old_value = models.CharField(max_length=constants.MAX_VALUE_LENGTH)
	new_value = models.CharField(max_length=constants.MAX_VALUE_LENGTH)
	listing = models.ForeignKey('Listing', related_name='change_details')

	def __repr__(self):
	    return "id:%d field %s was %s now is %s" % (
	        self.id, self.field_name, self.old_value, self.new_value)


class Contact(models.Model):
	"""
    A contact for a Listing

    TODO: Auditing for create, update, delete

    Additional db.relationships:
        * listings
    """
	secure_phone = models.CharField(
		max_length=50,
		validators=[
			RegexValidator(
				regex=constants.PHONE_REGEX,
				message='secure_phone must be a valid phone number',
				code='invalid phone number')]
	)
	unsecure_phone = models.CharField(
		max_length=50,
		validators=[
			RegexValidator(
				regex=constants.PHONE_REGEX,
				message='unsecure_phone must be a valid phone number',
				code='invalid phone number')]
	)
	email = models.CharField(
		max_length=100,
		validators=[
			RegexValidator(
				regex=constants.EMAIL_REGEX,
				message='email must be a valid address',
				code='invalid email')]
	)
	name = models.CharField(max_length=100)
	organization = models.CharField(max_length=100)
	contact_type = models.ForeignKey('ContactType', related_name='contacts')

	def clean(self):
		if not self.secure_phone and not self.unsecure_phone:
			raise ValidationError({'secure_phone': 'Both phone numbers cannot \
				be blank'})

	def __repr__(self):
	    val = '%s, %s' % (self.name, self.email)
	    val += 'organization %s' % (
	        self.organization if self.organization else '')
	    val += 'secure_phone %s' % (
	        self.secure_phone if self.secure_phone else '')
	    val += 'unsecure_phone %s' % (
	        self.unsecure_phone if self.unsecure_phone else '')

	    return val


class DocUrl(models.Model):
	"""
    A documentation link that belongs to a Listing

    Additional db.relationships:
        * listing
    """
	name = models.CharField(max_length=255)
	url = models.CharField(
		max_length=constants.MAX_URL_SIZE,
		validators=[
			RegexValidator(
				regex=constants.URL_REGEX,
				message='url must be a url',
				code='invalid url')]
		)
	listing = models.ForeignKey('Listing', related_name='doc_urls')

	def __repr__(self):
	    return '%s:%s' % (self.name, self.url)

class Profile(models.Model):
	"""
	A User (user's Profile) on OZP

	TODO: Auditing for create, update, delete
	"""
	#application_library = db.relationship('ApplicationLibraryEntry',
	#                                      backref='owner')
	username = models.CharField(max_length=255, unique=True)
	display_name = models.CharField(max_length=255)
	email = models.CharField(max_length=255)
	bio = models.CharField(max_length=1000)
	created_date = models.DateTimeField(auto_now_add=True)
	last_login = models.DateTimeField()
	ROLE_CHOICES = (
		(Roles.USER, 'USER'),
		(Roles.ORG_STEWARD, 'ORG_STEWARD'),
		(Roles.APPS_MALL_STEWARD, 'ADMIN')
	)
	highest_role = models.PositiveSmallIntegerField(
		choices=ROLE_CHOICES,
		default=Roles.USER.value)
	organizations = models.ManyToManyField(
		Agency,
		related_name='profiles',
		db_table='agency_profile')
	stewarded_organizations = models.ManyToManyField(
		Agency,
		related_name='stewarded_profiles',
		db_table='stewarded_agency_profile')
	# iwc_data_objects = db.relationship('IwcDataObject', backref='profile')
	# listing_activities = db.relationship('ListingActivity', backref='profile')
	# rejection_listings = db.relationship('RejectionListing', backref='author')


class Listing(models.Model):
	"""
	Listing
	"""
	title = models.CharField(max_length=255, unique=True)
	approved_date = models.DateTimeField(null=True)
	agency = models.ForeignKey(Agency, related_name='listings')


	def __repr__(self):
		return self.title

	def __str__(self):
		return self.title
