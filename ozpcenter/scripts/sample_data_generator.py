"""
Creates test data

************************************WARNING************************************
Many of the unit tests depend on data set in this script. Always
run the unit tests (python manage.py test) after making any changes to this
data!!
************************************WARNING************************************
"""
from PIL import Image
import datetime
import json
import os
import time
import pytz
import sys

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../../')))
from django.conf import settings
from django.db import transaction
import yaml

from ozpcenter import models
from ozpcenter.api.notification import model_access as notification_model_access
from ozpcenter.recommend.recommend import RecommenderDirectory
import ozpcenter.api.listing.model_access as listing_model_access


TEST_IMG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_images') + '/'
TEST_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data')

DEMO_APP_ROOT = settings.OZP['DEMO_APP_ROOT']


def time_ms():
    return time.time() * 1000.0


def create_listing_review_batch(*input_list):
    """
    Create Listing

    example:
        [
            listing,
            [profile_ref['charrington'], 5, "This app is great - well designed and easy to use"],
            [profile_ref['tparsons'], 3, "This app is great - well designed and easy to use"],
            [profile_ref['syme'], 1, "This app is great - well designed and easy to use"]
        ]
    """
    current_listing = input_list[0]

    for input_set in input_list[1:]:
        profile_obj = input_set[0]
        current_rating = input_set[1]
        current_text = input_set[2]
        listing_model_access.create_listing_review(profile_obj.user.username, current_listing, current_rating, text=current_text)


def create_library_entries(entries):
    """
    Create Bookmarks for users
    """
    for current_entry in entries:
        current_profile_string = current_entry[0]
        current_profile = models.Profile.objects.filter(user__username=current_profile_string).first()
        current_unique_name = current_entry[1]
        current_folder_name = current_entry[2]

        library_entry = models.ApplicationLibraryEntry(
            owner=current_profile,
            listing=models.Listing.objects.get(unique_name=current_unique_name),
            folder=current_folder_name)
        library_entry.save()


