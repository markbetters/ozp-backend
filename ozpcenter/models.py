# -*- coding: utf-8 -*-
"""
model definitions for ozpcenter

"""
import logging
import os
import uuid

import django.contrib.auth
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.validators import RegexValidator
from django.db import models
from django.forms import ModelForm
from django.conf import settings

from PIL import Image

import ozpcenter.constants as constants
import ozpcenter.access_control as access_control

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

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


class ImageType(models.Model):
    """
    Image types (as in Small Screenshot, not png)

    This data should be rather static, but is convenient to place in the DB

    listing_small_icon: 16x16
    listing_large_icon: 32x32
    listing_banner_icon: 220x137
    listing_large_banner_icon: 600x376
    listing_small_screenshot: 600x376
    listing_large_screenshot: 960x600
    """
    SMALL_ICON = 'small_icon'
    LARGE_ICON = 'large_icon'
    BANNER_ICON = 'banner_icon'
    LARGE_BANNER_ICON = 'large_banner_icon'
    SMALL_SCREENSHOT = 'small_screenshot'
    LARGE_SCREENSHOT = 'large_screenshot'
    NAME_CHOICES = (
        (SMALL_ICON, 'small_icon'),
        (LARGE_ICON, 'large_icon'),
        (BANNER_ICON, 'banner_icon'),
        (LARGE_BANNER_ICON, 'large_banner_icon'),
        (SMALL_SCREENSHOT, 'small_screenshot'),
        (LARGE_SCREENSHOT, 'large_screenshot'),
    )

    name = models.CharField(max_length=64, choices=NAME_CHOICES, unique=True)
    max_size_bytes = models.IntegerField(default=1048576)
    max_width = models.IntegerField(default=2048)
    max_height = models.IntegerField(default=2048)
    min_width = models.IntegerField(default=16)
    min_height = models.IntegerField(default=16)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class AccessControlImageManager(models.Manager):
    """
    Use a custom manager to control access to Images

    Instead of using models.Image.objects.all() or .filter(...) etc, use:
    models.Image.objects.for_user(user).all() or .filter(...) etc

    This way there is a single place to implement this 'tailored view' logic
    for image queries
    """
    def for_user(self, username):
        # get all images
        objects = super(AccessControlImageManager, self).get_queryset()
        user = Profile.objects.get(user__username=username)
        # filter out listings by user's access level
        images_to_exclude=[]
        for i in objects:
            if not access_control.has_access(user.access_control.title, i.access_control.title):
                images_to_exclude.append(i.id)
        objects = objects.exclude(id__in=images_to_exclude)
        return objects


class Image(models.Model):
    """
    Image

    (Uploaded) images are stored in a flat directory on the server using a
    filename like <id>_<image_type>.png

    When creating a new image, use the Image.create_image method, do not
    use the Image.save() directly

    Note that these images are access controlled, and as such cannot simply
    be statically served
    """
    # this is set automatically by the create_image method
    # TODO: we don't use this, but removiing it causes problems (unit tests
    # segfault. keeping it around doesn't hurt anything, and it could be
    # useful later)
    uuid = models.CharField(max_length=36, unique=True)
    access_control = models.ForeignKey(AccessControl, related_name='images')
    file_extension = models.CharField(max_length=16, default='png')
    image_type = models.ForeignKey(ImageType, related_name='images')

    # use a custom Manager class to limit returned Images
    objects = AccessControlImageManager()

    def __repr__(self):
        return str(self.id)

    def __str__(self):
        return str(self.id)

    @staticmethod
    def create_image(pil_img, **kwargs):
        """
        Given an image (PIL format) and some metadata, write to file sys and
        create DB entry

        pil_img: PIL.Image (see https://pillow.readthedocs.org/en/latest/reference/Image.html)
        """
        # get DB info for image
        random_uuid = str(uuid.uuid4())
        ac = kwargs.get('access_control', 'UNCLASSIFIED')
        access_control = AccessControl.objects.get(title=ac)
        file_extension = kwargs.get('file_extension', 'png')
        valid_extensions = constants.VALID_IMAGE_TYPES
        if file_extension not in valid_extensions:
            logger.error('Invalid image type: %s' % file_extension)
            # TODO: raise exception?
            return

        image_type = kwargs.get('image_type', None)
        if not image_type:
            logger.error('No image_type provided')
            # TODO raise exception?
            return
        image_type = ImageType.objects.get(name=image_type)

        # create database entry
        img = Image(uuid=random_uuid, access_control=access_control,
            file_extension=file_extension, image_type=image_type)
        img.save()

        # write the image to the file system
        file_name = settings.MEDIA_ROOT + str(img.id) + '_' + img.image_type.name + '.' + file_extension
        # logger.debug('saving image %s' % file_name)
        pil_img.save(file_name)

        # check size requirements
        size_bytes = os.path.getsize(file_name)
        if size_bytes > image_type.max_size_bytes:
            logger.error('Image size is %d bytes, which is larger than the max \
                allowed %d bytes' % (size_bytes, image_type.max_size_bytes))
            # TODO raise exception and remove file
            return

        # TODO: check width and height

        return img


