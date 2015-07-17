"""
Creates test data
"""
import datetime
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../../')))

import pytz

import django.contrib.auth

from ozpcenter import models as models
from ozpcenter import model_access

TEST_IMG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_images') + '/'

def run():
    """
    Creates basic sample data
    """
    # Create Groups
    models.Profile.create_groups()

    ############################################################################
    #                           Access Controls
    ############################################################################
    unclass = models.AccessControl(title='UNCLASSIFIED')
    unclass.save()
    c = models.AccessControl(title='UNCLASSIFIED//ABC')
    c.save()
    c = models.AccessControl(title='SECRET')
    c.save()
    c = models.AccessControl(title='TOP SECRET')
    c.save()

    ############################################################################
    #                           Categories
    ############################################################################
    cat1 = models.Category(title="Books and Reference",
        description="Things made of paper")
    cat1.save()
    cat2 = models.Category(title="Business",
        description="For making money")
    cat2.save()
    cat = models.Category(title="Education",
        description="Educational in nature")
    cat.save()
    cat = models.Category(title="Entertainment",
        description="For fun")
    cat.save()
    cat = models.Category(title="Tools",
        description="Tools and Utilities")
    cat.save()


    ############################################################################
    #                           Contact Types
    ############################################################################
    p = models.ContactType(name='Worker')
    p.save()
    p = models.ContactType(name='Manager')
    p.save()
    p = models.ContactType(name='Boss')
    p.save()

    ############################################################################
    #                           Listing Types
    ############################################################################
    t = models.ListingType(title='web application',
        description='web applications')
    t.save()
    t = models.ListingType(title='widgets',
        description='widget things')
    t.save()

    ############################################################################
    #                           Image Types
    ############################################################################
    # Note: these image sizes do not represent those that should be used in
    # production
    t = models.ImageType(name='listing_small_icon', max_size_bytes='4096')
    t.save()
    t = models.ImageType(name='listing_large_icon', max_size_bytes='8192')
    t.save()
    t = models.ImageType(name='listing_banner_icon', max_size_bytes='2097152')
    t.save()
    t = models.ImageType(name='listing_large_banner_icon',
        max_size_bytes='2097152')
    t.save()
    t = models.ImageType(name='listing_small_screenshot',
        max_size_bytes='1048576')
    t.save()
    t = models.ImageType(name='listing_large_screenshot',
        max_size_bytes='1048576')
    t.save()
    t = models.ImageType(name='intent_icon', max_size_bytes='2097152')
    t.save()
    t = models.ImageType(name='agency_icon', max_size_bytes='2097152')
    t.save()

    ############################################################################
    #                           Intents
    ############################################################################
    # TODO: more realistic data
    img = Image.open(TEST_IMG_PATH + 'android.png')
    icon = models.Image.create_image(img, file_extension='png',
        access_control='UNCLASSIFIED', image_type='intent_icon')
    i = models.Intent(action='/application/json/view',
        media_type='vnd.ozp-intent-v1+json.json',
        label='view',
        icon=icon)
    i.save()

    ############################################################################
    #                           Organizations
    ############################################################################
    img = Image.open(TEST_IMG_PATH + 'ministry_of_truth.jpg')
    icon = models.Image.create_image(img, file_extension='jpg',
        access_control='UNCLASSIFIED', image_type='agency_icon')
    a = models.Agency(title='Ministry of Truth', short_name='m-truth',
        icon=icon)
    a.save()
    img = Image.open(TEST_IMG_PATH + 'ministry_of_peace.png')
    icon = models.Image.create_image(img, file_extension='png',
        access_control='UNCLASSIFIED', image_type='agency_icon')
    a = models.Agency(title='Ministry of Peace', short_name='m-peace',
        icon=icon)
    a.save()
    img = Image.open(TEST_IMG_PATH + 'ministry_of_love.jpeg')
    icon = models.Image.create_image(img, file_extension='jpeg',
        access_control='UNCLASSIFIED', image_type='agency_icon')
    a = models.Agency(title='Ministry of Love', short_name='m-love',
        icon=icon)
    a.save()

    ############################################################################
    #                               Tags
    ############################################################################
    t1 =  models.Tag(name='demo')
    t1.save()
    t2 = models.Tag(name='useless')
    t2.save()

    ############################################################################
    #                               Org Stewards
    ############################################################################
    models.Profile.create_user('wsmith',
        email='wsmith@nowhere.com',
        display_name='William Smith',
        bio='I work at the Ministry of Truth',
        access_control='UNCLASSIFIED',
        organizations=['Ministry of Truth'],
        stewarded_organizations=['Ministry of Truth'],
        groups=['ORG_STEWARD']
    )

    ############################################################################
    #                               Apps Mall Stewards
    ############################################################################
    models.Profile.create_user('pboss',
        email='pboss@nowhere.com',
        display_name='P Boss',
        bio='I am the boss',
        access_control='UNCLASSIFIED',
        organizations=['Ministry of Truth'],
        groups=['APPS_MALL_STEWARD']
    )

    ############################################################################
    #                               Regular user
    ############################################################################
    p = models.Profile.create_user('bjones',
        email='bjones@nowhere.com',
        display_name='Bob Jones',
        bio='Nothing special',
        access_control='UNCLASSIFIED',
        organizations=['Ministry of Love'],
        groups=['USER']
    )

    p = models.Profile.create_user('jdoe',
        email='jdoe@nowhere.com',
        display_name='John Doe',
        bio='I am a normal person',
        access_control='UNCLASSIFIED',
        organizations=['Ministry of Truth'],
        groups=['USER']
    )

    ############################################################################
    #                           System Notifications
    ############################################################################
    next_week = datetime.datetime.now() + datetime.timedelta(days=7)
    eastern = pytz.timezone('US/Eastern')
    next_week = eastern.localize(next_week)
    n1 = models.Notification(message='The quick brown fox',
        expires_date=next_week, author=p)
    n1.save()
    n2 = models.Notification(message='Jumps over the lazy dog',
        expires_date=next_week, author=p)
    n2.save()

    ############################################################################
    #                           Contacts
    ############################################################################
    c = models.Contact(name='Jimmy John', organization='Jimmy Johns',
        contact_type=models.ContactType.objects.get(name='Manager'),
        email='jimmyjohn@jimmyjohns.com', unsecure_phone='555-555-5555')
    c.save()

    ############################################################################
    ############################################################################
    #                           Listings
    ############################################################################
    ############################################################################

    ############################################################################
    #                           Air Mail
    ############################################################################
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Icons
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    img = Image.open(TEST_IMG_PATH + 'AirMail16.png')
    small_icon = models.Image.create_image(img, file_extension='png',
        access_control='UNCLASSIFIED', image_type='listing_small_icon')
    img = Image.open(TEST_IMG_PATH + 'AirMail32.png')
    large_icon = models.Image.create_image(img, file_extension='png',
        access_control='UNCLASSIFIED', image_type='listing_large_icon')
    img = Image.open(TEST_IMG_PATH + 'AirMail.png')
    banner_icon = models.Image.create_image(img, file_extension='png',
        access_control='UNCLASSIFIED', image_type='listing_banner_icon')
    img = Image.open(TEST_IMG_PATH + 'AirMailFeatured.png')
    large_banner_icon = models.Image.create_image(img, file_extension='png',
        access_control='UNCLASSIFIED', image_type='listing_large_banner_icon')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Listing
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    l = models.Listing(
        title='Air Mail',
        agency=models.Agency.objects.get(title='Ministry of Truth'),
        app_type=models.ListingType.objects.get(title='web application'),
        description='Sends mail via air',
        launch_url='https://www.google.com/airmail',
        version_name='1.0.0',
        unique_name='ozp.test.air_mail',
        small_icon=small_icon,
        large_icon=large_icon,
        banner_icon=banner_icon,
        large_banner_icon=large_banner_icon,
        what_is_new='Nothing really new here',
        description_short='Sends airmail',
        requirements='None',
        approval_status=models.ApprovalStatus.APPROVED,
        is_enabled=True,
        is_featured=True,
        singleton=False,
        access_control=unclass
    )
    l.save()
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Contacts
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    l.contacts.add(models.Contact.objects.get(name='Jimmy John'))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Owners
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    l.owners.add(p)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Categories
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    l.categories.add(cat1)
    l.categories.add(cat2)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Tags
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    l.tags.add(t1)
    l.tags.add(t2)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Screenshots
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    img = Image.open(TEST_IMG_PATH + 'screenshot_small.png')
    small_img = models.Image.create_image(img, file_extension='png',
        access_control='UNCLASSIFIED', image_type='listing_small_screenshot')
    img = Image.open(TEST_IMG_PATH + 'screenshot_large.png')
    large_img = models.Image.create_image(img, file_extension='png',
        access_control='UNCLASSIFIED', image_type='listing_large_screenshot')
    s = models.Screenshot(small_image=small_img,
        large_image=large_img,
        listing=models.Listing.objects.get(title='Air Mail'))
    s.save()
    l.screenshots.add(s)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Notifications
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    n3 = models.Notification(message='Air Mail update next week',
        expires_date=next_week, listing=l, author=p)
    n3.save()

    ############################################################################
    #                           Bread Basket
    ############################################################################
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Icons
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    img = Image.open(TEST_IMG_PATH + 'BreadBasket16.png')
    small_icon = models.Image.create_image(img, file_extension='png',
        access_control='UNCLASSIFIED', image_type='listing_small_icon')
    img = Image.open(TEST_IMG_PATH + 'BreadBasket32.png')
    large_icon = models.Image.create_image(img, file_extension='png',
        access_control='UNCLASSIFIED', image_type='listing_large_icon')
    img = Image.open(TEST_IMG_PATH + 'BreadBasket.png')
    banner_icon = models.Image.create_image(img, file_extension='png',
        access_control='UNCLASSIFIED', image_type='listing_banner_icon')
    img = Image.open(TEST_IMG_PATH + 'BreadBasketFeatured.png')
    large_banner_icon = models.Image.create_image(img, file_extension='png',
        access_control='UNCLASSIFIED', image_type='listing_large_screenshot')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Listing
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    l = models.Listing(
        title='Bread Basket',
        agency=models.Agency.objects.get(title='Ministry of Truth'),
        app_type=models.ListingType.objects.get(title='web application'),
        description='Carries delicious bread',
        launch_url='https://www.google.com/breadbasket',
        version_name='1.0.0',
        unique_name='ozp.test.bread_basket',
        small_icon=small_icon,
        large_icon=large_icon,
        banner_icon=banner_icon,
        large_banner_icon=large_banner_icon,
        what_is_new='Nothing really new here',
        description_short='Carries bread',
        requirements='None',
        approval_status=models.ApprovalStatus.APPROVED,
        is_enabled=True,
        is_featured=True,
        singleton=False,
        is_private=True,
        access_control=unclass
    )
    l.save()
    l.contacts.add(models.Contact.objects.get(name='Jimmy John'))
    l.owners.add(p)
    l.categories.add(cat1)
    l.categories.add(cat2)
    l.tags.add(t1)

    ############################################################################
    #                           Chart Course
    ############################################################################
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Icons
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    img = Image.open(TEST_IMG_PATH + 'ChartCourse16.png')
    small_icon = models.Image.create_image(img, file_extension='png',
        access_control='UNCLASSIFIED', image_type='listing_small_icon')
    img = Image.open(TEST_IMG_PATH + 'BreadBasket32.png')
    large_icon = models.Image.create_image(img, file_extension='png',
        access_control='UNCLASSIFIED', image_type='listing_large_icon')
    img = Image.open(TEST_IMG_PATH + 'BreadBasket.png')
    banner_icon = models.Image.create_image(img, file_extension='png',
        access_control='UNCLASSIFIED', image_type='listing_banner_icon')
    img = Image.open(TEST_IMG_PATH + 'BreadBasketFeatured.png')
    large_banner_icon = models.Image.create_image(img, file_extension='png',
        access_control='UNCLASSIFIED', image_type='listing_large_banner_icon')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Listing
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    l = models.Listing(
        title='Cupid',
        agency=models.Agency.objects.get(title='Ministry of Love'),
        app_type=models.ListingType.objects.get(title='web application'),
        description='Find your match',
        launch_url='https://www.google.com/cupid',
        version_name='1.0.0',
        unique_name='ozp.test.cupid',
        small_icon=small_icon,
        large_icon=large_icon,
        banner_icon=banner_icon,
        large_banner_icon=large_banner_icon,
        what_is_new='Nothing really new here',
        description_short='Cupid stuff',
        requirements='None',
        approval_status=models.ApprovalStatus.APPROVED,
        is_enabled=True,
        is_featured=True,
        singleton=False,
        is_private=True,
        access_control=unclass
    )
    l.save()
    l.contacts.add(models.Contact.objects.get(name='Jimmy John'))
    l.owners.add(p)
    l.categories.add(cat1)
    l.tags.add(t2)

    l = models.Listing(
        title='ChartCourse',
        agency=models.Agency.objects.get(title='Ministry of Truth'),
        app_type=models.ListingType.objects.get(title='web application'),
        description='Find your match',
        launch_url='https://www.google.com/chartcourse',
        version_name='1.0.0',
        unique_name='ozp.test.chartcourse',
        small_icon=small_icon,
        large_icon=large_icon,
        banner_icon=banner_icon,
        large_banner_icon=large_banner_icon,
        what_is_new='Nothing really new here',
        description_short='chart course stuff',
        requirements='None',
        approval_status=models.ApprovalStatus.APPROVED,
        is_enabled=True,
        is_featured=True,
        singleton=False,
        is_private=True,
        access_control=models.AccessControl.objects.get(title='UNCLASSIFIED//ABC')
    )
    l.save()
    l.contacts.add(models.Contact.objects.get(name='Jimmy John'))
    # add intents
    l.intents.add(models.Intent.objects.get(action='/application/json/view'))
    l.categories.add(cat2)

    # bookmark listings
    a = models.ApplicationLibraryEntry(
        owner=model_access.get_profile('wsmith'),
        listing=models.Listing.objects.get(unique_name='ozp.test.bread_basket'))
    a.save()

    a = models.ApplicationLibraryEntry(
        owner=model_access.get_profile('wsmith'),
        listing=models.Listing.objects.get(unique_name='ozp.test.air_mail'))
    a.save()


if __name__ == "__main__":
    run()