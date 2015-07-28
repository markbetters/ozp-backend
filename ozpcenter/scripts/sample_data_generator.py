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
    secret = models.AccessControl(title='SECRET')
    secret.save()
    secret_n = models.AccessControl(title='SECRET//NOVEMBER')
    secret_n.save()
    ts = models.AccessControl(title='TOP SECRET')
    ts.save()
    ts_s = models.AccessControl(title='TOP SECRET//SIERRA')
    ts_s.save()
    ts_st = models.AccessControl(title='TOP SECRET//SIERRA//TANGO')
    ts_st.save()
    ts_stgh = models.AccessControl(title='TOP SECRET//SIERRA//TANGO//GOLF//HOTEL')
    ts_stgh.save()

    ts_n = models.AccessControl(title='TOP SECRET//NOVEMBER')
    ts_n.save()
    ts_sn = models.AccessControl(title='TOP SECRET//SIERRA//NOVEMBER')
    ts_sn.save()
    ts_stn = models.AccessControl(title='TOP SECRET//SIERRA//TANGO//NOVEMBER')
    ts_stn.save()
    ts_stghn = models.AccessControl(title='TOP SECRET//SIERRA//TANGO//GOLF//HOTEL//NOVEMBER')
    ts_stghn.save()

    ############################################################################
    #                           Categories
    ############################################################################
    books_ref = models.Category(title="Books and Reference",
        description="Things made of paper")
    books_ref.save()
    business = models.Category(title="Business",
        description="For making money")
    business.save()
    communication = models.Category(title="Communication",
        description="Moving info between people and things")
    communication.save()
    education = models.Category(title="Education",
        description="Educational in nature")
    education.save()
    entertainment = models.Category(title="Entertainment",
        description="For fun")
    entertainment.save()
    finance = models.Category(title="Finance",
        description="For managing money")
    finance.save()
    health_fitness = models.Category(title="Health and Fitness",
        description="Be healthy, be fit")
    health_fitness.save()
    media_video = models.Category(title="Media and Video",
        description="Videos and media stuff")
    media_video.save()
    music_audio = models.Category(title="Music and Audio",
        description="Using your ears")
    music_audio.save()
    news = models.Category(title="News",
        description="What's happening where")
    news.save()
    productivity = models.Category(title="Productivity",
        description="Do more in less time")
    productivity.save()
    shopping = models.Category(title="Shopping",
        description="For spending your money")
    shopping.save()
    sports = models.Category(title="Sports",
        description="Score more points than your opponent")
    sports.save()
    tools = models.Category(title="Tools",
        description="Tools and Utilities")
    tools.save()
    weather = models.Category(title="Weather",
        description="Get the temperature")
    weather.save()


    ############################################################################
    #                           Contact Types
    ############################################################################
    civillian = models.ContactType(name='Civillian')
    civillian.save()
    government = models.ContactType(name='Government')
    government.save()
    military = models.ContactType(name='Military')
    military.save()

    ############################################################################
    #                           Listing Types
    ############################################################################
    web_app = models.ListingType(title='web application',
        description='web applications')
    web_app.save()
    widget = models.ListingType(title='widgets',
        description='widget things')
    widget.save()
    dev_resource = models.ListingType(title='developer resource',
        description='APIs and resources for developers')
    dev_resource.save()

    ############################################################################
    #                           Image Types
    ############################################################################
    # Note: these image sizes do not represent those that should be used in
    # production
    small_icon_type = models.ImageType(name='listing_small_icon',
        max_size_bytes='4096')
    small_icon_type.save()
    large_icon_type = models.ImageType(name='listing_large_icon',
        max_size_bytes='8192')
    large_icon_type.save()
    banner_icon_type = models.ImageType(name='listing_banner_icon',
        max_size_bytes='2097152')
    banner_icon_type.save()
    large_banner_icon_type = models.ImageType(name='listing_large_banner_icon',
        max_size_bytes='2097152')
    large_banner_icon_type.save()
    small_screenshot_type = models.ImageType(name='listing_small_screenshot',
        max_size_bytes='1048576')
    small_screenshot_type.save()
    large_screenshot_type = models.ImageType(name='listing_large_screenshot',
        max_size_bytes='1048576')
    large_screenshot_type.save()
    intent_icon_type = models.ImageType(name='intent_icon',
        max_size_bytes='2097152')
    intent_icon_type.save()
    agency_icon_type = models.ImageType(name='agency_icon',
        max_size_bytes='2097152')
    agency_icon_type.save()

    ############################################################################
    #                           Intents
    ############################################################################
    # TODO: more realistic data
    img = Image.open(TEST_IMG_PATH + 'android.png')
    icon = models.Image.create_image(img, file_extension='png',
        access_control='UNCLASSIFIED', image_type=intent_icon_type.name)
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
    minitrue = models.Agency(title='Ministry of Truth', short_name='Minitrue',
        icon=icon)
    minitrue.save()

    img = Image.open(TEST_IMG_PATH + 'ministry_of_peace.png')
    icon = models.Image.create_image(img, file_extension='png',
        access_control='UNCLASSIFIED', image_type='agency_icon')
    minipax = models.Agency(title='Ministry of Peace', short_name='Minipax',
        icon=icon)
    minipax.save()

    img = Image.open(TEST_IMG_PATH + 'ministry_of_love.jpeg')
    icon = models.Image.create_image(img, file_extension='jpeg',
        access_control='UNCLASSIFIED', image_type='agency_icon')
    miniluv = models.Agency(title='Ministry of Love', short_name='Miniluv',
        icon=icon)
    miniluv.save()

    img = Image.open(TEST_IMG_PATH + 'ministry_of_plenty.png')
    icon = models.Image.create_image(img, file_extension='png',
        access_control='UNCLASSIFIED', image_type='agency_icon')
    miniplenty = models.Agency(title='Ministry of Plenty',
        short_name='Miniplenty', icon=icon)
    miniplenty.save()

    ############################################################################
    #                               Tags
    ############################################################################
    demo =  models.Tag(name='demo')
    demo.save()
    example = models.Tag(name='example')
    example.save()

    ############################################################################
    #                               Org Stewards
    ############################################################################
    winston = models.Profile.create_user('wsmith',
        email='wsmith@oceania.gov',
        display_name='Winston Smith',
        bio='I work at the Ministry of Truth',
        access_control=ts_stn.title,
        organizations=['Ministry of Truth'],
        stewarded_organizations=['Ministry of Truth'],
        groups=['ORG_STEWARD']
    )

    julia = models.Profile.create_user('julia',
        email='julia@oceania.gov',
        display_name='Julia Dixon',
        bio='An especially zealous propagandist',
        access_control=ts_s.title,
        organizations=['Ministry of Truth'],
        stewarded_organizations=['Ministry of Truth', 'Ministry of Love'],
        groups=['ORG_STEWARD']
    )
    obrien = models.Profile.create_user('obrien',
        email='obrien@oceania.gov',
        display_name='O\'brien',
        bio='I will find you, winston and julia',
        access_control=ts_stghn.title,
        organizations=['Ministry of Peace'],
        stewarded_organizations=['Ministry of Peace', 'Ministry of Plenty'],
        groups=['ORG_STEWARD']
    )

    ############################################################################
    #                               Apps Mall Stewards
    ############################################################################
    big_brother = models.Profile.create_user('bigbrother',
        email='bigbrother@oceania.gov',
        display_name='Big Brother',
        bio='I make everyones life better',
        access_control=ts_stghn.title,
        organizations=['Ministry of Truth', 'Ministry of Love',
        'Ministry of Peace', 'Ministry of Plenty'],
        groups=['APPS_MALL_STEWARD']
    )

    big_brother2 = models.Profile.create_user('bigbrother2',
        email='bigbrother2@oceania.gov',
        display_name='Big Brother2',
        bio='I also make everyones life better',
        access_control=ts_stghn.title,
        organizations=['Ministry of Truth', 'Ministry of Love',
        'Ministry of Peace', 'Ministry of Plenty'],
        groups=['APPS_MALL_STEWARD']
    )

    ############################################################################
    #                               Regular user
    ############################################################################
    aaronson = models.Profile.create_user('aaronson',
        email='aaronson@airstripone.com',
        display_name='Aaronson',
        bio='Nothing special',
        access_control=secret_n.title,
        organizations=['Ministry of Love'],
        groups=['USER']
    )

    jones = models.Profile.create_user('jones',
        email='jones@airstripone.com',
        display_name='Jones',
        bio='I am a normal person',
        access_control=secret_n.title,
        organizations=['Ministry of Truth'],
        groups=['USER']
    )

    rutherford = models.Profile.create_user('rutherford',
        email='rutherford@airstripone.com',
        display_name='Rutherford',
        bio='I am a normal person',
        access_control=secret.title,
        organizations=['Ministry of Plenty'],
        groups=['USER']
    )

    syme = models.Profile.create_user('syme',
        email='syme@airstripone.com',
        display_name='Syme',
        bio='I am too smart for my own good',
        access_control=ts_s.title,
        organizations=['Ministry of Peace'],
        groups=['USER']
    )

    tparsons = models.Profile.create_user('tparsons',
        email='tparsons@airstripone.com',
        display_name='Tom Parsons',
        bio='I am uneducated and loyal',
        access_control=unclass.title,
        organizations=['Ministry of Peace', 'Ministry of Love'],
        groups=['USER']
    )

    charrington = models.Profile.create_user('charrington',
        email='charrington@airstripone.com',
        display_name='Charrington',
        bio='A member of the Thought Police',
        access_control=ts_stghn.title,
        organizations=['Ministry of Peace', 'Ministry of Love',
        'Ministry of Truth'],
        groups=['USER']
    )

    ############################################################################
    #                           System Notifications
    ############################################################################
    # create some notifications that expire next week
    next_week = datetime.datetime.now() + datetime.timedelta(days=7)
    eastern = pytz.timezone('US/Eastern')
    next_week = eastern.localize(next_week)
    n1 = models.Notification(message='System will be going down for \
        approximately 30 minutes on X/Y at 1100Z',
        expires_date=next_week, author=winston)
    n1.save()
    n2 = models.Notification(message='System will be functioning in a \
        degredaded state between 1800Z-0400Z on A/B',
        expires_date=next_week, author=julia)
    n2.save()

    # create some expired notifications
    last_week = datetime.datetime.now() - datetime.timedelta(days=7)
    last_week = eastern.localize(last_week)
    n1 = models.Notification(message='System will be going down for \
        approximately 30 minutes on C/D at 1700Z',
        expires_date=last_week, author=winston)
    n1.save()
    n2 = models.Notification(message='System will be functioning in a \
        degredaded state between 2100Z-0430Z on F/G',
        expires_date=last_week, author=julia)
    n2.save()

    ############################################################################
    #                           Contacts
    ############################################################################
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
        access_control=unclass.title, image_type=small_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'AirMail32.png')
    large_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=large_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'AirMail.png')
    banner_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=banner_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'AirMailFeatured.png')
    large_banner_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=large_banner_icon_type.name)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Listing
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    listing = models.Listing(
        title='Air Mail',
        agency=minitrue,
        app_type=web_app,
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
    listing.save()
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Contacts
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    listing.contacts.add(osha)
    listing.contacts.add(brienne)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Owners
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    listing.owners.add(winston)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Categories
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    listing.categories.add(communication)
    listing.categories.add(productivity)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Tags
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    listing.tags.add(demo)
    listing.tags.add(example)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Screenshots
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    img = Image.open(TEST_IMG_PATH + 'screenshot_small.png')
    small_img = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=small_screenshot_type.name)
    img = Image.open(TEST_IMG_PATH + 'screenshot_large.png')
    large_img = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=large_screenshot_type.name)
    screenshot = models.Screenshot(small_image=small_img,
        large_image=large_img,
        listing=listing)
    screenshot.save()
    listing.screenshots.add(screenshot)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Notifications
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    notification1 = models.Notification(message='Air Mail update next week',
        expires_date=next_week, listing=listing, author=winston)
    notification1.save()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Reviews
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    air_mail_comment_1 = models.ItemComment(
        text="This app is great - well designed and easy to use",
        rate=5,
        author=charrington,
        listing=listing)
    air_mail_comment_1.save()

    air_mail_comment_2 = models.ItemComment(
        text="Air mail is ok - does what it says and no more",
        rate=3,
        author=tparsons,
        listing=listing)
    air_mail_comment_2.save()

    air_mail_comment_3 = models.ItemComment(
        text="Air mail crashes all the time - it doesn't even support IE 6!",
        rate=1,
        author=syme,
        listing=listing)
    air_mail_comment_3.save()

    ############################################################################
    #                           Bread Basket
    ############################################################################
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Icons
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    img = Image.open(TEST_IMG_PATH + 'BreadBasket16.png')
    small_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=small_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'BreadBasket32.png')
    large_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=large_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'BreadBasket.png')
    banner_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=banner_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'BreadBasketFeatured.png')
    large_banner_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=large_banner_icon_type.name)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Listing
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    listing = models.Listing(
        title='Bread Basket',
        agency=minitrue,
        app_type=web_app,
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
    listing.save()

    listing.contacts.add(osha)
    listing.owners.add(julia)
    listing.categories.add(health_fitness)
    listing.categories.add(shopping)
    listing.screenshots.add(screenshot)

    listing.tags.add(demo)
    listing.tags.add(example)

    ############################################################################
    #                           Chart Course
    ############################################################################
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Icons
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    img = Image.open(TEST_IMG_PATH + 'ChartCourse16.png')
    small_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=small_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'ChartCourse32.png')
    large_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=large_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'ChartCourse.png')
    banner_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=banner_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'ChartCourseFeatured.png')
    large_banner_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=large_banner_icon_type.name)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Listing
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    listing = models.Listing(
        title='Chart Course',
        agency=minitrue,
        app_type=web_app,
        description='Chart your course',
        launch_url='https://www.google.com/chartcourse',
        version_name='1.0.0',
        unique_name='ozp.test.chartcourse',
        small_icon=small_icon,
        large_icon=large_icon,
        banner_icon=banner_icon,
        large_banner_icon=large_banner_icon,
        what_is_new='Nothing really new here',
        description_short='Chart your course',
        requirements='None',
        approval_status=models.ApprovalStatus.APPROVED,
        is_enabled=True,
        is_featured=True,
        singleton=False,
        is_private=False,
        access_control=unclass
    )
    listing.save()
    listing.contacts.add(rob_baratheon)
    listing.owners.add(winston)
    listing.categories.add(tools)
    listing.categories.add(education)
    listing.tags.add(demo)
    listing.screenshots.add(screenshot)


    ############################################################################
    #                           Chatter Box
    ############################################################################
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Icons
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    img = Image.open(TEST_IMG_PATH + 'ChatterBox16.png')
    small_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=small_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'ChatterBox32.png')
    large_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=large_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'ChatterBox.png')
    banner_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=banner_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'ChatterBoxFeatured.png')
    large_banner_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=large_banner_icon_type.name)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Listing
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    listing = models.Listing(
        title='Chatter Box',
        agency=miniluv,
        app_type=web_app,
        description='Chat with people',
        launch_url='https://www.google.com/chatterbox',
        version_name='1.0.0',
        unique_name='ozp.test.chatterbox',
        small_icon=small_icon,
        large_icon=large_icon,
        banner_icon=banner_icon,
        large_banner_icon=large_banner_icon,
        what_is_new='Nothing really new here',
        description_short='Chat in a box',
        requirements='None',
        approval_status=models.ApprovalStatus.APPROVED,
        is_enabled=True,
        is_featured=True,
        singleton=False,
        is_private=False,
        access_control=unclass
    )
    listing.save()
    listing.contacts.add(rob_baratheon)
    listing.owners.add(julia)
    listing.categories.add(communication)
    listing.tags.add(demo)
    listing.screenshots.add(screenshot)

    ############################################################################
    #                           Clipboard
    ############################################################################
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Icons
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    img = Image.open(TEST_IMG_PATH + 'Clipboard16.png')
    small_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=small_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'Clipboard32.png')
    large_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=large_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'Clipboard.png')
    banner_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=banner_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'ClipboardFeatured.png')
    large_banner_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=large_banner_icon_type.name)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Listing
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    listing = models.Listing(
        title='Clipboard',
        agency=minitrue,
        app_type=web_app,
        description='Clip stuff on a board',
        launch_url='https://www.google.com/clipboard',
        version_name='1.0.0',
        unique_name='ozp.test.clipboard',
        small_icon=small_icon,
        large_icon=large_icon,
        banner_icon=banner_icon,
        large_banner_icon=large_banner_icon,
        what_is_new='Nothing really new here',
        description_short='Its a clipboard',
        requirements='None',
        approval_status=models.ApprovalStatus.APPROVED,
        is_enabled=True,
        is_featured=True,
        singleton=False,
        is_private=False,
        access_control=unclass
    )
    listing.save()
    listing.contacts.add(rob_baratheon)
    listing.owners.add(winston)
    listing.categories.add(tools)
    listing.categories.add(education)
    listing.tags.add(demo)
    listing.screenshots.add(screenshot)

    ############################################################################
    #                           FrameIt
    ############################################################################
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Icons
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    img = Image.open(TEST_IMG_PATH + 'FrameIt16.png')
    small_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=small_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'FrameIt32.png')
    large_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=large_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'FrameIt.png')
    banner_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=banner_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'FrameItFeatured.png')
    large_banner_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=large_banner_icon_type.name)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Listing
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    listing = models.Listing(
        title='FrameIt',
        agency=minitrue,
        app_type=web_app,
        description='Show things in an iframe',
        launch_url='https://www.google.com/frameit',
        version_name='1.0.0',
        unique_name='ozp.test.frameit',
        small_icon=small_icon,
        large_icon=large_icon,
        banner_icon=banner_icon,
        large_banner_icon=large_banner_icon,
        what_is_new='Nothing really new here',
        description_short='Its an iframe',
        requirements='None',
        approval_status=models.ApprovalStatus.APPROVED,
        is_enabled=True,
        is_featured=True,
        singleton=False,
        is_private=False,
        access_control=unclass
    )
    listing.save()
    listing.contacts.add(rob_baratheon)
    listing.owners.add(winston)
    listing.categories.add(tools)
    listing.categories.add(education)
    listing.tags.add(demo)
    listing.screenshots.add(screenshot)

    ############################################################################
    #                           Hatch Latch
    ############################################################################
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Icons
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    img = Image.open(TEST_IMG_PATH + 'HatchLatch16.png')
    small_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=small_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'HatchLatch32.png')
    large_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=large_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'HatchLatch.png')
    banner_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=banner_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'HatchLatchFeatured.png')
    large_banner_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=large_banner_icon_type.name)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Listing
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    listing = models.Listing(
        title='Hatch Latch',
        agency=minitrue,
        app_type=web_app,
        description='Hatch latches',
        launch_url='https://www.google.com/hatchlatch',
        version_name='1.0.0',
        unique_name='ozp.test.hatchlatch',
        small_icon=small_icon,
        large_icon=large_icon,
        banner_icon=banner_icon,
        large_banner_icon=large_banner_icon,
        what_is_new='Nothing really new here',
        description_short='Its a hatch latch',
        requirements='None',
        approval_status=models.ApprovalStatus.APPROVED,
        is_enabled=True,
        is_featured=True,
        singleton=False,
        is_private=False,
        access_control=unclass
    )
    listing.save()
    listing.contacts.add(rob_baratheon)
    listing.owners.add(winston)
    listing.categories.add(tools)
    listing.categories.add(education)
    listing.categories.add(health_fitness)
    listing.tags.add(demo)
    listing.screenshots.add(screenshot)

    ############################################################################
    #                           Jot Spot
    ############################################################################
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Icons
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    img = Image.open(TEST_IMG_PATH + 'JotSpot16.png')
    small_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=small_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'JotSpot32.png')
    large_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=large_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'JotSpot.png')
    banner_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=banner_icon_type.name)
    img = Image.open(TEST_IMG_PATH + 'JotSpotFeatured.png')
    large_banner_icon = models.Image.create_image(img, file_extension='png',
        access_control=unclass.title, image_type=large_banner_icon_type.name)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #                           Listing
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    listing = models.Listing(
        title='JotSpot',
        agency=minitrue,
        app_type=web_app,
        description='Jot things down',
        launch_url='https://www.google.com/jotspot',
        version_name='1.0.0',
        unique_name='ozp.test.jotspot',
        small_icon=small_icon,
        large_icon=large_icon,
        banner_icon=banner_icon,
        large_banner_icon=large_banner_icon,
        what_is_new='Nothing really new here',
        description_short='Jot stuff down',
        requirements='None',
        approval_status=models.ApprovalStatus.APPROVED,
        is_enabled=True,
        is_featured=True,
        singleton=False,
        is_private=False,
        access_control=unclass
    )
    listing.save()
    listing.contacts.add(rob_baratheon)
    listing.owners.add(winston)
    listing.categories.add(tools)
    listing.categories.add(education)
    listing.tags.add(demo)
    listing.screenshots.add(screenshot)

    ############################################################################
    #                           Library
    ############################################################################
    # bookmark listings
    library_entry = models.ApplicationLibraryEntry(
        owner=winston,
        listing=models.Listing.objects.get(unique_name='ozp.test.bread_basket'))
    library_entry.save()

    library_entry = models.ApplicationLibraryEntry(
        owner=winston,
        listing=models.Listing.objects.get(unique_name='ozp.test.air_mail'))
    library_entry.save()


if __name__ == "__main__":
    run()