class Tag(models.Model):
    """
    Tag name (for a listing)

    TODO: this will work differently than legacy
    """
    name = models.CharField(max_length=16, unique=True)

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
    icon = models.ForeignKey(Image, related_name='agency', null=True,
        blank=True)

    short_name = models.CharField(max_length=8, unique=True)

    def __repr__(self):
        return self.title

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "agencies"


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
    folder = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ForeignKey('Profile', related_name='application_library_entries')
    listing = models.ForeignKey('Listing', related_name='application_library_entries')

    def __str__(self):
        return '%s:%s:%s' % (self.folder, self.owner.user.username,
            self.listing.title)

    def __repr__(self):
        return '%s:%s:%s' % (self.folder, self.owner.user.username,
            self.listing.title)

    class Meta:
        verbose_name_plural = "application library entries"


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

    class Meta:
        verbose_name_plural = "categories"


class ChangeDetail(models.Model):
    """
    A change made to a field of a Listing

    Every time a Listing is modified, a ChangeDetail is created for each field
    that was modified

    Additional db.relationships:
        * ListingActivity (ManyToMany)
    """
    field_name = models.CharField(max_length=255)
    old_value = models.CharField(max_length=constants.MAX_VALUE_LENGTH,
        blank=True, null=True)
    new_value = models.CharField(max_length=constants.MAX_VALUE_LENGTH,
        blank=True, null=True)

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
                code='invalid phone number')],
        null=True
    )
    unsecure_phone = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex=constants.PHONE_REGEX,
                message='unsecure_phone must be a valid phone number',
                code='invalid phone number')],
        null=True
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
    organization = models.CharField(max_length=100, null=True)
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

    def __str__(self):
        return '%s: %s' % (self.name, self.email)


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

    # TODO: unique_together constraint on name and url
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

    def __str__(self):
        return '%s: %s' % (self.name, self.url)


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
    icon = models.ForeignKey(Image, related_name='intent')

    def __repr__(self):
        return '%s/%s' % (self.type, self.action)

    def __str__(self):
        return self.action

class AccessControlReviewManager(models.Manager):
    """
    Use a custom manager to control access to Reviews

    Instead of using models.Review.objects.all() or .filter(...) etc, use:
    models.Review.objects.for_user(user).all() or .filter(...) etc

    This way there is a single place to implement this 'tailored view' logic
    for review queries
    """
    def for_user(self, username):
        # get all reviews
        all_reviews = super(AccessControlReviewManager, self).get_queryset()
        # get all listings for this user
        listings = Listing.objects.for_user(username).all()
        # filter out reviews for listings this user cannot see
        filtered_reviews = all_reviews.filter(listing__in=listings)
        return filtered_reviews


