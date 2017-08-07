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
import ozpcenter.api.listing.model_access_es as model_access_es


TEST_IMG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_images') + '/'
TEST_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data')

DEMO_APP_ROOT = settings.OZP['DEMO_APP_ROOT']


def time_ms():
    return time.time() * 1000.0


def create_listing_review_batch(listing, review_list):
    """
    Create Listing

    Args:
        listing
        review_list
            [{
              "text": "This app is great - well designed and easy to use",
              "author": "charrington",
              "rate": 5
            },..
            ]

    """
    current_listing = listing

    for review_entry in review_list:
        profile_obj = models.Profile.objects.get(user__username=review_entry['author'])
        current_rating = review_entry['rate']
        current_text = review_entry['text']
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


def create_listing(listing_builder_dict):
    listing_data = listing_builder_dict['listing']
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Icons
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    small_icon = models.Image.create_image(
        Image.open(TEST_IMG_PATH + listing_data['small_icon']['filename']),
        file_extension=listing_data['small_icon']['filename'].split('.')[-1],
        security_marking=listing_data['small_icon']['security_marking'],
        image_type=models.ImageType.objects.get(name='small_icon').name)

    large_icon = models.Image.create_image(
        Image.open(TEST_IMG_PATH + listing_data['large_icon']['filename']),
        file_extension=listing_data['large_icon']['filename'].split('.')[-1],
        security_marking=listing_data['large_icon']['security_marking'],
        image_type=models.ImageType.objects.get(name='large_icon').name)

    banner_icon = models.Image.create_image(
        Image.open(TEST_IMG_PATH + listing_data['banner_icon']['filename']),
        file_extension=listing_data['banner_icon']['filename'].split('.')[-1],
        security_marking=listing_data['banner_icon']['security_marking'],
        image_type=models.ImageType.objects.get(name='banner_icon').name)


    large_banner_icon = models.Image.create_image(
        Image.open(TEST_IMG_PATH + listing_data['large_banner_icon']['filename']),
        file_extension=listing_data['large_banner_icon']['filename'].split('.')[-1],
        security_marking=listing_data['large_banner_icon']['security_marking'],
        image_type=models.ImageType.objects.get(name='large_banner_icon').name)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Listing
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    listing = models.Listing(
        title=listing_data['title'],
        agency=models.Agency.objects.get(short_name=listing_data['agency']),
        listing_type=models.ListingType.objects.get(title=listing_data['listing_type']),
        description=listing_data['description'],
        launch_url=listing_data['launch_url'],
        version_name=listing_data['version_name'],
        unique_name=listing_data['unique_name'],
        small_icon=small_icon,
        large_icon=large_icon,
        banner_icon=banner_icon,
        large_banner_icon=large_banner_icon,
        what_is_new=listing_data['what_is_new'],
        description_short=listing_data['description_short'],
        requirements=listing_data['requirements'],
        is_enabled=listing_data['is_enabled'],
        is_private=listing_data['is_private'],
        is_featured=listing_data['is_featured'],
        iframe_compatible=listing_data['iframe_compatible'],
        security_marking=listing_data['security_marking']
    )
    listing.save()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Contacts
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    for current_contact in listing_data['contacts']:
        listing.contacts.add(models.Contact.objects.get(email=current_contact))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Owners
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    for current_owner in listing_data['owners']:
        listing.owners.add(models.Profile.objects.get(user__username=current_owner))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Categories
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    for current_category in listing_data['categories']:
        listing.categories.add(models.Category.objects.get(title=current_category))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Tags
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    for current_tag in listing_data['tags']:
        current_tag_obj, created = models.Tag.objects.get_or_create(name=current_tag)
        listing.tags.add(current_tag_obj)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Screenshots
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    for current_screenshot_entry in listing_data['screenshots']:
        small_image = models.Image.create_image(
            Image.open(TEST_IMG_PATH + current_screenshot_entry['small_image']['filename']),
            file_extension=current_screenshot_entry['small_image']['filename'].split('.')[-1],
            security_marking=current_screenshot_entry['small_image']['security_marking'],
            image_type=models.ImageType.objects.get(name='small_screenshot').name)



        large_image = models.Image.create_image(
            Image.open(TEST_IMG_PATH + current_screenshot_entry['large_image']['filename']),
            file_extension=current_screenshot_entry['large_image']['filename'].split('.')[-1],
            security_marking=current_screenshot_entry['large_image']['security_marking'],
            image_type=models.ImageType.objects.get(name='large_screenshot').name)


        screenshot = models.Screenshot(small_image=small_image,
                                        large_image=large_image,
                                        listing=listing,
                                        description=current_screenshot_entry['description'],
                                        order=current_screenshot_entry['order'])
        screenshot.save()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Document URLs
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    for current_doc_url_entry in listing_data['doc_urls']:
        current_doc_url_obj = models.DocUrl(name=current_doc_url_entry['name'], url=current_doc_url_entry['url'],
            listing=listing)
        current_doc_url_obj.save()

    # listing_activity
    for listing_activity_entry in listing_builder_dict['listing_activity']:
        listing_activity_action = listing_activity_entry['action']
        listing_activity_author = models.Profile.objects.get(user__username=listing_activity_entry['author'])

        if listing_activity_action == 'CREATED':
            listing_model_access.create_listing(listing_activity_author, listing)
        elif listing_activity_action == 'SUBMITTED':
            listing_model_access.submit_listing(listing_activity_author, listing)
        elif listing_activity_action == 'APPROVED_ORG':
            listing_model_access.approve_listing_by_org_steward(listing_activity_author, listing)
        elif listing_activity_action == 'APPROVED':
            listing_model_access.approve_listing(listing_activity_author, listing)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Reviews
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # listing_review_batch
    create_listing_review_batch(listing, listing_builder_dict['listing_review_batch'])


