# -*- coding: utf-8 -*-
"""
model definitions for ozpcenter

"""
import logging

import django.contrib.auth
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.validators import RegexValidator
from django.db import models
from django.forms import ModelForm
from django.conf import settings

# plugin for enum support https://github.com/5monkeys/django-enumfield
from django_enumfield import enum

import ozpcenter.constants as constants
import ozpcenter.access_control as access_control

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

# Listing approval statuses
class ApprovalStatus(enum.Enum):
    IN_PROGRESS = 'In Progress'
    PENDING = 'Pending'
    APPROVED_ORG = 'Approved by Organization'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'


# Action for a Listing Activity
# TODO: Actions also have a description
class Action(enum.Enum):
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


class AccessControl(models.Model):
	"""
	Access levels (classifications)

	Format: <CLASSIFICATION>//CONTROL1//CONTROL2//...
	"""
	title = models.CharField(max_length=1024, unique=True)

	def __repr__(self):
		return self.title

	def __str__(self):
		return self.title

class Icon(models.Model):
	"""
	Icon
	"""
	icon_url = models.CharField(
		max_length=constants.MAX_URL_SIZE,
		validators=[
			RegexValidator(
				regex=constants.URL_REGEX,
				message='icon url must be a url',
				code='invalid url')]
	)
	access_control = models.ForeignKey(AccessControl, related_name='icons')

class Tag(models.Model):
	"""
	Tag name (for a listing)
	"""
	name = models.CharField(max_length=16)

	def __repr__(self):
		return self.name

	def __str__(self):
		return self.name


