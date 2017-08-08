"""
Purpose of this script: Export All Listings for sample data generator

"""
# Format for each listing
# {
#     "listing_activity": [
#       {
#         "action": "CREATED",
#         "author": "wsmith",
#         "description": null
#       },
#       {
#         "action": "SUBMITTED",
#         "author": "wsmith",
#         "description": null
#       },
#       {
#         "action": "APPROVED_ORG",
#         "author": "wsmith",
#         "description": null
#       },
#       {
#         "action": "APPROVED",
#         "author": "wsmith",
#         "description": null
#       }
#     ],
#     "library_entries": [
#       {
#         "owner": "wsmith",
#         "position": 0,
#         "folder": null
#       },
#       {
#         "owner": "hodor",
#         "position": 0,
#         "folder": null
#       }
#     ],
#     "listing_review_batch": [
#       {
#         "text": "This app is great - well designed and easy to use",
#         "author": "charrington",
#         "rate": 5
#       },
#       {
#         "text": "Air mail is ok - does what it says and no more",
#         "author": "tparsons",
#         "rate": 3
#       },
#       {
#         "text": "Air mail crashes all the time - it doesn't even support IE 6!",
#         "author": "syme",
#         "rate": 1
#       }
#     ],
#     "listing": {
#       "large_icon": {
#         "security_marking": "UNCLASSIFIED",
#         "filename": "Air_Mail_large_icon.png"
#       },
#       "doc_urls": [
#         {
#           "url": "http://www.google.com/wiki",
#           "name": "wiki"
#         },
#         {
#           "url": "http://www.google.com/guide",
#           "name": "guide"
#         }agency
#       ],
#       "what_is_new": "Nothing really new here",
#       "description_short": "Sends airmail",
#       "categories": [
#         "Communication",
#         "Productivity"
#       ],
#       "description": "Sends mail via air",
#       "tags": [
#         "demo",
#         "example",
#         "tag_0"
#       ],
#       "launch_url": "https://localhost:8443/demo_apps/centerSampleListings/airMail/index.html",
#       "is_featured": true,
#       "is_deleted": false,
#       "is_private": false,
#       "screenshots": [
#         {
#           "large_image": {
#             "security_marking": "UNCLASSIFIED",
#             "filename": "AirMail_0_screenshot_large_icon.png"
#           },
#           "small_image": {
#             "security_marking": "UNCLASSIFIED",
#             "filename": "AirMail_0_screenshot_small_icon.png"
#           },
#           "description": null,
#           "order": 0
#         }
#       ],
#       "unique_name": "ozp.test.air_mail",
#       "iframe_compatible": false,
#       "title": "Air Mail",
#       "listing_type": "Web Application",
#       "requirements": "None",
#       "small_icon": {
#         "security_marking": "UNCLASSIFIED",
#         "filename": "Air_Mail_small_icon.png"
#       },
#       "owners": [
#         "wsmith"
#       ],
#       "version_name": "1.0.0",
#       "is_enabled": true,
#       "large_banner_icon": {
#         "security_marking": "UNCLASSIFIED",
#         "filename": "Air_Mail_large_banner_icon.png"
#       },
#       "banner_icon": {
#         "security_marking": "UNCLASSIFIED",
#         "filename": "Air_Mail_banner_icon.png"
#       },
#       "contacts": [
#         "osha@stark.com",
#         "brienne@stark.com"
#       ],
#       "security_marking": "UNCLASSIFIED",
#       "agency": "Minitrue"
#     }
#   }

import os
import sys
# import json
import yaml

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../../')))

from django.conf import settings
from ozp.storage import media_storage
from ozpcenter import models
from shutil import copy2
from shutil import rmtree

COPY_IMG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../', 'test_images_copy') + '/'
DEMO_APP_ROOT = settings.OZP['DEMO_APP_ROOT']


