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


def create_library_entries(library_entries):
    """
    Create Bookmarks for users

    # library_entries = [{'folder': None, 'listing_unique_name': 'ozp.test.air_mail', 'owner': 'wsmith', 'position': 0},
    #    {'folder': None, 'listing_unique_name': 'ozp.test.air_mail', 'owner': 'hodor', 'position': 0},...]
    """
    print('Creating Library Entries...')
    for current_entry in library_entries:
        current_profile = models.Profile.objects.filter(user__username=current_entry['owner']).first()

        library_entry = models.ApplicationLibraryEntry(
            owner=current_profile,
            listing=models.Listing.objects.get(unique_name=current_entry['listing_unique_name']),
            folder=current_entry['folder'],
            position=current_entry['position'])
        library_entry.save()
    print('Finished Library Entries...')


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
        launch_url=listing_data['launch_url'].format_map({'DEMO_APP_ROOT':DEMO_APP_ROOT}),
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
    #                           Contact Types and Contacts
    ############################################################################
    with transaction.atomic():
        contact_data = None
        with open(os.path.join(TEST_DATA_PATH, 'contacts.yaml'), 'r') as stream:
            try:
                contact_data = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        for contact_type in contact_data['contact_types']:
            current_contact_type_obj = models.ContactType(name=contact_type)
            current_contact_type_obj.save()

        for current_contact in contact_data['contacts']:
            if not models.Contact.objects.filter(email=current_contact['email']).exists():
                current_contact_obj = models.Contact(name=current_contact['name'],
                                                     organization=current_contact['organization'],
                                                     contact_type=models.ContactType.objects.get(
                                                        name=current_contact['contact_type']),
                                                     email=current_contact['email'],
                                                     unsecure_phone=current_contact['unsecure_phone'])
                current_contact_obj.save()

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
    # ===========================================================================
    #                           Listings
    #                           Listings from File
    # ===========================================================================
    with transaction.atomic():  # Maybe too large of a transaction
        listings_data = None
        with open(os.path.join(TEST_DATA_PATH, 'listings.yaml'), 'r') as stream:
            try:
                listings_data = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        library_entries = []
        for current_listing_data in listings_data:
            listing_unique_name = current_listing_data['listing']['unique_name']
            listing_library_entries = current_listing_data['library_entries']

            if listing_library_entries:

                for listing_library_entry in listing_library_entries:
                    listing_library_entry['listing_unique_name'] = listing_unique_name
                    library_entries.append(listing_library_entry)

            create_listing(current_listing_data)

    ############################################################################
    #                           Library (bookmark listings)
    ############################################################################
    with transaction.atomic():
        create_library_entries(library_entries)

    for current_unique_name in [entry['listing_unique_name'] for entry in library_entries]:
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
