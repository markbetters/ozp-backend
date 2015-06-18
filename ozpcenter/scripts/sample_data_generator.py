"""
Creates test data
"""
import os
import sys
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../../')))

import django.contrib.auth

from ozpcenter import models as models

def run():
	"""
	Creates basic sample data
	"""
	# Categories
	cat = models.Category(title="Books and Reference",
		description="Things made of paper")
	cat.save()
	cat = models.Category(title="Business",
		description="For making money")
	cat.save()
	cat = models.Category(title="Education",
		description="Educational in nature")
	cat.save()
	cat = models.Category(title="Entertainment",
		description="For fun")
	cat.save()
	cat = models.Category(title="Tools",
		description="Tools and Utilities")
	cat.save()


	# Contact Types
	p = models.ContactType(name='Worker')
	p.save()
	p = models.ContactType(name='Manager')
	p.save()
	p = models.ContactType(name='Boss')
	p.save()

	# Listing Types
	t = models.ListingType(title='web application',
		description='web applications')
	t.save()
	t = models.ListingType(title='widgets',
		description='widget things')
	t.save()

	# Intents
	# TODO: more realistic data
	i = models.Intent(action='/application/json/view',
		media_type='vnd.ozp-intent-v1+json.json',
		label='view',
		icon='http://www.google.com/intent_view_icon.png')
	i.save()

	# Organizations
	a = models.Agency(title='Ministry of Truth', short_name='m-truth',
		icon_url='http://www.google.com/mot.png')
	a.save()
	a = models.Agency(title='Ministry of Peace', short_name='m-peace',
		icon_url='http://www.google.com/mop.png')
	a.save()
	a = models.Agency(title='Ministry of Love', short_name='m-love',
		icon_url='http://www.google.com/mol.png')
	a.save()

	# Access Controls
	c = models.AccessControl(title='UNCLASSIFIED')
	c.save()
	c = models.AccessControl(title='UNCLASSIFIED//FOUO')
	c.save()
	c = models.AccessControl(title='SECRET')
	c.save()
	c = models.AccessControl(title='TOP SECRET')
	c.save()

	# Org Stewards
	p = models.Profile(username='wsmith', display_name='William Smith',
		email='wsmith@nowhere.com', bio='I work at the Ministry of Truth',
		highest_role=models.Profile.ORG_STEWARD,
		access_control=models.AccessControl.objects.get(title='UNCLASSIFIED'))
	p.save()
	p.organizations.add(models.Agency.objects.get(title='Ministry of Truth'))
	p.stewarded_organizations.add(models.Agency.objects.get(title='Ministry of Truth'))

	# Apps Mall Stewards
	p = models.Profile(username='pboss', display_name='P Boss',
		email='pboss@nowhere.com', bio='I am the boss',
		highest_role=models.Profile.APPS_MALL_STEWARD,
		access_control=models.AccessControl.objects.get(title='UNCLASSIFIED'))
	p.save()

	# Regular user
	p = models.Profile(username='jdoe', display_name='John Doe',
		email='djoe@nowhere.com', bio='Im a normal person',
		highest_role=models.Profile.USER,
		access_control=models.AccessControl.objects.get(title='UNCLASSIFIED'))
	p.save()
	p.organizations.add(models.Agency.objects.get(title='Ministry of Truth'))

	# Notifications

	# Contacts
	c = models.Contact(name='Jimmy John', organization='Jimmy Johns',
		contact_type=models.ContactType.objects.get(name='Manager'),
		email='jimmyjohn@jimmyjohns.com', unsecure_phone='555-555-5555')
	c.save()

	# Listings
	l = models.Listing(
		title='Air Mail',
		agency=models.Agency.objects.get(title='Ministry of Truth'),
		app_type=models.ListingType.objects.get(title='web application'),
		description='Sends mail via air',
		launch_url='https://www.google.com/airmail',
		version_name='1.0.0',
		unique_name='ozp.test.air_mail',
		small_icon='http://www.google.com/small_icon',
		large_icon='http://www.google.com/large_icon',
		banner_icon='http://www.google.com/banner_icon',
		large_banner_icon='http://www.google.com/large_banner_icon',
		what_is_new='Nothing really new here',
		description_short='Sends airmail',
		requirements='None',
		approval_status=models.ApprovalStatus.APPROVED,
		is_enabled=True,
		is_featured=True,
		singleton=False,
		access_control=models.AccessControl.objects.get(title='UNCLASSIFIED')
	)
	l.save()
	l.contacts.add(models.Contact.objects.get(name='Jimmy John'))

	l = models.Listing(
		title='Bread Basket',
		agency=models.Agency.objects.get(title='Ministry of Truth'),
		app_type=models.ListingType.objects.get(title='web application'),
		description='Carries delicious bread',
		launch_url='https://www.google.com/breadbasket',
		version_name='1.0.0',
		unique_name='ozp.test.bread_basket',
		small_icon='http://www.google.com/small_icon',
		large_icon='http://www.google.com/large_icon',
		banner_icon='http://www.google.com/banner_icon',
		large_banner_icon='http://www.google.com/large_banner_icon',
		what_is_new='Nothing really new here',
		description_short='Carries bread',
		requirements='None',
		approval_status=models.ApprovalStatus.APPROVED,
		is_enabled=True,
		is_featured=True,
		singleton=False,
		access_control=models.AccessControl.objects.get(title='UNCLASSIFIED')
	)
	l.save()
	l.contacts.add(models.Contact.objects.get(name='Jimmy John'))

	l = models.Listing(
		title='Cupid',
		agency=models.Agency.objects.get(title='Ministry of Love'),
		app_type=models.ListingType.objects.get(title='web application'),
		description='Find your match',
		launch_url='https://www.google.com/cupid',
		version_name='1.0.0',
		unique_name='ozp.test.cupid',
		small_icon='http://www.google.com/small_icon',
		large_icon='http://www.google.com/large_icon',
		banner_icon='http://www.google.com/banner_icon',
		large_banner_icon='http://www.google.com/large_banner_icon',
		what_is_new='Nothing really new here',
		description_short='Cupid stuff',
		requirements='None',
		approval_status=models.ApprovalStatus.APPROVED,
		is_enabled=True,
		is_featured=True,
		singleton=False,
		is_private=True,
		access_control=models.AccessControl.objects.get(title='UNCLASSIFIED')
	)
	l.save()
	l.contacts.add(models.Contact.objects.get(name='Jimmy John'))
	# add screenshots
	s = models.Screenshot(small_image_url='http://www.google.com/air_mail.png',
		large_image_url='http://www.google.com/air_mail.png',
		listing=models.Listing.objects.get(title='Air Mail'))
	s.save()
	# add intents
	l.intents.add(models.Intent.objects.get(action='/application/json/view'))

	# bookmark listings
	a = models.ApplicationLibraryEntry(
		owner=models.Profile.objects.get(username='wsmith'),
		listing=models.Listing.objects.get(unique_name='ozp.test.bread_basket'))
	a.save()

	a = models.ApplicationLibraryEntry(
		owner=models.Profile.objects.get(username='wsmith'),
		listing=models.Listing.objects.get(unique_name='ozp.test.air_mail'))
	a.save()

	# add django users corresponding to Profiles
	django.contrib.auth.models.User.objects.create_user(username='wsmith',
		email='wmsith@google.com', password='password')
	django.contrib.auth.models.User.objects.create_superuser(username='admin',
		password='password', email='admin@admin.com')
	django.contrib.auth.models.User.objects.create_superuser(username='jdoe',
		password='password', email='jdoe@nowhere.com')

def get_categories():
	cats = models.Category.objects.all()
	print('categories: ' + str(cats))

if __name__ == "__main__":
	run()