def run():
    """
    Creates basic sample data
    """
    total_start_time = time_ms()

    # Recreate Index Mapping
    model_access_es.recreate_index_mapping()

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
        Civilian = models.ContactType(name='Civilian')
        Civilian.save()

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

        img = Image.open(TEST_IMG_PATH + 'ministry_of_plenty.png')
        icon = models.Image.create_image(img, file_extension='png',
            security_marking='UNCLASSIFIED', image_type='agency_icon')
        test = models.Agency(title='Test', short_name='Test', icon=icon)
        test.save()

        img = Image.open(TEST_IMG_PATH + 'ministry_of_plenty.png')
        icon = models.Image.create_image(img, file_extension='png',
            security_marking='UNCLASSIFIED', image_type='agency_icon')
        test1 = models.Agency(title='Test 1', short_name='Test 1', icon=icon)
        test1.save()

        img = Image.open(TEST_IMG_PATH + 'ministry_of_plenty.png')
        icon = models.Image.create_image(img, file_extension='png',
            security_marking='UNCLASSIFIED', image_type='agency_icon')
        test2 = models.Agency(title='Test 2', short_name='Test2', icon=icon)
        test2.save()

        img = Image.open(TEST_IMG_PATH + 'ministry_of_plenty.png')
        icon = models.Image.create_image(img, file_extension='png',
            security_marking='UNCLASSIFIED', image_type='agency_icon')
        test3 = models.Agency(title='Test 3', short_name='Test 3', icon=icon)
        test3.save()

        img = Image.open(TEST_IMG_PATH + 'ministry_of_plenty.png')
        icon = models.Image.create_image(img, file_extension='png',
            security_marking='UNCLASSIFIED', image_type='agency_icon')
        test4 = models.Agency(title='Test 4', short_name='Test 4', icon=icon)
        test4.save()

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
                profile_data = yaml.load(stream)
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
            contact_type=models.ContactType.objects.get(name='Civilian'),
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

            current_listing_builder_dict = {
                "listing": {
                    "doc_urls": [
                      {
                        "name": "wiki",
                        "url": "http://www.google.com/wiki"
                      },
                      {
                        "name": "guide",
                        "url": "http://www.google.com/guide"
                      }
                    ],
                    "description_short": "Sends airmail",
                    "owners": [
                      "wsmith"
                    ],
                    "version_name": "1.0.0",
                    "contacts": [
                      "osha@stark.com",
                      "brienne@stark.com"
                    ],
                    "iframe_compatible": False,
                    "requirements": "None",
                    "is_private": False,
                    "screenshots": [
                      {
                        "small_image": {
                          "security_marking": "UNCLASSIFIED",
                          "filename": "screenshot_small.png"
                        },
                        "description": 'airmail screenshot set 1',
                        "order": 0,
                        "large_image": {
                          "security_marking": "UNCLASSIFIED",
                          "filename": "screenshot_large.png"
                        }
                      },
                        {
                          "small_image": {
                            "security_marking": "UNCLASSIFIED",
                            "filename": "screenshot_small.png"
                          },
                          "description": 'airmail screenshot set 2',
                          "order": 1,
                          "large_image": {
                            "security_marking": "UNCLASSIFIED",
                            "filename": "screenshot_large.png"
                          }
                        }
                    ],
                    "unique_name": 'ozp.test.air_mail{0!s}'.format(postfix_dot),
                    "is_featured": True,
                    "launch_url": '{DEMO_APP_ROOT}/demo_apps/centerSampleListings/airMail/index.html'.format_map({'DEMO_APP_ROOT':DEMO_APP_ROOT}),
                    "title": 'Air Mail{0!s}'.format(postfix_space),
                    "categories": [
                      "Communication",
                      "Productivity"
                    ],
                    "tags": [
                      "demo",
                      "example",
                      "tag_{}".format(i)
                    ],
                    "what_is_new": "Nothing really new here",
                    "listing_type": "Web Application",
                    "description": "Sends mail via air",
                    "banner_icon": {
                      "security_marking": "UNCLASSIFIED",
                      "filename": "AirMail_banner_icon.png"
                    },
                    "large_banner_icon": {
                      "security_marking": "UNCLASSIFIED",
                      "filename": "AirMail_large_banner_icon.png"
                    },
                    "small_icon": {
                      "security_marking": "UNCLASSIFIED",
                      "filename": "AirMail_small_icon.png"
                    },
                    "large_icon": {
                      "security_marking": "UNCLASSIFIED",
                      "filename": "AirMail_large_icon.png"
                    },
                    "is_enabled": True,
                    "is_deleted": False,
                    "agency": "Minitrue",
                    "security_marking": "UNCLASSIFIED"
                  },
                  "listing_activity": [
                    {
                      "author": "wsmith",
                      "action": "CREATED",
                      "description": None
                    },
                    {
                      "author": "wsmith",
                      "action": "SUBMITTED",
                      "description": None
                    },
                    {
                      "author": "wsmith",
                      "action": "APPROVED_ORG",
                      "description": None
                    },
                    {
                      "author": "wsmith",
                      "action": "APPROVED",
                      "description": None
                    }
                  ],
                  "library_entries": [
                    {
                      "owner": "wsmith",
                      "position": 0,
                      "folder": None
                    },
                    {
                      "owner": "hodor",
                      "position": 0,
                      "folder": None
                    }
                  ],
                  "listing_review_batch": [
                    {
                      "author": "charrington",
                      "rate": 5,
                      "text": "This app is great - well designed and easy to use"
                    },
                    {
                      "author": "tparsons",
                      "rate": 3,
                      "text": "Air mail is ok - does what it says and no more"
                    },
                    {
                      "author": "syme",
                      "rate": 1,
                      "text": "Air mail crashes all the time - it doesn't even support IE 6!"
                    }
                  ]
                }
            create_listing(current_listing_builder_dict)

    ############################################################################
    #                           Bread Basket
    ############################################################################
    print('== Creating Bread Basket Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)

            current_listing_builder_dict = {
               "listing_activity": [
                 {
                   "action": "CREATED",
                   "description": None,
                   "author": "julia"
                 },
                 {
                   "action": "SUBMITTED",
                   "description": None,
                   "author": "julia"
                 },
                 {
                   "action": "APPROVED_ORG",
                   "description": None,
                   "author": "wsmith"
                 },
                 {
                   "action": "APPROVED",
                   "description": None,
                   "author": "wsmith"
                 }
               ],
               "listing_review_batch": [
                   {
                     "author": "jones",
                     "rate": 2,
                     "text": "This bread is stale!"
                   },
                   {
                     "author": "julia",
                     "rate": 5,
                     "text": "Yum!"
                   },
               ],
               "listing": {
                 "requirements": "None",
                 "is_deleted": False,
                 "categories": [
                   "Health and Fitness",
                   "Shopping"
                 ],
                 "small_icon": {
                   "security_marking": "UNCLASSIFIED",
                   "filename": "BreadBasket_small_icon.png"
                 },
                 "banner_icon": {
                   "security_marking": "UNCLASSIFIED",
                   "filename": "BreadBasket_banner_icon.png"
                 },
                 "is_private": True,
                 "contacts": [
                   "osha@stark.com"
                 ],
                 "tags": [
                   "demo",
                   "example"
                 ],
                 "large_banner_icon": {
                   "security_marking": "UNCLASSIFIED",
                   "filename": "BreadBasket_large_banner_icon.png"
                 },
                 "screenshots": [
                   {
                     "small_image": {
                       "security_marking": "UNCLASSIFIED",
                       "filename": "screenshot_small.png"
                     },
                     "description": None,
                     "order": 0,
                     "large_image": {
                       "security_marking": "UNCLASSIFIED",
                       "filename": "screenshot_large.png"
                     }
                   }
                 ],
                 "what_is_new": "Nothing really new here",
                 "launch_url": "{0!s}/demo_apps/centerSampleListings/breadBasket/index.html".format(DEMO_APP_ROOT),
                 "doc_urls": [],
                 "large_icon": {
                   "security_marking": "UNCLASSIFIED",
                   "filename": "BreadBasket_large_icon.png"
                 },
                 "listing_type": "Web Application",
                 "is_enabled": True,
                 "owners": [
                   "julia"
                 ],
                 "description": "Carries delicious bread",
                 "is_featured": True,
                 "agency": "Minitrue",
                 "unique_name": 'ozp.test.bread_basket{0!s}'.format(postfix_dot),
                 "description_short": "Carries bread",
                 "version_name": "1.0.0",
                 "title": 'Bread Basket{0!s}'.format(postfix_space),
                 "iframe_compatible": False,
                 "security_marking": "UNCLASSIFIED"
               },
               "library_entries": [
                 {
                   "folder": None,
                   "owner": "wsmith",
                   "position": 0
                 }
               ]
            }
            create_listing(current_listing_builder_dict)

    ############################################################################
    #                           Chart Course
    ############################################################################
    print('== Creating Chart Course Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)

            current_listing_builder_dict = {
             "listing_activity": [
               {
                 "action": "CREATED",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "SUBMITTED",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "APPROVED_ORG",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "APPROVED",
                 "description": None,
                 "author": "wsmith"
               }
             ],
             "listing_review_batch": [
                {
                    "author": "wsmith",
                    "rate": 2,
                    "text": "This Chart is bad!"
                },
                {
                    "author": "bigbrother",
                    "rate": 5,
                    "text": "Good Chart!"
                 },
             ],
             "listing": {
               "requirements": "None",
               "is_deleted": False,
               "categories": [
                 "Education",
                 "Tools"
               ],
               "small_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "ChartCourse_small_icon.png"
               },
               "banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "ChartCourse_banner_icon.png"
               },
               "is_private": False,
               "contacts": [
                 "rbaratheon@baratheon.com"
               ],
               "tags": [
                 "demo"
               ],
               "large_banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "ChartCourse_large_banner_icon.png"
               },
               "what_is_new": "Nothing really new here",
               "launch_url": "{0!s}/demo_apps/centerSampleListings/chartCourse/index.html".format(DEMO_APP_ROOT),
               "doc_urls": [],
               "large_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "ChartCourse_large_icon.png"
               },
               "screenshots": [
                 {
                   "small_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_small.png"
                   },
                   "description": None,
                   "order": 0,
                   "large_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_large.png"
                   }
                 }
               ],
               "listing_type": "Web Application",
               "is_enabled": True,
               "owners": [
                 "wsmith"
               ],
               "description": "Chart your course",
               "is_featured": True,
               "agency": "Minitrue",
               "unique_name": 'ozp.test.chartcourse{0!s}'.format(postfix_dot),
               "description_short": "Chart your course",
               "version_name": "1.0.0",

               "title": 'Chart Course{0!s}'.format(postfix_space),
               "iframe_compatible": False,
               "security_marking": "UNCLASSIFIED"
             },
             "library_entries": []
            }
            create_listing(current_listing_builder_dict)

    ############################################################################
    #                           Chatter Box
    ############################################################################
    print('== Creating Chatter Box Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)

            current_listing_builder_dict = {
             "listing_activity": [
               {
                 "action": "CREATED",
                 "description": None,
                 "author": "julia"
               },
               {
                 "action": "SUBMITTED",
                 "description": None,
                 "author": "julia"
               },
               {
                 "action": "APPROVED_ORG",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "APPROVED",
                 "description": None,
                 "author": "wsmith"
               }
             ],
             "listing_review_batch": [],
             "listing": {
               "requirements": "None",
               "is_deleted": False,
               "categories": [
                 "Communication"
               ],
               "small_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "ChatterBox_small_icon.png"
               },
               "banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "ChatterBox_banner_icon.png"
               },
               "is_private": False,
               "contacts": [
                 "rbaratheon@baratheon.com"
               ],
               "tags": [
                 "demo"
               ],
               "large_banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "ChatterBox_large_banner_icon.png"
               },
               "screenshots": [
                 {
                   "small_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_small.png"
                   },
                   "description": None,
                   "order": 0,
                   "large_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_large.png"
                   }
                 }
               ],
               "what_is_new": "Nothing really new here",
               "launch_url": "{0!s}/demo_apps/centerSampleListings/chatterBox/index.html".format(DEMO_APP_ROOT),
               "doc_urls": [],
               "large_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "ChatterBox_large_icon.png"
               },
               "listing_type": "Web Application",
               "is_enabled": True,
               "owners": [
                 "julia"
               ],
               "description": "Chat with people",
               "is_featured": True,
               "agency": "Miniluv",
               "unique_name": 'ozp.test.chatterbox{0!s}'.format(postfix_dot),
               "description_short": "Chat in a box",
               "version_name": "1.0.0",

               "title": 'Chatter Box{0!s}'.format(postfix_space),
               "iframe_compatible": False,
               "security_marking": "UNCLASSIFIED"
             },
             "library_entries": []
            }
            create_listing(current_listing_builder_dict)

    ############################################################################
    #                           Clipboard
    ############################################################################
    print('== Creating Clipboard Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)

            current_listing_builder_dict = {
             "listing_activity": [
               {
                 "action": "CREATED",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "SUBMITTED",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "APPROVED_ORG",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "APPROVED",
                 "description": None,
                 "author": "wsmith"
               }
             ],
             "listing_review_batch": [],
             "listing": {
               "requirements": "None",
               "is_deleted": False,
               "categories": [
                 "Education",
                 "Tools"
               ],
               "small_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "Clipboard_small_icon.png"
               },
               "banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "Clipboard_banner_icon.png"
               },
               "is_private": False,
               "contacts": [
                 "rbaratheon@baratheon.com"
               ],
               "tags": [
                 "demo"
               ],
               "large_banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "Clipboard_large_banner_icon.png"
               },
               "screenshots": [
                 {
                   "small_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_small.png"
                   },
                   "description": None,
                   "order": 0,
                   "large_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_large.png"
                   }
                 }
               ],
               "what_is_new": "Nothing really new here",
               "launch_url": "{0!s}/demo_apps/centerSampleListings/clipboard/index.html".format(DEMO_APP_ROOT),
               "doc_urls": [],
               "large_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "Clipboard_large_icon.png"
               },
               "listing_type": "Web Application",
               "is_enabled": True,
               "owners": [
                 "wsmith"
               ],
               "description": "Clip stuff on a board",
               "is_featured": True,
               "agency": "Minitrue",
               "unique_name": 'ozp.test.clipboard{0!s}'.format(postfix_dot),
               "description_short": "Its a clipboard",
               "version_name": "1.0.0",

               "title": 'Clipboard{0!s}'.format(postfix_space),
               "iframe_compatible": False,
               "security_marking": "UNCLASSIFIED"
             },
             "library_entries": []
            }
            create_listing(current_listing_builder_dict)

    ############################################################################
    #                           FrameIt
    ############################################################################
    print('== Creating FrameIt Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)

            current_listing_builder_dict = {
             "listing_activity": [
               {
                 "action": "CREATED",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "SUBMITTED",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "APPROVED_ORG",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "APPROVED",
                 "description": None,
                 "author": "wsmith"
               }
             ],
             "listing_review_batch": [],
             "listing": {
               "requirements": "None",
               "is_deleted": False,
               "categories": [
                 "Education",
                 "Tools"
               ],
               "small_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "FrameIt_small_icon.png"
               },
               "banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "FrameIt_banner_icon.png"
               },
               "is_private": False,
               "contacts": [
                 "rbaratheon@baratheon.com"
               ],
               "tags": [
                 "demo"
               ],
               "large_banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "FrameIt_large_banner_icon.png"
               },
               "what_is_new": "Nothing really new here",
               "launch_url": "{0!s}/demo_apps/frameit/index.html".format(DEMO_APP_ROOT),
               "doc_urls": [],
               "large_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "FrameIt_large_icon.png"
               },
               "screenshots": [
                 {
                   "small_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_small.png"
                   },
                   "description": None,
                   "order": 0,
                   "large_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_large.png"
                   }
                 }
               ],
               "listing_type": "Web Application",
               "is_enabled": True,
               "owners": [
                 "wsmith"
               ],
               "description": "Show things in an iframe",
               "is_featured": True,
               "agency": "Minitrue",
               "unique_name": 'ozp.test.frameit{0!s}'.format(postfix_dot),
               "description_short": "Its an iframe",
               "version_name": "1.0.0",

               "title":'FrameIt{0!s}'.format(postfix_space),
               "iframe_compatible": False,
               "security_marking": "UNCLASSIFIED"
             },
             "library_entries": []
            }
            create_listing(current_listing_builder_dict)

    ############################################################################
    #                           Hatch Latch
    ############################################################################
    print('== Creating Hatch Latch Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)

            current_listing_builder_dict = {
             "listing_activity": [
               {
                 "action": "CREATED",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "SUBMITTED",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "APPROVED_ORG",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "APPROVED",
                 "description": None,
                 "author": "wsmith"
               }
             ],
             "listing_review_batch": [],
             "listing": {
               "requirements": "None",
               "is_deleted": False,
               "categories": [
                 "Education",
                 "Health and Fitness",
                 "Tools"
               ],
               "small_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "HatchLatch_small_icon.png"
               },
               "banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "HatchLatch_banner_icon.png"
               },
               "is_private": False,
               "contacts": [
                 "rbaratheon@baratheon.com"
               ],
               "tags": [
                 "demo"
               ],
               "large_banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "HatchLatch_large_banner_icon.png"
               },
               "what_is_new": "Nothing really new here",
               "launch_url": "{0!s}/demo_apps/centerSampleListings/hatchLatch/index.html".format(DEMO_APP_ROOT),
               "doc_urls": [],
               "large_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "HatchLatch_large_icon.png"
               },
               "screenshots": [
                 {
                   "small_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_small.png"
                   },
                   "description": None,
                   "order": 0,
                   "large_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_large.png"
                   }
                 }
               ],
               "listing_type": "Web Application",
               "is_enabled": True,
               "owners": [
                 "wsmith"
               ],
               "description": "Hatch latches",
               "is_featured": True,
               "agency": "Minitrue",
               "unique_name": 'ozp.test.hatchlatch{0!s}'.format(postfix_dot),
               "description_short": "Its a hatch latch",
               "version_name": "1.0.0",

               "title": "Hatch Latch{0!s}".format(postfix_space),
               "iframe_compatible": False,
               "security_marking": "UNCLASSIFIED"
             },
             "library_entries": []
            }
            create_listing(current_listing_builder_dict)

    print('== Creating Jot Spot Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)
            ############################################################################
            #                           Jot Spot
            ############################################################################
            current_listing_builder_dict = {
             "listing_activity": [
               {
                 "action": "CREATED",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "SUBMITTED",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "APPROVED_ORG",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "APPROVED",
                 "description": None,
                 "author": "wsmith"
               }
             ],
             "listing_review_batch": [
               {
                 "author": "charrington",
                 "rate": 4,
                 "text": "I really like it"
               }
             ],
             "listing": {
               "requirements": "None",
               "is_deleted": False,
               "categories": [
                 "Education",
                 "Tools"
               ],
               "small_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "JotSpot_small_icon.png"
               },
               "banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "JotSpot_banner_icon.png"
               },
               "is_private": False,
               "contacts": [
                 "rbaratheon@baratheon.com"
               ],
               "tags": [
                 "demo"
               ],
               "large_banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "JotSpot_large_banner_icon.png"
               },
               "screenshots": [
                 {
                   "small_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_small.png"
                   },
                   "description": None,
                   "order": 0,
                   "large_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_large.png"
                   }
                 }
               ],
               "what_is_new": "Nothing really new here",
               "launch_url": "{0!s}/demo_apps/centerSampleListings/jotSpot/index.html".format(DEMO_APP_ROOT),
               "doc_urls": [],
               "large_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "JotSpot_large_icon.png"
               },
               "listing_type": "Web Application",
               "is_enabled": True,
               "owners": [
                 "wsmith"
               ],
               "description": "Jot things down",
               "is_featured": True,
               "agency": "Minitrue",
               "unique_name": "ozp.test.jotspot{0!s}".format(postfix_dot),
               "description_short": "Jot stuff down",
               "version_name": "1.0.0",

               "title": "JotSpot{0!s}".format(postfix_space),
               "iframe_compatible": False,
               "security_marking": "UNCLASSIFIED"
             },
             "library_entries": []
            }
            create_listing(current_listing_builder_dict)

    ############################################################################
    #                           Location Lister
    ############################################################################
    print('== Creating Location Lister Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)

            current_listing_builder_dict = {
             "listing_activity": [
               {
                 "action": "CREATED",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "SUBMITTED",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "APPROVED_ORG",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "APPROVED",
                 "description": None,
                 "author": "wsmith"
               }
             ],
             "listing_review_batch": [
               {
                 "author": "charrington",
                 "rate": 4,
                 "text": "I really like it"
               }
             ],
             "listing": {
               "requirements": "None",
               "is_deleted": False,
               "categories": [
                 "Education",
                 "Tools"
               ],
               "small_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "LocationLister_small_icon.png"
               },
               "banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "LocationLister_banner_icon.png"
               },
               "is_private": False,
               "contacts": [
                 "rbaratheon@baratheon.com"
               ],
               "tags": [
                 "demo"
               ],
               "large_banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "LocationLister_large_banner_icon.png"
               },
               "screenshots": [
                 {
                   "small_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_small.png"
                   },
                   "description": None,
                   "order": 0,
                   "large_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_large.png"
                   }
                 }
               ],
               "what_is_new": "Nothing really new here",
               "launch_url": "{0!s}/demo_apps/locationLister/index.html".format(DEMO_APP_ROOT),
               "doc_urls": [],
               "large_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "LocationLister_large_icon.png"
               },
               "listing_type": "Web Application",
               "is_enabled": True,
               "owners": [
                 "wsmith"
               ],
               "description": "List locations",
               "is_featured": True,
               "agency": "Minitrue",
               "unique_name": "ozp.test.locationlister{0!s}".format(postfix_dot),
               "description_short": "List locations",
               "version_name": "1.0.0",

               "title": "LocationLister{0!s}".format(postfix_space),
               "iframe_compatible": False,
               "security_marking": "UNCLASSIFIED"
             },
             "library_entries": []
            }
            create_listing(current_listing_builder_dict)

    ############################################################################
    #                           Location Viewer
    ############################################################################
    print('== Creating Location Viewer Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)

            current_listing_builder_dict = {
             "listing_activity": [
               {
                 "action": "CREATED",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "SUBMITTED",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "APPROVED_ORG",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "APPROVED",
                 "description": None,
                 "author": "wsmith"
               }
             ],
             "listing_review_batch": [],
             "listing": {
               "requirements": "None",
               "is_deleted": False,
               "categories": [
                 "Education",
                 "Tools"
               ],
               "small_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "LocationViewer_small_icon.png"
               },
               "banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "LocationViewer_banner_icon.png"
               },
               "is_private": False,
               "contacts": [
                 "rbaratheon@baratheon.com"
               ],
               "tags": [
                 "demo"
               ],
               "large_banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "LocationViewer_large_banner_icon.png"
               },
               "screenshots": [
                 {
                   "small_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_small.png"
                   },
                   "description": None,
                   "order": 0,
                   "large_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_large.png"
                   }
                 }
               ],
               "what_is_new": "Nothing really new here",
               "launch_url": "{0!s}/demo_apps/locationViewer/index.html".format(DEMO_APP_ROOT),
               "doc_urls": [],
               "large_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "LocationViewer_large_icon.png"
               },
               "listing_type": "Web Application",
               "is_enabled": True,
               "owners": [
                 "wsmith"
               ],
               "description": "View locations",
               "is_featured": True,
               "agency": "Minitrue",
               "unique_name": "ozp.test.locationviewer{0!s}".format(postfix_dot),
               "description_short": "View locations",
               "version_name": "1.0.0",

               "title": "LocationViewer{0!s}".format(postfix_space),
               "iframe_compatible": False,
               "security_marking": "UNCLASSIFIED"
             },
             "library_entries": []
            }
            create_listing(current_listing_builder_dict)

    ############################################################################
    #                           Location Analyzer
    ############################################################################
    print('== Creating Location Analyzer Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)

            current_listing_builder_dict = {
             "listing_activity": [
               {
                 "action": "CREATED",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "SUBMITTED",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "APPROVED_ORG",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "APPROVED",
                 "description": None,
                 "author": "wsmith"
               }
             ],
             "listing_review_batch": [],
             "listing": {
               "requirements": "None",
               "is_deleted": False,
               "categories": [
                 "Education",
                 "Tools"
               ],
               "small_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "LocationAnalyzer_small_icon.png"
               },
               "banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "LocationAnalyzer_banner_icon.png"
               },
               "is_private": False,
               "contacts": [
                 "rbaratheon@baratheon.com"
               ],
               "tags": [
                 "demo"
               ],
               "large_banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "LocationAnalyzer_large_banner_icon.png"
               },
               "what_is_new": "Nothing really new here",
               "launch_url": '{0!s}/demo_apps/locationAnalyzer/index.html'.format(DEMO_APP_ROOT),
               "doc_urls": [],
               "large_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "LocationAnalyzer_large_icon.png"
               },
               "screenshots": [
                 {
                   "small_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_small.png"
                   },
                   "description": None,
                   "order": 0,
                   "large_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_large.png"
                   }
                 }
               ],
               "listing_type": "Web Application",
               "is_enabled": True,
               "owners": [
                 "wsmith"
               ],
               "description": "Analyze locations",
               "is_featured": True,
               "agency": "Minitrue",
               "unique_name": 'ozp.test.locationanalyzer{0!s}'.format(postfix_dot),
               "description_short": "Analyze locations",
               "version_name": "1.0.0",

               "title": 'LocationAnalyzer{0!s}'.format(postfix_space),
               "iframe_compatible": False,
               "security_marking": "UNCLASSIFIED"
             },
             "library_entries": []
            }
            create_listing(current_listing_builder_dict)

    ############################################################################
    #                           Skybox
    ############################################################################
    print('== Creating Skybox Listings')
    with transaction.atomic():
        for i in range(0, 10):
            postfix_space = "" if (i == 0) else " " + str(i)
            postfix_dot = "" if (i == 0) else "." + str(i)

            current_listing_builder_dict = {
             "listing_activity": [
               {
                 "action": "CREATED",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "SUBMITTED",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "APPROVED_ORG",
                 "description": None,
                 "author": "wsmith"
               },
               {
                 "action": "APPROVED",
                 "description": None,
                 "author": "wsmith"
               }
             ],
             "listing_review_batch": [],
             "listing": {
               "requirements": "None",
               "is_deleted": False,
               "categories": [
                 "Education",
                 "Tools"
               ],
               "small_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "Skybox_small_icon.png"
               },
               "banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "Skybox_banner_icon.png"
               },
               "is_private": False,
               "contacts": [
                 "rbaratheon@baratheon.com"
               ],
               "tags": [
                 "demo"
               ],
               "large_banner_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "Skybox_large_banner_icon.png"
               },
               "what_is_new": "It's a box in the sky",
               "launch_url": '{0!s}/demo_apps/Skybox/index.html'.format(DEMO_APP_ROOT),
               "doc_urls": [],
               "large_icon": {
                 "security_marking": "UNCLASSIFIED",
                 "filename": "Skybox_large_icon.png"
               },
               "screenshots": [
                 {
                   "small_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_small.png"
                   },
                   "description": None,
                   "order": 0,
                   "large_image": {
                     "security_marking": "UNCLASSIFIED",
                     "filename": "screenshot_large.png"
                   }
                 }
               ],
               "listing_type": "Web Application",
               "is_enabled": True,
               "owners": [
                 "david",
                 "pmurt"
               ],
               "description": "Sky Overlord",
               "is_featured": True,
               "agency": "Miniluv",
               "unique_name": 'ozp.test.skybox{0!s}'.format(postfix_dot),
               "description_short": "Sky Overlord",
               "version_name": "1.0.0",

               "title": 'Skybox{0!s}'.format(postfix_space),
               "iframe_compatible": False,
               "security_marking": "UNCLASSIFIED"
             },
             "library_entries": []
            }
            create_listing(current_listing_builder_dict)

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