def run():
    """
    Creates basic sample data
    """
    total_start_time = time_ms()
    # Create Groups
    models.Profile.create_groups()

    ############################################################################
    #                           Security Markings
    ############################################################################
    unclass = 'UNCLASSIFIED'  # noqa: F841
    secret = 'SECRET'    # noqa: F841
    secret_n = 'SECRET//NOVEMBER'    # noqa: F841
    ts = 'TOP SECRET'    # noqa: F841
    ts_s = 'TOP SECRET//SIERRA'    # noqa: F841
    ts_st = 'TOP SECRET//SIERRA//TANGO'    # noqa: F841
    ts_stgh = 'TOP SECRET//SIERRA//TANGO//GOLF//HOTEL'    # noqa: F841

    ts_n = 'TOP SECRET//NOVEMBER'    # noqa: F841
    ts_sn = 'TOP SECRET//SIERRA//NOVEMBER'    # noqa: F841
    ts_stn = 'TOP SECRET//SIERRA//TANGO//NOVEMBER'    # noqa: F841
    ts_stghn = 'TOP SECRET//SIERRA//TANGO//GOLF//HOTEL//NOVEMBER'    # noqa: F841

    ############################################################################
    #                           Categories
    ############################################################################
    category_start_time = time_ms()

    categories_bulk = models.Category.objects.bulk_create([
        models.Category(title="Books and Reference", description="Things made of paper"),
        models.Category(title="Business", description="For making money"),
        models.Category(title="Communication", description="Moving info between people and things"),
        models.Category(title="Education", description="Educational in nature"),
        models.Category(title="Entertainment", description="For fun"),
        models.Category(title="Finance", description="For managing money"),
        models.Category(title="Health and Fitness", description="Be healthy, be fit"),
        models.Category(title="Media and Video", description="Videos and media stuff"),
        models.Category(title="Music and Audio", description="Using your ears"),
        models.Category(title="News", description="What's happening where"),
        models.Category(title="Productivity", description="Do more in less time"),
        models.Category(title="Shopping", description="For spending your money"),
        models.Category(title="Sports", description="Score more points than your opponent"),
        models.Category(title="Tools", description="Tools and Utilities"),
        models.Category(title="Weather", description="Get the temperature")
        ])

    categories_ref = {}

    for category in categories_bulk:
        categories_ref[category.title.lower().replace(' and ', ' ').replace(' ', '_')] = models.Category.objects.get(title=category.title)

    category_end_time = time_ms()

    ############################################################################
    #                           Contact Types
    ############################################################################
    with transaction.atomic():
        civillian = models.ContactType(name='Civillian')
        civillian.save()

        government = models.ContactType(name='Government')
        government.save()

        military = models.ContactType(name='Military')
        military.save()

    ############################################################################
    #                           Listing Types
    ############################################################################
    with transaction.atomic():
        web_app = models.ListingType(title='Web Application', description='web applications')
        web_app.save()

        widget = models.ListingType(title='Widget', description='widget things')
        widget.save()

        desktop_app = models.ListingType(title='Desktop App', description='desktop app')
        desktop_app.save()

        web_services = models.ListingType(title='Web Services', description='web services')
        web_services.save()

        code_library = models.ListingType(title='Code Library', description='code library')
        code_library.save()

    ############################################################################
    #                           Image Types
    ############################################################################
    # Note: these image sizes do not represent those that should be used in
    # production
    with transaction.atomic():
        small_icon_type = models.ImageType(name='small_icon', max_size_bytes='4096')
        small_icon_type.save()

        large_icon_type = models.ImageType(name='large_icon', max_size_bytes='8192')
        large_icon_type.save()

        banner_icon_type = models.ImageType(name='banner_icon', max_size_bytes='2097152')
        banner_icon_type.save()

        large_banner_icon_type = models.ImageType(name='large_banner_icon', max_size_bytes='2097152')
        large_banner_icon_type.save()

        small_screenshot_type = models.ImageType(name='small_screenshot', max_size_bytes='1048576')
        small_screenshot_type.save()

        large_screenshot_type = models.ImageType(name='large_screenshot', max_size_bytes='1048576')
        large_screenshot_type.save()

        intent_icon_type = models.ImageType(name='intent_icon', max_size_bytes='2097152')
        intent_icon_type.save()

        agency_icon_type = models.ImageType(name='agency_icon', max_size_bytes='2097152')
        agency_icon_type.save()

    ############################################################################
    #                           Intents
    ############################################################################
    # TODO: more realistic data
    with transaction.atomic():
        img = Image.open(TEST_IMG_PATH + 'android.png')
        icon = models.Image.create_image(img, file_extension='png',
            security_marking='UNCLASSIFIED', image_type=intent_icon_type.name)
        i = models.Intent(action='/application/json/view',
            media_type='vnd.ozp-intent-v1+json.json',
            label='view',
            icon=icon)
        i.save()

        i = models.Intent(action='/application/json/edit',
            media_type='vnd.ozp-intent-v1+json.json',
            label='edit',
            icon=icon)
        i.save()

    ############################################################################
    #                           Organizations
    ############################################################################
    with transaction.atomic():
        # Minitrue - Ministry of Truth
        img = Image.open(TEST_IMG_PATH + 'ministry_of_truth.jpg')
        icon = models.Image.create_image(img, file_extension='jpg',
            security_marking='UNCLASSIFIED', image_type='agency_icon')
        minitrue = models.Agency(title='Ministry of Truth', short_name='Minitrue', icon=icon)
        minitrue.save()

        # Minipax - Ministry of Peace
        img = Image.open(TEST_IMG_PATH + 'ministry_of_peace.png')
        icon = models.Image.create_image(img, file_extension='png',
            security_marking='UNCLASSIFIED', image_type='agency_icon')
        minipax = models.Agency(title='Ministry of Peace', short_name='Minipax',
            icon=icon)
        minipax.save()

        # Miniluv - Ministry of Love
        img = Image.open(TEST_IMG_PATH + 'ministry_of_love.jpeg')
        icon = models.Image.create_image(img, file_extension='jpeg',
            security_marking='UNCLASSIFIED', image_type='agency_icon')
        miniluv = models.Agency(title='Ministry of Love', short_name='Miniluv', icon=icon)
        miniluv.save()

        # Miniplen - Ministry of Plenty
        img = Image.open(TEST_IMG_PATH + 'ministry_of_plenty.png')
        icon = models.Image.create_image(img, file_extension='png',
            security_marking='UNCLASSIFIED', image_type='agency_icon')
        miniplenty = models.Agency(title='Ministry of Plenty', short_name='Miniplen', icon=icon)
        miniplenty.save()

    ############################################################################
    #                               Tags
    ############################################################################
    with transaction.atomic():
        demo = models.Tag(name='demo')
        demo.save()

        example = models.Tag(name='example')
        example.save()

    ############################################################################
    #                               Profiles
    ############################################################################
    with transaction.atomic():
        profile_ref = {}
        profile_data = None
        with open(os.path.join(TEST_DATA_PATH, 'profile.yaml'), 'r') as stream:
            try:
                profile_data= yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        for current_profile_data in profile_data:
            access_control = json.dumps(current_profile_data['access_control'])
            profile_ref[current_profile_data['username']] = models.Profile.create_user(current_profile_data['username'],  # noqa: F841
                email=current_profile_data['email'],
                display_name=current_profile_data['display_name'],
                bio=current_profile_data['bio'],
                access_control=access_control,
                organizations=current_profile_data['organizations'],
                stewarded_organizations=current_profile_data['stewarded_organizations'],
                groups=current_profile_data['groups'],
                dn=current_profile_data['dn']
            )

    # -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
    ############################################################################
    #                           System Notifications
    ############################################################################
    with transaction.atomic():
        # create some notifications that expire next week
        next_week = datetime.datetime.now() + datetime.timedelta(days=7)
        eastern = pytz.timezone('US/Eastern')
        next_week = eastern.localize(next_week)
        n1 = notification_model_access.create_notification(profile_ref['wsmith'],  # noqa: F841
                                                           next_week,
                                                           'System will be going down for approximately 30 minutes on X/Y at 1100Z')

        n2 = notification_model_access.create_notification(profile_ref['julia'],  # noqa: F841
                                                           next_week,
                                                           'System will be functioning in a degredaded state between 1800Z-0400Z on A/B')

        # create some expired notifications
        last_week = datetime.datetime.now() - datetime.timedelta(days=7)
        last_week = eastern.localize(last_week)

        n1 = notification_model_access.create_notification(profile_ref['wsmith'],  # noqa: F841
                                                           last_week,
                                                           'System will be going down for approximately 30 minutes on C/D at 1700Z')

        n2 = notification_model_access.create_notification(profile_ref['julia'],  # noqa: F841
                                                           last_week,
                                                           'System will be functioning in a degredaded state between 2100Z-0430Z on F/G')

    # -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
    ############################################################################
    #                           Contacts
    ############################################################################
    with transaction.atomic():
        osha = models.Contact(name='Osha', organization='House Stark',
            contact_type=models.ContactType.objects.get(name='Civillian'),
            email='osha@stark.com', unsecure_phone='321-123-7894')
        osha.save()

        rob_baratheon = models.Contact(name='Robert Baratheon',
            organization='House Baratheon',
            contact_type=models.ContactType.objects.get(name='Government'),
            email='rbaratheon@baratheon.com', unsecure_phone='123-456-7890')
        rob_baratheon.save()

        brienne = models.Contact(name='Brienne Tarth', organization='House Stark',
            contact_type=models.ContactType.objects.get(name='Military'),
            email='brienne@stark.com', unsecure_phone='222-324-3846')
        brienne.save()

    # -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
    # ===========================================================================
    #                           Listings
    # ===========================================================================

    ############################################################################
    #                           Air Mail
    ############################################################################
    # Looping for more sample results
    print('== Creating Air Mail Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Icons
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            img = Image.open(TEST_IMG_PATH + 'AirMail16.png')
            small_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=small_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'AirMail32.png')
            large_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'AirMail.png')
            banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=banner_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'AirMailFeatured.png')
            large_banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_banner_icon_type.name)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Listing
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            listing = models.Listing(
                title='Air Mail{0!s}'.format(postfix_space),
                agency=minitrue,
                listing_type=web_app,
                description='Sends mail via air',
                launch_url='{0!s}/demo_apps/centerSampleListings/airMail/index.html'.format(DEMO_APP_ROOT),
                version_name='1.0.0',
                unique_name='ozp.test.air_mail{0!s}'.format(postfix_dot),
                small_icon=small_icon,
                large_icon=large_icon,
                banner_icon=banner_icon,
                large_banner_icon=large_banner_icon,
                what_is_new='Nothing really new here',
                description_short='Sends airmail',
                requirements='None',
                is_enabled=True,
                is_featured=True,
                iframe_compatible=False,
                security_marking=unclass
            )
            listing.save()
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Contacts
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            listing.contacts.add(osha)
            listing.contacts.add(brienne)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Owners
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            listing.owners.add(profile_ref['wsmith'])

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Categories
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            listing.categories.add(categories_ref['communication'])
            listing.categories.add(categories_ref['productivity'])
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Tags
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

            current_tag = models.Tag(name='tag_{0}'.format(i))
            current_tag.save()

            listing.tags.add(demo)
            listing.tags.add(example)
            listing.tags.add(current_tag)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Screenshots
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            img = Image.open(TEST_IMG_PATH + 'screenshot_small.png')
            small_img = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=small_screenshot_type.name)
            img = Image.open(TEST_IMG_PATH + 'screenshot_large.png')
            large_img = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_screenshot_type.name)
            screenshot = models.Screenshot(small_image=small_img,
                large_image=large_img,
                listing=listing)
            screenshot.save()

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Document URLs
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            wiki = models.DocUrl(name='wiki', url='http://www.google.com/wiki',
                listing=listing)
            wiki.save()
            guide = models.DocUrl(name='guide', url='http://www.google.com/guide',
                listing=listing)
            guide.save()

            listing_model_access.create_listing(profile_ref['wsmith'], listing)
            listing_model_access.submit_listing(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing_by_org_steward(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing(profile_ref['wsmith'], listing)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Reviews
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            create_listing_review_batch(listing,
                [profile_ref['charrington'], 5, "This app is great - well designed and easy to use"],
                [profile_ref['tparsons'], 3, "Air mail is ok - does what it says and no more"],
                [profile_ref['syme'], 1, "Air mail crashes all the time - it doesn't even support IE 6!"]
            )

    ############################################################################
    #                           Bread Basket
    ############################################################################
    print('== Creating Bread Basket Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Icons
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            img = Image.open(TEST_IMG_PATH + 'BreadBasket16.png')
            small_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=small_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'BreadBasket32.png')
            large_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'BreadBasket.png')
            banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=banner_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'BreadBasketFeatured.png')
            large_banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_banner_icon_type.name)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Listing
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            listing = models.Listing(
                title='Bread Basket{0!s}'.format(postfix_space),
                agency=minitrue,
                listing_type=web_app,
                description='Carries delicious bread',
                launch_url='{0!s}/demo_apps/centerSampleListings/breadBasket/index.html'.format(DEMO_APP_ROOT),
                version_name='1.0.0',
                unique_name='ozp.test.bread_basket{0!s}'.format(postfix_dot),
                small_icon=small_icon,
                large_icon=large_icon,
                banner_icon=banner_icon,
                large_banner_icon=large_banner_icon,
                what_is_new='Nothing really new here',
                description_short='Carries bread',
                requirements='None',
                is_enabled=True,
                is_featured=True,
                iframe_compatible=False,
                is_private=True,
                security_marking=unclass
            )
            listing.save()

            listing.contacts.add(osha)
            listing.owners.add(profile_ref['julia'])
            listing.categories.add(categories_ref['health_fitness'])
            listing.categories.add(categories_ref['shopping'])

            listing.tags.add(demo)
            listing.tags.add(example)

            listing_model_access.create_listing(profile_ref['julia'], listing)
            listing_model_access.submit_listing(profile_ref['julia'], listing)
            listing_model_access.approve_listing_by_org_steward(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing(profile_ref['wsmith'], listing)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Reviews
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            create_listing_review_batch(listing,
                [profile_ref['jones'], 2, "This bread is stale!"],
                [profile_ref['julia'], 5, "Yum!"]
            )

    ############################################################################
    #                           Chart Course
    ############################################################################
    print('== Creating Chart Course Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Icons
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # ChartCourse16
            img = Image.open(TEST_IMG_PATH + 'ChartCourse16.png')
            small_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=small_icon_type.name)

            # ChartCourse32
            img = Image.open(TEST_IMG_PATH + 'ChartCourse32.png')
            large_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_icon_type.name)

            # ChartCourse
            img = Image.open(TEST_IMG_PATH + 'ChartCourse.png')
            banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=banner_icon_type.name)

            # ChartCourseFeatured
            img = Image.open(TEST_IMG_PATH + 'ChartCourseFeatured.png')
            large_banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_banner_icon_type.name)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Listing
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            listing = models.Listing(
                title='Chart Course{0!s}'.format(postfix_space),
                agency=minitrue,
                listing_type=web_app,
                description='Chart your course',
                launch_url='{0!s}/demo_apps/centerSampleListings/chartCourse/index.html'.format(DEMO_APP_ROOT),
                version_name='1.0.0',
                unique_name='ozp.test.chartcourse{0!s}'.format(postfix_dot),
                small_icon=small_icon,
                large_icon=large_icon,
                banner_icon=banner_icon,
                large_banner_icon=large_banner_icon,
                what_is_new='Nothing really new here',
                description_short='Chart your course',
                requirements='None',
                is_enabled=True,
                is_featured=True,
                iframe_compatible=False,
                is_private=False,
                security_marking=unclass
            )
            listing.save()
            listing.contacts.add(rob_baratheon)
            listing.owners.add(profile_ref['wsmith'])
            listing.categories.add(categories_ref['tools'])
            listing.categories.add(categories_ref['education'])
            listing.tags.add(demo)

            listing_model_access.create_listing(profile_ref['wsmith'], listing)
            listing_model_access.submit_listing(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing_by_org_steward(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing(profile_ref['wsmith'], listing)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Reviews
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            create_listing_review_batch(listing,
                [profile_ref['wsmith'], 2, "This Chart is bad"],
                [profile_ref['bigbrother'], 5, "Good Chart!"]
            )

    ############################################################################
    #                           Chatter Box
    ############################################################################
    print('== Creating Chatter Box Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Icons
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            img = Image.open(TEST_IMG_PATH + 'ChatterBox16.png')
            small_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=small_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'ChatterBox32.png')
            large_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'ChatterBox.png')
            banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=banner_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'ChatterBoxFeatured.png')
            large_banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_banner_icon_type.name)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Listing
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            listing = models.Listing(
                title='Chatter Box{0!s}'.format(postfix_space),
                agency=miniluv,
                listing_type=web_app,
                description='Chat with people',
                launch_url='{0!s}/demo_apps/centerSampleListings/chatterBox/index.html'.format(DEMO_APP_ROOT),
                version_name='1.0.0',
                unique_name='ozp.test.chatterbox{0!s}'.format(postfix_dot),
                small_icon=small_icon,
                large_icon=large_icon,
                banner_icon=banner_icon,
                large_banner_icon=large_banner_icon,
                what_is_new='Nothing really new here',
                description_short='Chat in a box',
                requirements='None',
                is_enabled=True,
                is_featured=True,
                iframe_compatible=False,
                is_private=False,
                security_marking=unclass
            )
            listing.save()
            listing.contacts.add(rob_baratheon)
            listing.owners.add(profile_ref['julia'])
            listing.categories.add(categories_ref['communication'])
            listing.tags.add(demo)

            listing_model_access.create_listing(profile_ref['julia'], listing)
            listing_model_access.submit_listing(profile_ref['julia'], listing)
            listing_model_access.approve_listing_by_org_steward(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing(profile_ref['wsmith'], listing)

    ############################################################################
    #                           Clipboard
    ############################################################################
    print('== Creating Clipboard Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Icons
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            img = Image.open(TEST_IMG_PATH + 'Clipboard16.png')
            small_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=small_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'Clipboard32.png')
            large_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'Clipboard.png')
            banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=banner_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'ClipboardFeatured.png')
            large_banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_banner_icon_type.name)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Listing
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            listing = models.Listing(
                title='Clipboard{0!s}'.format(postfix_space),
                agency=minitrue,
                listing_type=web_app,
                description='Clip stuff on a board',
                launch_url='{0!s}/demo_apps/centerSampleListings/clipboard/index.html'.format(DEMO_APP_ROOT),
                version_name='1.0.0',
                unique_name='ozp.test.clipboard{0!s}'.format(postfix_dot),
                small_icon=small_icon,
                large_icon=large_icon,
                banner_icon=banner_icon,
                large_banner_icon=large_banner_icon,
                what_is_new='Nothing really new here',
                description_short='Its a clipboard',
                requirements='None',
                is_enabled=True,
                is_featured=True,
                iframe_compatible=False,
                is_private=False,
                security_marking=unclass
            )
            listing.save()
            listing.contacts.add(rob_baratheon)
            listing.owners.add(profile_ref['wsmith'])
            listing.categories.add(categories_ref['tools'])
            listing.categories.add(categories_ref['education'])
            listing.tags.add(demo)

            listing_model_access.create_listing(profile_ref['wsmith'], listing)
            listing_model_access.submit_listing(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing_by_org_steward(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing(profile_ref['wsmith'], listing)

    ############################################################################
    #                           FrameIt
    ############################################################################
    print('== Creating FrameIt Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Icons
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            img = Image.open(TEST_IMG_PATH + 'FrameIt16.png')
            small_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=small_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'FrameIt32.png')
            large_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'FrameIt.png')
            banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=banner_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'FrameItFeatured.png')
            large_banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_banner_icon_type.name)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Listing
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            listing = models.Listing(
                title='FrameIt{0!s}'.format(postfix_space),
                agency=minitrue,
                listing_type=web_app,
                description='Show things in an iframe',
                launch_url='{0!s}/demo_apps/frameit/index.html'.format(DEMO_APP_ROOT),
                version_name='1.0.0',
                unique_name='ozp.test.frameit{0!s}'.format(postfix_dot),
                small_icon=small_icon,
                large_icon=large_icon,
                banner_icon=banner_icon,
                large_banner_icon=large_banner_icon,
                what_is_new='Nothing really new here',
                description_short='Its an iframe',
                requirements='None',
                is_enabled=True,
                is_featured=True,
                iframe_compatible=False,
                is_private=False,
                security_marking=unclass
            )
            listing.save()
            listing.contacts.add(rob_baratheon)
            listing.owners.add(profile_ref['wsmith'])
            listing.categories.add(categories_ref['tools'])
            listing.categories.add(categories_ref['education'])
            listing.tags.add(demo)

            listing_model_access.create_listing(profile_ref['wsmith'], listing)
            listing_model_access.submit_listing(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing_by_org_steward(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing(profile_ref['wsmith'], listing)

    ############################################################################
    #                           Hatch Latch
    ############################################################################
    print('== Creating Hatch Latch Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Icons
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            img = Image.open(TEST_IMG_PATH + 'HatchLatch16.png')
            small_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=small_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'HatchLatch32.png')
            large_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'HatchLatch.png')
            banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=banner_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'HatchLatchFeatured.png')
            large_banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_banner_icon_type.name)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Listing
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            listing = models.Listing(
                title='Hatch Latch{0!s}'.format(postfix_space),
                agency=minitrue,
                listing_type=web_app,
                description='Hatch latches',
                launch_url='{0!s}/demo_apps/centerSampleListings/hatchLatch/index.html'.format(DEMO_APP_ROOT),
                version_name='1.0.0',
                unique_name='ozp.test.hatchlatch{0!s}'.format(postfix_dot),
                small_icon=small_icon,
                large_icon=large_icon,
                banner_icon=banner_icon,
                large_banner_icon=large_banner_icon,
                what_is_new='Nothing really new here',
                description_short='Its a hatch latch',
                requirements='None',
                is_enabled=True,
                is_featured=True,
                iframe_compatible=False,
                is_private=False,
                security_marking=unclass
            )
            listing.save()
            listing.contacts.add(rob_baratheon)
            listing.owners.add(profile_ref['wsmith'])
            listing.categories.add(categories_ref['tools'])
            listing.categories.add(categories_ref['education'])
            listing.categories.add(categories_ref['health_fitness'])
            listing.tags.add(demo)

            listing_model_access.create_listing(profile_ref['wsmith'], listing)
            listing_model_access.submit_listing(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing_by_org_steward(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing(profile_ref['wsmith'], listing)

            ############################################################################
            #                           Jot Spot
            ############################################################################
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Icons
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            img = Image.open(TEST_IMG_PATH + 'JotSpot16.png')
            small_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=small_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'JotSpot32.png')
            large_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'JotSpot.png')
            banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=banner_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'JotSpotFeatured.png')
            large_banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_banner_icon_type.name)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Listing
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

            listing = models.Listing(
                title='JotSpot{0!s}'.format(postfix_space),
                agency=minitrue,
                listing_type=web_app,
                description='Jot things down',
                launch_url='{0!s}/demo_apps/centerSampleListings/jotSpot/index.html'.format(DEMO_APP_ROOT),
                version_name='1.0.0',
                unique_name='ozp.test.jotspot{0!s}'.format(postfix_dot),
                small_icon=small_icon,
                large_icon=large_icon,
                banner_icon=banner_icon,
                large_banner_icon=large_banner_icon,
                what_is_new='Nothing really new here',
                description_short='Jot stuff down',
                requirements='None',
                is_enabled=True,
                is_featured=True,
                iframe_compatible=False,
                is_private=False,
                security_marking=unclass
            )
            listing.save()
            listing.contacts.add(rob_baratheon)
            listing.owners.add(profile_ref['wsmith'])
            listing.categories.add(categories_ref['tools'])
            listing.categories.add(categories_ref['education'])
            listing.tags.add(demo)

            listing_model_access.create_listing(profile_ref['wsmith'], listing)
            listing_model_access.submit_listing(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing_by_org_steward(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing(profile_ref['wsmith'], listing)

            listing_model_access.create_listing_review(profile_ref['charrington'].user.username, listing, 4, text="I really like it")

    ############################################################################
    #                           Location Lister
    ############################################################################
    print('== Creating Location Lister Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Icons
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            img = Image.open(TEST_IMG_PATH + 'LocationLister16.png')
            small_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=small_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'LocationLister32.png')
            large_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'LocationLister.png')
            banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=banner_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'LocationListerFeatured.png')
            large_banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_banner_icon_type.name)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Listing
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

            listing = models.Listing(
                title='LocationLister{0!s}'.format(postfix_space),
                agency=minitrue,
                listing_type=web_app,
                description='List locations',
                launch_url='{0!s}/demo_apps/locationLister/index.html'.format(DEMO_APP_ROOT),
                version_name='1.0.0',
                unique_name='ozp.test.locationlister{0!s}'.format(postfix_dot),
                small_icon=small_icon,
                large_icon=large_icon,
                banner_icon=banner_icon,
                large_banner_icon=large_banner_icon,
                what_is_new='Nothing really new here',
                description_short='List locations',
                requirements='None',
                is_enabled=True,
                is_featured=True,
                iframe_compatible=False,
                is_private=False,
                security_marking=unclass
            )
            listing.save()
            listing.contacts.add(rob_baratheon)
            listing.owners.add(profile_ref['wsmith'])
            listing.categories.add(categories_ref['tools'])
            listing.categories.add(categories_ref['education'])
            listing.tags.add(demo)

            listing_model_access.create_listing(profile_ref['wsmith'], listing)
            listing_model_access.submit_listing(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing_by_org_steward(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing(profile_ref['wsmith'], listing)

            listing_model_access.create_listing_review(profile_ref['charrington'].user.username, listing, 4, text="I really like it")

    ############################################################################
    #                           Location Viewer
    ############################################################################
    print('== Creating Location Viewer Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Icons
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            img = Image.open(TEST_IMG_PATH + 'LocationViewer16.png')
            small_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=small_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'LocationViewer32.png')
            large_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'LocationViewer.png')
            banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=banner_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'LocationViewerFeatured.png')
            large_banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_banner_icon_type.name)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Listing
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            listing = models.Listing(
                title='LocationViewer{0!s}'.format(postfix_space),
                agency=minitrue,
                listing_type=web_app,
                description='View locations',
                launch_url='{0!s}/demo_apps/locationViewer/index.html'.format(DEMO_APP_ROOT),
                version_name='1.0.0',
                unique_name='ozp.test.locationviewer{0!s}'.format(postfix_dot),
                small_icon=small_icon,
                large_icon=large_icon,
                banner_icon=banner_icon,
                large_banner_icon=large_banner_icon,
                what_is_new='Nothing really new here',
                description_short='View locations',
                requirements='None',
                is_enabled=True,
                is_featured=True,
                iframe_compatible=False,
                is_private=False,
                security_marking=unclass
            )
            listing.save()
            listing.contacts.add(rob_baratheon)
            listing.owners.add(profile_ref['wsmith'])
            listing.categories.add(categories_ref['tools'])
            listing.categories.add(categories_ref['education'])
            listing.tags.add(demo)

            listing_model_access.create_listing(profile_ref['wsmith'], listing)
            listing_model_access.submit_listing(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing_by_org_steward(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing(profile_ref['wsmith'], listing)

    ############################################################################
    #                           Location Analyzer
    ############################################################################
    print('== Creating Location Analyzer Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Icons
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            img = Image.open(TEST_IMG_PATH + 'LocationAnalyzer16.png')
            small_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=small_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'LocationAnalyzer32.png')
            large_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'LocationAnalyzer.png')
            banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=banner_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'LocationAnalyzerFeatured.png')
            large_banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_banner_icon_type.name)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Listing
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            listing = models.Listing(
                title='LocationAnalyzer{0!s}'.format(postfix_space),
                agency=minitrue,
                listing_type=web_app,
                description='Analyze locations',
                launch_url='{0!s}/demo_apps/locationAnalyzer/index.html'.format(DEMO_APP_ROOT),
                version_name='1.0.0',
                unique_name='ozp.test.locationanalyzer{0!s}'.format(postfix_dot),
                small_icon=small_icon,
                large_icon=large_icon,
                banner_icon=banner_icon,
                large_banner_icon=large_banner_icon,
                what_is_new='Nothing really new here',
                description_short='Analyze locations',
                requirements='None',
                is_enabled=True,
                is_featured=True,
                iframe_compatible=False,
                is_private=False,
                security_marking=unclass
            )
            listing.save()
            listing.contacts.add(rob_baratheon)
            listing.owners.add(profile_ref['wsmith'])
            listing.categories.add(categories_ref['tools'])
            listing.categories.add(categories_ref['education'])
            listing.tags.add(demo)

            listing_model_access.create_listing(profile_ref['wsmith'], listing)
            listing_model_access.submit_listing(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing_by_org_steward(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing(profile_ref['wsmith'], listing)

    ############################################################################
    #                           Skybox
    ############################################################################
    #   Looping for more sample listings
    print('== Creating Skybox Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Icons
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            img = Image.open(TEST_IMG_PATH + 'Skybox16.png')
            small_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=small_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'Skybox32.png')
            large_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'Skybox.png')
            banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=banner_icon_type.name)
            img = Image.open(TEST_IMG_PATH + 'SkyboxFeatured.png')
            large_banner_icon = models.Image.create_image(img, file_extension='png',
                security_marking=unclass, image_type=large_banner_icon_type.name)

            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            #                           Listing
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            listing = models.Listing(
                title='Skybox{0!s}'.format(postfix_space),
                agency=miniluv,
                listing_type=web_app,
                description='Sky Overlord',
                launch_url='{0!s}/demo_apps/Skybox/index.html'.format(DEMO_APP_ROOT),
                version_name='1.0.0',
                unique_name='ozp.test.skybox{0!s}'.format(postfix_dot),
                small_icon=small_icon,
                large_icon=large_icon,
                banner_icon=banner_icon,
                large_banner_icon=large_banner_icon,
                what_is_new="It's a box in the sky",
                description_short='Sky Overlord',
                requirements='None',
                is_enabled=True,
                is_featured=True,
                iframe_compatible=False,
                is_private=False,
                security_marking=unclass
            )
            listing.save()
            listing.contacts.add(rob_baratheon)

            listing.owners.add(profile_ref['pmurt'])
            listing.owners.add(profile_ref['david'])

            listing.categories.add(categories_ref['tools'])
            listing.categories.add(categories_ref['education'])

            listing.tags.add(demo)

            listing_model_access.create_listing(profile_ref['wsmith'], listing)
            listing_model_access.submit_listing(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing_by_org_steward(profile_ref['wsmith'], listing)
            listing_model_access.approve_listing(profile_ref['wsmith'], listing)

    ############################################################################
    #                           Library
    ############################################################################
    # bookmark listings
    # [[entry.owner.user.username , entry.listing.unique_name, entry.folder] for entry in ApplicationLibraryEntry.objects.all()]

    library_entries = [
        # wsmith
        ['wsmith', 'ozp.test.bread_basket', None],
        ['wsmith', 'ozp.test.air_mail', None],
        ['wsmith', 'ozp.test.skybox.1', None],
        ['wsmith', 'ozp.test.skybox.2', None],
        ['wsmith', 'ozp.test.skybox.3', None],

        # Hodor
        ['hodor', 'ozp.test.jotspot', None],
        ['hodor', 'ozp.test.locationlister', None],
        ['hodor', 'ozp.test.chartcourse', None],
        ['hodor', 'ozp.test.air_mail', None],
        ['hodor', 'ozp.test.skybox', None],
        ['hodor', 'ozp.test.skybox.1', None],

        ['bigbrother', 'ozp.test.bread_basket', None]
    ]

    create_library_entries(
        library_entries
    )

    for current_unique_name in [entry[1] for entry in library_entries]:
        print('======={}======'.format(current_unique_name))
        current_listing = models.Listing.objects.get(unique_name=current_unique_name)
        current_listing_owner = current_listing.owners.first()
        listing_notification = notification_model_access.create_notification(current_listing_owner,  # noqa: F841
                                                                      next_week,
                                                                      '{} update next week'.format(current_listing.title),
                                                                      listing=current_listing)

    ############################################################################
    #                           Subscription
    ############################################################################
    # Categories
    # ['Books and Reference', 'Business', 'Communication', 'Education', 'Entertainment', 'Finance',
    #  'Health and Fitness', 'Media and Video', 'Music and Audio', 'News',
    #  'Productivity', 'Shopping', 'Sports', 'Tools', 'Weather']
    # Tags
    # ['demo', 'example', 'tag_0', 'tag_1', 'tag_2', 'tag_3',
    #  'tag_4', 'tag_5', 'tag_6', 'tag_7', 'tag_8', 'tag_9']
    # Usernames
    # ['bigbrother', 'bigbrother2', 'khaleesi', 'wsmith', 'julia', 'obrien', 'aaronson',
    #  'pmurt', 'hodor', 'jones', 'tammy', 'rutherford', 'noah', 'syme', 'abe',
    #  'tparsons', 'jsnow', 'charrington', 'johnson']

    subscriptions = [  # flake8: noqa
        ['bigbrother', 'category', 'Books and Reference'],
        ['bigbrother', 'category', 'Business']
    ]
    ############################################################################
    #                           Recommendations
    ############################################################################
    sample_data_recommender = RecommenderDirectory()
    sample_data_recommender.recommend('baseline,graph_cf')

    total_end_time = time_ms()

    print('Sample Data Generator took: {} ms'.format(total_end_time - total_start_time))

if __name__ == "__main__":
    run()