class Review(models.Model):
    """
    A review made on a Listing
    """
    text = models.CharField(max_length=constants.MAX_VALUE_LENGTH,
        blank=True, null=True)
    rate = models.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
        ]
    )
    listing = models.ForeignKey('Listing', related_name='reviews')
    author = models.ForeignKey('Profile', related_name='reviews')

    # use a custom Manager class to limit returned Reviews
    objects = AccessControlReviewManager()

    def __repr__(self):
        return '%s: rate: %d text: %s' % (self.author.user.username,
                                                     self.rate, self.text)

    def __str__(self):
        return '%s: rate: %d text: %s' % (self.author.user.username,
                                                     self.rate, self.text)

    class Meta:
        # a user can only have one review per listing
        unique_together = ('author', 'listing')


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
        return 'Profile: %s' % self.user.username

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
        # if this user is an ORG_STEWARD or APPS_MALL_STEWARD, give them
        # access to the admin site
        groups = kwargs.get('groups', ['USER'])
        if 'ORG_STEWARD' in groups or 'APPS_MALL_STEWARD' in groups:
            user = django.contrib.auth.models.User.objects.create_superuser(
                username=username, email=email, password=password)
            user.save()
            # logger.warn('creating superuser: %s, password: %s' % (username, password))
        else:
            user = django.contrib.auth.models.User.objects.create_user(
                username=username, email=email, password=password)
            user.save()
            # logger.info('creating user: %s' % username)

        # add user to group(s) (i.e. Roles - USER, ORG_STEWARD,
        # APPS_MALL_STEWARD). If no specific Group is provided, we
        # will default to USER
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
            if not i.access_control:
                logger.error('Listing %s has no access_control' % i.title)
            if not access_control.has_access(user.access_control.title, i.access_control.title):
                titles_to_exclude.append(i.title)
        objects = objects.exclude(title__in=titles_to_exclude)
        return objects