class Agency(models.Model):
	"""
	Agency (like of the three letter variety)

	TODO: Auditing for create, update, delete

	Additional db.relationships:
	    * profiles
	    * steward_profiles
	"""
	title = models.CharField(max_length=255, unique=True)
	icon = models.ForeignKey(Icon, related_name='agency')

	short_name = models.CharField(max_length=8, unique=True)

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

	TODO: should we allow multiple bookmarks of the same listing (perhaps
		in different folders)?
	"""
	folder = models.CharField(max_length=255, blank=True)
	owner = models.ForeignKey('Profile', related_name='application_library_entries')
	listing = models.ForeignKey('Listing', related_name='application_library_entries')

	def __str__(self):
		return self.folder


class Category(models.Model):
	"""
	Categories for Listings

	TODO: Auditing for create, update, delete
	"""
	title = models.CharField(max_length=50, unique=True)
	description = models.CharField(max_length=255)

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
	# TODO: add a date/time field?

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


class ContactType(models.Model):
	"""
	Contact Type

	Examples: TechnicalPOC, GovieGuy, etc

	TODO: Auditing for create, update, delete
	"""
	name = models.CharField(max_length=50, unique=True)
	required = models.BooleanField(default=False)

	def __repr__(self):
	    return self.title


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


class Intent(models.Model):
	"""
	An Intent is an abstract description of an operation to be performed

	TODO: Auditing for create, update, delete
	"""
	# TODO unique on type
	action = models.CharField(
		max_length=64,
		validators=[
			RegexValidator(
				regex=constants.INTENT_ACTION_REGEX,
				message='action must be a valid action',
				code='invalid action')]
	)
	media_type = models.CharField(
		max_length=129,
		validators=[
			RegexValidator(
				regex=constants.MEDIA_TYPE_REGEX,
				message='type must be a valid media type',
				code='invalid type')]
	)
	label = models.CharField(max_length=255)
	icon = models.ForeignKey(Icon, related_name='intent')

	def __repr__(self):
	    return '%s/%s' % (self.type, self.action)


class ItemComment(models.Model):
	"""
	A comment made on a Listing
	"""
	text = models.CharField(max_length=constants.MAX_VALUE_LENGTH)
	rate = models.IntegerField(validators=[
		MinValueValidator(1),
		MaxValueValidator(5)
		]
	)
	listing = models.ForeignKey('Listing', related_name='item_comments')
	author = models.ForeignKey('Profile', related_name='item_comments')

	def __repr__(self):
	    return 'Author id %s: Rate %d Stars : %s' % (self.author_id,
	                                                 self.rate, self.text)

class Profile(models.Model):
	"""
	A User (user's Profile) on OZP

	Note that some information (username, email, last_login, date_joined) is
	held in the associated Django User model. In addition, the user's role
	(USER, ORG_STEWARD, or APPS_MALL_STEWARD) is represented by the Group
	associated with the Django User model

	Notes on use of contrib.auth.models.User model:
		* first_name and last_name are not used
		* is_superuser is always set to False
		* is_staff is set to True for Org Stewards and Apps Mall Stewards
		* password is only used in development. On production, client SSL certs
			are used, and so password is set to TODO: TBD

	TODO: Auditing for create, update, delete
	"""
	#application_library = db.relationship('ApplicationLibraryEntry',
	#                                      backref='owner')
	display_name = models.CharField(max_length=255)
	bio = models.CharField(max_length=1000, blank=True)
	organizations = models.ManyToManyField(
		Agency,
		related_name='profiles',
		db_table='agency_profile')
	stewarded_organizations = models.ManyToManyField(
		Agency,
		related_name='stewarded_profiles',
		db_table='stewarded_agency_profile',
		blank=True)

	access_control = models.ForeignKey(AccessControl, related_name='profiles')

	# instead of overriding the builtin Django User model used
	# for authentication, we extend it
	# https://docs.djangoproject.com/en/1.8/topics/auth/customizing/#extending-the-existing-user-model
	user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True,
		blank=True)

	# TODO
	# iwc_data_objects = db.relationship('IwcDataObject', backref='profile')

	# TODO: on create, update, or delete, do the same for the related
	# django_user

	def __repr__(self):
	    return self.user.username

	def __str__(self):
		return self.user.username

	@staticmethod
	def create_groups():
		"""
		Groups are used as Roles, and as such are relatively static, hence
		their declaration here (NOTE that this must be invoked manually
		after the server has started)
		"""
		# create the different Groups (Roles) of users
		group = django.contrib.auth.models.Group.objects.create(
			name='USER')
		group = django.contrib.auth.models.Group.objects.create(
			name='ORG_STEWARD')
		group = django.contrib.auth.models.Group.objects.create(
			name='APPS_MALL_STEWARD')

	def highest_role(self):
		"""
		APPS_MALL_STEWARD > ORG_STEWARD > USER
		"""
		groups = self.user.groups.all()
		group_names = [i.name for i in groups]

		if 'APPS_MALL_STEWARD' in group_names:
			return 'APPS_MALL_STEWARD'
		elif 'ORG_STEWARD' in group_names:
			return 'ORG_STEWARD'
		elif 'USER' in group_names:
			return 'USER'
		else:
			# TODO: raise exception?
			logger.error('User %s has invalid Group' % self.user.username)
			return ''

	@staticmethod
	def create_user(username, **kwargs):
		"""
		Create a new User and Profile object

		kwargs:
			password
			display_name
			bio
			access_control (models.access_control.title)
			organizations (['org1_title', 'org2_title'])
			stewarded_organizations (['org1_title', 'org2_title'])
			groups (['group1_name', 'group2_name'])

		"""
		# TODO: what to make default password?
		password = kwargs.get('password', 'password')

		email = kwargs.get('email', '')

		# create User object
		user = django.contrib.auth.models.User.objects.create_user(
			username=username, password=password, email=email)
		user.save()

		# add user to group(s) (i.e. Roles - USER, ORG_STEWARD,
		# APPS_MALL_STEWARD). If no specific Group is provided, we
		# will default to USER
		groups = kwargs.get('groups', ['USER'])
		for i in groups:
			g = django.contrib.auth.models.Group.objects.get(name=i)
			user.groups.add(g)

		# get additional profile information
		display_name = kwargs.get('display_name', username)
		bio = kwargs.get('password', '')
		ac = kwargs.get('access_control', 'UNCLASSIFIED')
		access_control = AccessControl.objects.get(title=ac)

		# create the profile object and associate it with the User
		p = Profile(display_name=display_name,
			bio=bio,
			access_control=access_control,
			user=user
		)
		p.save()

		# add organizations
		organizations = kwargs.get('organizations', [])
		for i in organizations:
			org = Agency.objects.get(title=i)
			p.organizations.add(org)

		# add stewarded organizations
		organizations = kwargs.get('stewarded_organizations', [])
		for i in organizations:
			org = Agency.objects.get(title=i)
			p.stewarded_organizations.add(org)

		return p


class AccessControlListingManager(models.Manager):
	"""
	Use a custom manager to control access to Listings

	Instead of using models.Listing.objects.all() or .filter(...) etc, use:
	models.Listing.objects.for_user(user).all() or .filter(...) etc

	This way there is a single place to implement this 'tailored view' logic
	for listing queries
	"""
	def for_user(self, username):
		# get all listings
		objects = super(AccessControlListingManager, self).get_queryset()
		# filter out private listings
		user = Profile.objects.get(user__username=username)
		user_orgs = user.organizations.all()
		user_orgs = [i.title for i in user_orgs]
		# get all agencies for which this user is not a member
		exclude_orgs = Agency.objects.exclude(title__in=user_orgs)
		objects = objects.exclude(is_private=True,
			agency__in=exclude_orgs)
		# filter out listings by user's access level
		titles_to_exclude=[]
		for i in objects:
			if not access_control.has_access(user.access_control.title, i.access_control.title):
				titles_to_exclude.append(i.title)
		objects = objects.exclude(title__in=titles_to_exclude)
		return objects


class Listing(models.Model):
	"""
	Listing
	"""
	title = models.CharField(max_length=255, unique=True)
	approved_date = models.DateTimeField(null=True)
	agency = models.ForeignKey(Agency, related_name='listings')
	app_type = models.ForeignKey('ListingType', related_name='listings')
	description = models.CharField(max_length=255)
	launch_url = models.CharField(
		max_length=constants.MAX_URL_SIZE,
		validators=[
			RegexValidator(
				regex=constants.URL_REGEX,
				message='launch_url must be a url',
				code='invalid url')]
	)
	version_name = models.CharField(max_length=255)
	# NOTE: replacing uuid with this
	unique_name = models.CharField(max_length=255, unique=True)
	small_icon = models.ForeignKey(Icon, related_name='listing_small_icon')
	large_icon = models.ForeignKey(Icon, related_name='listing_large_icon')
	banner_icon = models.ForeignKey(Icon, related_name='listing_banner_icon')
	large_banner_icon = models.ForeignKey(Icon, related_name='listing_large_banner_icon')


	what_is_new = models.CharField(max_length=255)
	description_short = models.CharField(max_length=150)
	requirements = models.CharField(max_length=1000)
	approval_status = models.CharField(max_length=255) # one of enum ApprovalStatus
	is_enabled = models.BooleanField(default=True)
	is_featured = models.BooleanField(default=False)
	# a weighted average (5*total_rate5 + 4*total_rate4 + ...) / total_votes
	avg_rate = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
	total_votes = models.IntegerField(default=0)
	total_rate5 = models.IntegerField(default=0)
	total_rate4 = models.IntegerField(default=0)
	total_rate3 = models.IntegerField(default=0)
	total_rate2 = models.IntegerField(default=0)
	total_rate1 = models.IntegerField(default=0)
	total_comments = models.IntegerField(default=0)
	singleton = models.BooleanField(default=False)

	contacts = models.ManyToManyField(
		'Contact',
		related_name='listings',
		db_table='contact_listing'
	)

	owners = models.ManyToManyField(
		'Profile',
		related_name='owned_listings',
		db_table='profile_listing'
	)

	categories = models.ManyToManyField(
		'Category',
		related_name='listings',
		db_table='category_listing'
	)

	tags = models.ManyToManyField(
		'Tag',
		related_name='listings',
		db_table='tag_listing'
	)

	required_listings = models.ForeignKey('self', null=True)
	# TODO: name/use of related name?
	last_activity = models.ForeignKey('ListingActivity',
		related_name='most_recent_listings', null=True)

	intents = models.ManyToManyField(
		'Intent',
		related_name='listings',
		db_table='intent_listing'
	)

	access_control = models.ForeignKey(AccessControl, related_name='listings')

	# private listings can only be viewed by members of the same agency
	is_private = models.BooleanField(default=False)

	# use a custom Manager class to limit returned Listings
	objects = AccessControlListingManager()


	def __repr__(self):
		return self.title

	def __str__(self):
		return self.title



class ListingActivity(models.Model):
	"""
	Listing Activity

	Additional db.relationships:
	    * listing
	    * profile
	"""
	action = models.CharField(max_length=255) # one of an enum of Action
	activity_date = models.DateTimeField()
	# TODO: how to handle last_activity?
	listing = models.ForeignKey('Listing', related_name='listing_activities')
	profile = models.ForeignKey('Profile', related_name='listing_activities')

class RejectionListing(models.Model):
	"""
	An admin can reject a submitted Listing, thus creating a Rejection Listing

	TODO: Auditing for create, update, delete

	Rejection Listings are referenced by RejectionActivities, and thus never
	removed even after the Listing is approved. They are just ignored if the
	ApprovalState of the Listing is APPROVED

	Additional db.relationships:
	    * listing
	    * author
	"""
	listing = models.ForeignKey('Listing', related_name='rejection_listings')
	author = models.ForeignKey('Profile', related_name='rejection_listings')
	description = models.CharField(max_length=2000)


class Screenshot(models.Model):
	"""
	A screenshot for a Listing

	TODO: Auditing for create, update, delete

	Additional db.relationships:
	    * listing
	"""
	small_image = models.ForeignKey(Icon, related_name='screenshot_small')
	large_image = models.ForeignKey(Icon, related_name='screenshot_large')
	listing = models.ForeignKey('Listing', related_name='screenshots')

	def __repr__(self):
	    return '%s, %s' % (self.large_image_url, self.small_image_url)

	def __str__(self):
	    return '%s, %s' % (self.large_image_url, self.small_image_url)


class ListingType(models.Model):
	"""
	The type of a Listing

	In NextGen OZP, only two listing types are supported: web apps and widgets

	TODO: Auditing for create, update, delete
	"""
	title = models.CharField(max_length=50, unique=True)
	description = models.CharField(max_length=255)

	def __repr__(self):
	    return self.title

	def __str__(self):
	    return self.title

class Notification(models.Model):
	"""
	A notification. Can optionally belong to a specific application

	Notifications that do not have an associated listing are assumed to be
	'system-wide', and thus will be sent to all users
	"""
	message = models.CharField(max_length=1024)
	expires_date = models.DateTimeField()
	author = models.ForeignKey(Profile, related_name='authored_notifications')
	dismissed_by = models.ManyToManyField(
		'Profile',
		related_name='dismissed_notifications',
		db_table='notification_profile'
	)
	listing = models.ForeignKey(Listing, related_name='notifications',
		null=True, blank=True)