def run():
    if os.path.exists(COPY_IMG_PATH):
        # TODO: Verify that rmtree works
        rmtree(COPY_IMG_PATH)

    if not os.path.exists(COPY_IMG_PATH):
        os.mkdir(COPY_IMG_PATH)

    contacts_list = []
    for current_contact in models.Contact.objects.iterator():
        contact = {}
        contact['name'] = current_contact.name
        contact['organization'] = current_contact.organization
        contact['contact_type'] = current_contact.contact_type.name
        contact['email'] = current_contact.email
        contact['unsecure_phone'] = current_contact.unsecure_phone
        contact['secure_phone'] = current_contact.secure_phone
        contacts_list.append(contact)
    output_dict = {'contacts': contacts_list}

    output_dict['contact_types'] = [contact_type.name for contact_type in models.ContactType.objects.iterator()]

    with open('contacts.yaml', 'w') as file_stream:
        yaml.dump(output_dict, file_stream, indent=2, default_flow_style=False)

    output_list = []
    for current_listing in models.Listing.objects.iterator():
        listing = {}
        listing['agency'] = current_listing.agency.short_name
        listing['title'] = current_listing.title
        listing['listing_type'] = current_listing.listing_type.title
        listing['description'] = current_listing.description

        if current_listing.launch_url:
            listing['launch_url'] = current_listing.launch_url.replace(DEMO_APP_ROOT, '{DEMO_APP_ROOT}')
        else:
            listing['launch_url'] = '{DEMO_APP_ROOT}/default/index.html'

        listing['version_name'] = current_listing.version_name
        listing['unique_name'] = current_listing.unique_name
        listing['what_is_new'] = current_listing.what_is_new
        listing['description_short'] = current_listing.description_short
        listing['requirements'] = current_listing.requirements
        listing['is_enabled'] = current_listing.is_enabled
        listing['is_featured'] = current_listing.is_featured
        listing['is_deleted'] = current_listing.is_deleted
        listing['iframe_compatible'] = current_listing.iframe_compatible
        listing['security_marking'] = current_listing.security_marking
        listing['is_private'] = current_listing.is_private

        # "intents": [],
        listing['doc_urls'] = [{'name': doc_url.name, 'url': doc_url.url} for doc_url in models.DocUrl.objects.filter(listing=current_listing).all()]
        listing['owners'] = [current_owner.user.username for current_owner in current_listing.owners.iterator()]
        listing['tags'] = [current_tag.name for current_tag in current_listing.tags.iterator()]
        listing['categories'] = [current_category.title for current_category in current_listing.categories.iterator()]
        listing['contacts'] = [current_contact.email for current_contact in current_listing.contacts.iterator()]

        screenshot_entry_counter = 0
        screenshot_entry_list = []
        for screenshot_entry in current_listing.screenshots.iterator():
            screenshot_image_types = ['small_image', 'large_image']
            screenshot_entry_dict = {}
            screenshot_entry_dict['order'] = screenshot_entry.order
            screenshot_entry_dict['description'] = screenshot_entry.description

            for current_image_type in screenshot_image_types:
                current_image = getattr(screenshot_entry, current_image_type)
                current_image_path = str(current_image.id) + '_' + current_image.image_type.name + '.' + current_image.file_extension

                with media_storage.open(current_image_path) as current_image_file:
                    filename = str(current_listing.title.replace(' ', '')) + '_' + str(screenshot_entry_counter) + '_' + current_image.image_type.name + '.' + current_image.file_extension
                    copy_to_path = COPY_IMG_PATH + filename
                    screenshot_entry_dict[current_image_type] = {'filename': filename, 'security_marking': current_image.security_marking}
                    print('Copying {} to {}'.format(current_image_file.name, copy_to_path))
                    copy2(current_image_file.name, copy_to_path)

            screenshot_entry_counter = screenshot_entry_counter + 1
            screenshot_entry_list.append(screenshot_entry_dict)

        listing['screenshots'] = screenshot_entry_list
        image_types = ['small_icon', 'large_icon', 'banner_icon', 'large_banner_icon']

        for current_image_type in image_types:
            current_image = getattr(current_listing, current_image_type)

            current_image_path = str(current_image.id) + '_' + current_image.image_type.name + '.' + current_image.file_extension

            with media_storage.open(current_image_path) as current_image_file:
                filename = str(current_listing.title.replace(' ', '')) + '_' + current_image.image_type.name + '.' + current_image.file_extension
                listing[current_image_type] = {'filename': filename, "security_marking": current_image.security_marking}
                copy_to_path = COPY_IMG_PATH + filename
                print('Copying {} to {}'.format(current_image_file.name, copy_to_path))
                copy2(current_image_file.name, copy_to_path)
        # Reviews
        review_list = []
        for current_review in models.Review.objects.filter(listing=current_listing).order_by('edited_date').iterator():
            review_dict = {}
            review_dict['text'] = current_review.text
            review_dict['rate'] = current_review.rate
            review_dict['author'] = current_review.author.user.username
            review_list.append(review_dict)

        # library_entries
        library_entries_list = []
        for current_library_entry in models.ApplicationLibraryEntry.objects.filter(listing=current_listing).order_by('position').iterator():
            library_entry_dict = {}
            library_entry_dict['folder'] = current_library_entry.folder
            library_entry_dict['owner'] = current_library_entry.owner.user.username
            library_entry_dict['position'] = current_library_entry.position
            library_entries_list.append(library_entry_dict)

        # listing_activity
        listing_activity_list = []
        for listing_activity_entry in models.ListingActivity.objects.filter(listing=current_listing).order_by('activity_date').iterator():
            listing_activity_dict = {}
            listing_activity_dict['action'] = listing_activity_entry.action
            listing_activity_dict['author'] = listing_activity_entry.author.user.username
            listing_activity_dict['description'] = listing_activity_entry.description
            listing_activity_list.append(listing_activity_dict)

        # Combine Dictionaries into output_dict
        output_dict = {}
        output_dict['listing'] = listing
        output_dict['listing_review_batch'] = review_list
        output_dict['library_entries'] = library_entries_list
        output_dict['listing_activity'] = listing_activity_list
        output_list.append(output_dict)

    print('titles:{}'.format([record['listing']['title'] for record in output_list]))

    with open('listing.yaml', 'w') as file_stream:
        yaml.dump(output_list, file_stream, indent=2)