class Listing(models.Model):
    """
    Listing

    To allow users to save Listings in an incompleted state, most of the fields
    in this model are nullable, even though that's not valid for a finalized
    listing
    """
    # Approval Statuses
    # This is the Djangoy mechanism for doing CHOICES fields:
    # https://docs.djangoproject.com/en/1.8/ref/models/fields/#choices
    IN_PROGRESS = 'IN_PROGRESS'
    PENDING = 'PENDING'
    APPROVED_ORG = 'APPROVED_BY_ORG'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    APPROVAL_STATUS_CHOICES = (
        (IN_PROGRESS, 'IN_PROGRESS'),
        (PENDING, 'PENDING'),
        (APPROVED_ORG, 'APPROVED_ORG'),
        (APPROVED, 'APPROVED'),
        (REJECTED, 'REJECTED')
    )

    title = models.CharField(max_length=255, unique=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    agency = models.ForeignKey(Agency, related_name='listings')
    listing_type = models.ForeignKey('ListingType', related_name='listings',
        null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    launch_url = models.CharField(
        max_length=constants.MAX_URL_SIZE,
        validators=[
            RegexValidator(
                regex=constants.URL_REGEX,
                message='launch_url must be a url',
                code='invalid url')
        ], null=True, blank=True
    )
    version_name = models.CharField(max_length=255, null=True, blank=True)
    # NOTE: replacing uuid with this - will need to add to the form
    unique_name = models.CharField(max_length=255, unique=True, null=True,
        blank=True)
    small_icon = models.ForeignKey(Image, related_name='listing_small_icon',
        null=True, blank=True)
    large_icon = models.ForeignKey(Image, related_name='listing_large_icon',
        null=True, blank=True)
    banner_icon = models.ForeignKey(Image, related_name='listing_banner_icon',
        null=True, blank=True)
    large_banner_icon = models.ForeignKey(Image,
        related_name='listing_large_banner_icon', null=True, blank=True)


    what_is_new = models.CharField(max_length=255, null=True, blank=True)
    description_short = models.CharField(max_length=150, null=True, blank=True)
    requirements = models.CharField(max_length=1000, null=True, blank=True)
    approval_status = models.CharField(max_length=255,
        choices=APPROVAL_STATUS_CHOICES, default=IN_PROGRESS)
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
    total_reviews = models.IntegerField(default=0)
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

    required_listings = models.ForeignKey('self', null=True, blank=True)
    # no reverse relationship - use '+'
    last_activity = models.OneToOneField('ListingActivity', related_name='+',
        null=True, blank=True)

    intents = models.ManyToManyField(
        'Intent',
        related_name='listings',
        db_table='intent_listing'
    )

    access_control = models.ForeignKey(AccessControl, related_name='listings',
        null=True, blank=True)

    # private listings can only be viewed by members of the same agency
    is_private = models.BooleanField(default=False)

    # use a custom Manager class to limit returned Listings
    objects = AccessControlListingManager()

    def __repr__(self):
        return self.title

    def __str__(self):
        return self.title


class AccessControlListingActivityManager(models.Manager):
    """
    Use a custom manager to control access to ListingActivities

    Instead of using models.ListingActivity.objects.all() or .filter(...) etc,
    use: models.ListingActivity.objects.for_user(user).all() or .filter(...) etc

    This way there is a single place to implement this 'tailored view' logic
    for ListingActivity queries
    """
    def for_user(self, username):
        # get all activities
        all_activities = super(
            AccessControlListingActivityManager, self).get_queryset()
        # get all listings for this user
        listings = Listing.objects.for_user(username).all()
        # filter out listing_activities for listings this user cannot see
        filtered_listing_activities = all_activities.filter(
            listing__in=listings)
        return filtered_listing_activities


class ListingActivity(models.Model):
    """
    Listing Activity
    """
    # Actions
    # listing is initially created
    CREATED = 'CREATED'
    # field of a listing is modified - has a corresponding ChangeDetail entry
    MODIFIED = 'MODIFIED'
    # listing is submitted for approval by org steward and apps mall steward
    SUBMITTED = 'SUBMITTED'
    # listing is approved by an org steward
    APPROVED_ORG = 'APPROVED_ORG'
    # listing is approved by apps mall steward (upon previous org steward
        # approval) - it is now visible to users
    APPROVED = 'APPROVED'
    # listing is rejected for approval by org steward or apps mall steward
    REJECTED = 'REJECTED'
    # listing is enabled (visible to users)
    ENABLED = 'ENABLED'
    # listing is disabled (hidden from users)
    DISABLED = 'DISABLED'
    # a review for a listing has been modified
    REVIEW_EDITED = 'REVIEW_EDITED'
    # a review for a listing has been deleted
    REVIEW_DELETED = 'REVIEW_DELETED'

    ACTION_CHOICES = (
        (CREATED, 'CREATED'),
        (MODIFIED, 'MODIFIED'),
        (SUBMITTED, 'SUBMITTED'),
        (APPROVED_ORG, 'APPROVED_ORG'),
        (APPROVED, 'APPROVED'),
        (REJECTED, 'REJECTED'),
        (ENABLED, 'ENABLED'),
        (DISABLED, 'DISABLED'),
        (REVIEW_EDITED, 'REVIEW_EDITED'),
        (REVIEW_DELETED, 'REVIEW_DELETED')
    )

    action = models.CharField(max_length=128, choices=ACTION_CHOICES)
    activity_date = models.DateTimeField(auto_now=True)
    # an optional description of the activity (required if the action is
    #   REJECTED)
    description = models.CharField(max_length=2000, blank=True, null=True)
    author = models.ForeignKey('Profile', related_name='listing_activities')
    listing = models.ForeignKey('Listing', related_name='listing_activities')
    change_details = models.ManyToManyField(
        'ChangeDetail',
        related_name='listing_activity',
        db_table='listing_activity_change_detail'
    )

    # use a custom Manager class to limit returned activities
    objects = AccessControlListingActivityManager()

    def __repr__(self):
        return '%s %s %s at %s' % (self.author.user.username, self.action,
            self.listing.title, self.activity_date)

    def __str__(self):
        return '%s %s %s at %s' % (self.author.user.username, self.action,
            self.listing.title, self.activity_date)

    class Meta:
        verbose_name_plural = "listing activities"


class Screenshot(models.Model):
    """
    A screenshot for a Listing

    TODO: Auditing for create, update, delete

    Additional db.relationships:
        * listing
    """
    small_image = models.ForeignKey(Image, related_name='screenshot_small')
    large_image = models.ForeignKey(Image, related_name='screenshot_large')
    listing = models.ForeignKey('Listing', related_name='screenshots')

    def __repr__(self):
        return '%s: %s, %s' % (self.listing.title, self.large_image.id, self.small_image.id)

    def __str__(self):
        return '%s: %s, %s' % (self.listing.title, self.large_image.id, self.small_image.id)


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
    # TODO: created date
    created_date = models.DateTimeField(auto_now=True)
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

    def __repr__(self):
        return '%s: %s' % (self.author.user.username, self.message)

    def __str__(self):
        return '%s: %s' % (self.author.user.username, self.message)
