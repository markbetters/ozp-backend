"""
Script to migrate the existing data (in MySQL) into PostgreSQL

Prereqs:
* for each table in the old database, there is a corresponding file created
    via: mysqldump -u ozp -p ozp TABLENAME > TABLENAME.sql --complete-insert --hex-blob
* all images have been copied to a local directory

Usage:
    Assumes that the database referenced in settings.py is empty
"""
import datetime
import json
import os
import pytz
import re
import shutil
import sys
import uuid

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../')))

os.environ['DJANGO_SETTINGS_MODULE'] = 'ozp.settings'
import django
from django.conf import settings

from ozpcenter import models as models
from ozpcenter import model_access
from ozpcenter import utils

from ozpiwc import models as iwc_models

# path to the SQL dump files
SQL_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sql_dumps')
# path to the images
IMAGE_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')

DEFAULT_SECURITY_MARKING = "TOP SECRET"

def get_date_from_str(date_str):
    """
    Create a datetime object in UTC from a string

    Assumes the string was in format YYYY-MM-DD HH:MM:SS
    """
    if not date_str:
        return None
    d = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    return pytz.timezone('UTC').localize(d)

def get_index_next_unescaped_quote(str):
    """
    Get the index of the next unescaped single quote in a given string
    """
    for i, c in enumerate(str):
        if c == "'" and str[i-1] != "\\":
            return i

def get_columns(table):
    """
    Get the columns of a table in an array

    Columns will be in the same order as the values appear in the data
    """
    with open('%s/%s.sql' % (SQL_FILE_PATH, table), 'r') as f:
        data = f.read().replace('\n', '')
    # extract a string like (`id`, `version`, `created_by_id`)
    columns = utils.find_between(data, "INSERT INTO `%s`" % table, " VALUES")
    # remove parenthesis, backticks, and spaces
    columns = re.sub('[`() ]', '', columns)
    columns = columns.split(',')
    return columns

def get_values(table, column_count):
    """
    Get the values of a table in an array of arrays

    Args:
        table: name of the database table
        column_count: number of columns in this table
    """
    values = []
    with open('%s/%s.sql' % (SQL_FILE_PATH, table), 'r') as f:
        data = f.read().replace('\n', '')
    # extract the data we want
    values_str = utils.find_between(data, "VALUES ", ");") + ')'

    # values can contain special chars like paranthesis and commas, so we
    # have to be smart about how we extract the data

    while values_str:
        if values_str[0] != '(':
            print('Error: each value must start with opening paranthesis')
            return None
        # remove leading '('
        values_str = values_str[1:]
        # create empty array that will hold all values for this entry
        entry_values = []
        current_entry_finished = False
        columns_processed = 0
        while not current_entry_finished:
            # check for hex value (includes booleans)
            if values_str[:2] == '0x':
                val = re.findall(r'0x[0-9ABCDEF]*', values_str)[0]
                if val == '0x00':
                    entry_values.append(False)
                elif val == '0x01':
                    entry_values.append(True)
                else:
                    # assume the hex value is a UUID
                    entry_values.append(uuid.UUID(hex=val[2:]))
                # remove extracted data from the original string
                idx = len(val)
                values_str = values_str[idx:]
                columns_processed += 1
                # print('got hex value: %s' % val)
                # remove comma
                if values_str[0] != ',' and columns_processed != column_count:
                    print('Error: comma not found after extracting hex value')
                    return None
                if columns_processed < column_count:
                    values_str = values_str[1:]
            # check for a string value
            elif values_str[0] == "'":
                # read all chars between this quote and next unescaped quote
                # remove the leading quote
                values_str = values_str[1:]
                # find the index of the next unescaped quote
                idx = get_index_next_unescaped_quote(values_str)
                val = values_str[:idx]
                entry_values.append(val)
                # remove extracted data from original string
                idx = len(val) + 1 # +1 for the trailing quote
                values_str = values_str[idx:]
                columns_processed += 1
                # print('got string value: %s' % val)
                # remove comma
                if values_str[0] != ',' and columns_processed != column_count:
                    print('Error: comma not found after extracting string value. string[0]: %s' % values_str[0])
                    return None
                if columns_processed < column_count:
                    values_str = values_str[1:]
            # check for NULL value
            elif values_str[0:4] == 'NULL':
                val = None
                entry_values.append(val)
                values_str = values_str[4:]
                columns_processed += 1
                # print('got NULL value: %s' % val)
                # remove comma
                if values_str[0] != ',' and columns_processed != column_count:
                    print('Error: comma not found after extracting NULL value')
                    return None
                if columns_processed < column_count:
                    values_str = values_str[1:]
            # check for integer value
            elif values_str[0] in ['0','1','2','3','4','5','6','7','8','9']:
                val = re.findall(r'\d+', values_str)[0]
                entry_values.append(val)
                # remove extracted data from original string
                idx = len(val)
                values_str = values_str[idx:]
                columns_processed += 1
                # print('got integer value: %s' % val)
                # remove comma
                if values_str[0] != ',' and columns_processed != column_count:
                    print('Error: comma not found after extracting integer value')
                    return None
                if columns_processed < column_count:
                    values_str = values_str[1:]
            else:
                print('Error: found invalid character in data: %s' % values_str[0])
                return None

            if columns_processed == column_count:
                current_entry_finished = True
                # print('completed processing of row')
                # remove closing parenthesis
                if values_str[0] != ')':
                    print('Error: closing parenthesis not found at end of row data')
                    return None
                values_str = values_str[1:]
                # remove the comma between entries, unless this is the last entry
                if values_str:
                    values_str = values_str[1:]

        values.append(entry_values)
    return values

def run():
    print('running db_migration')
    # setup: http://stackoverflow.com/questions/25537905/django-1-7-throws-django-core-exceptions-appregistrynotready-models-arent-load
    django.setup()

    # first, create the default groups
     # Create Groups
    models.Profile.create_groups()
    # create default image types
    small_icon_type = models.ImageType(name='small_icon',
        max_size_bytes='4096')
    small_icon_type.save()
    large_icon_type = models.ImageType(name='large_icon',
        max_size_bytes='8192')
    large_icon_type.save()
    banner_icon_type = models.ImageType(name='banner_icon',
        max_size_bytes='2097152')
    banner_icon_type.save()
    large_banner_icon_type = models.ImageType(name='large_banner_icon',
        max_size_bytes='2097152')
    large_banner_icon_type.save()
    small_screenshot_type = models.ImageType(name='small_screenshot',
        max_size_bytes='1048576')
    small_screenshot_type.save()
    large_screenshot_type = models.ImageType(name='large_screenshot',
        max_size_bytes='1048576')
    large_screenshot_type.save()


    category_mapper = migrate_category()
    print('category_mapper: %s' % category_mapper)
    agency_mapper = migrate_agency()
    print('agency_mapper: %s' % agency_mapper)
    type_mapper = migrate_type()
    print('type_mapper: %s' % type_mapper)
    contact_type_mapper = migrate_contact_type()
    print('contact_type_mapper: %s' % contact_type_mapper)
    profile_mapper = migrate_profile()
    print('profile_mapper: %s' % profile_mapper)
    notification_mapper = migrate_notification(profile_mapper)
    print('notification_mapper: %s' % notification_mapper)
    migrate_profile_dismissed_notifications(profile_mapper, notification_mapper)
    listing_mapper = migrate_listing(category_mapper, agency_mapper, type_mapper,
        contact_type_mapper, profile_mapper)
    migrate_application_library_entry(profile_mapper, listing_mapper)
    migrate_doc_url(listing_mapper)
    migrate_item_comment(profile_mapper, listing_mapper)
    migrate_iwc_data_object(profile_mapper)
    migrate_listing_category(listing_mapper, category_mapper)
    migrate_listing_profile(profile_mapper, listing_mapper)
    migrate_listing_screenshot(listing_mapper)
    migrate_listing_tags(listing_mapper)
    migrate_contact(listing_mapper, contact_type_mapper)

def migrate_category():
    print('migrating categories...')
    columns = get_columns('category')
    # ['id', 'version', 'created_by_id', 'created_date', 'description', 'edited_by_id', 'edited_date', 'title']
    assert columns[0] == 'id'
    assert columns[1] == 'version'
    assert columns[2] == 'created_by_id'
    assert columns[3] == 'created_date'
    assert columns[4] == 'description'
    assert columns[5] == 'edited_by_id'
    assert columns[6] == 'edited_date'
    assert columns[7] == 'title'
    values = get_values('category', len(columns))
    # print('category columns: %s' % columns)
    print('number of category entries: %s' % len(values))
    # print('category values: %s' % values)
    # map old ids to new ones for future migrations: {'<old_id>': '<new_id>'}
    category_mapper = {}
    for i in values:
        old_id = i[0]
        description = i[4]
        title = i[7]
        print('adding category id %s, title: %s, description: %s' % (old_id, title, description))
        cat = models.Category(description=description, title=title)
        cat.save()
        category_mapper[i[0]] = str(cat.id)
    return category_mapper

def migrate_agency():
    print('migrating agencies...')
    columns = get_columns('agency')
    # ['id', 'version', 'created_by_id', 'created_date', 'edited_by_id', 'edited_date', 'icon_id', 'short_name', 'title']
    assert columns[0] == 'id'
    assert columns[1] == 'version'
    assert columns[2] == 'created_by_id'
    assert columns[3] == 'created_date'
    assert columns[4] == 'edited_by_id'
    assert columns[5] == 'edited_date'
    assert columns[6] == 'icon_id'
    assert columns[7] == 'short_name'
    assert columns[8] == 'title'
    values = get_values('agency', len(columns))
    # print('category columns: %s' % columns)
    print('number of agencies entries: %s' % len(values))
    # print('agency values: %s' % values)
    # map old ids to new ones for future migrations: {'<old_id>': '<new_id>'}
    agency_mapper = {}
    for i in values:
        old_id = i[0]
        short_name = i[7]
        title = i[8]
        print('adding agency id %s, title: %s, short_name: %s' % (old_id, title, short_name))
        a = models.Agency(short_name=short_name, title=title)
        a.save()
        agency_mapper[i[0]] = str(a.id)
    return agency_mapper

def migrate_type():
    print('migrating type...')
    columns = get_columns('type')
    # ['id', 'version', 'created_by_id', 'created_date', 'description', 'edited_by_id', 'edited_date', 'title']
    assert columns[0] == 'id'
    assert columns[1] == 'version'
    assert columns[2] == 'created_by_id'
    assert columns[3] == 'created_date'
    assert columns[4] == 'description'
    assert columns[5] == 'edited_by_id'
    assert columns[6] == 'edited_date'
    assert columns[7] == 'title'
    values = get_values('type', len(columns))
    # print('category columns: %s' % columns)
    print('number of type entries: %s' % len(values))
    # print('agency values: %s' % values)
    # map old ids to new ones for future migrations: {'<old_id>': '<new_id>'}
    type_mapper = {}
    for i in values:
        old_id = i[0]
        description = i[4]
        title = i[7]
        print('adding type id %s, title: %s, description: %s' % (old_id, title, description))
        t = models.ListingType(title=title, description=description)
        t.save()
        type_mapper[i[0]] = str(t.id)
    return type_mapper

def migrate_contact_type():
    print('migrating contact_type...')
    columns = get_columns('contact_type')
    # ['id', 'version', 'created_by_id', 'created_date', 'edited_by_id', 'edited_date', 'required', 'title']
    assert columns[0] == 'id'
    assert columns[1] == 'version'
    assert columns[2] == 'created_by_id'
    assert columns[3] == 'created_date'
    assert columns[4] == 'edited_by_id'
    assert columns[5] == 'edited_date'
    assert columns[6] == 'required'
    assert columns[7] == 'title'
    values = get_values('contact_type', len(columns))
    # print('category columns: %s' % columns)
    print('number of type entries: %s' % len(values))
    # print('agency values: %s' % values)
    # map old ids to new ones for future migrations: {'<old_id>': '<new_id>'}
    contact_type_mapper = {}
    for i in values:
        old_id = i[0]
        required = i[6]
        title = i[7]
        print('adding contact_type id %s, title: %s, required: %s' % (old_id, title, required))
        ct = models.ContactType(name=title, required=required)
        ct.save()
        contact_type_mapper[i[0]] = str(ct.id)
    return contact_type_mapper

def migrate_profile():
    print('migrating profile...')
    columns = get_columns('profile')
    # ['id', 'version', 'bio', 'created_by_id', 'created_date', 'display_name', 'edited_by_id', 'edited_date', 'email', 'highest_role', 'last_login', 'username', 'launch_in_webtop']
    assert columns[0] == 'id'
    assert columns[1] == 'version'
    assert columns[2] == 'bio'
    assert columns[3] == 'created_by_id'
    assert columns[4] == 'created_date'
    assert columns[5] == 'display_name'
    assert columns[6] == 'edited_by_id'
    assert columns[7] == 'edited_date'
    assert columns[8] == 'email'
    assert columns[9] == 'highest_role'
    assert columns[10] == 'last_login'
    assert columns[11] == 'username'
    assert columns[12] == 'launch_in_webtop'
    values = get_values('profile', len(columns))
    # print('category columns: %s' % columns)
    print('number of type entries: %s' % len(values))
    # print('agency values: %s' % values)
    # map old ids to new ones for future migrations: {'<old_id>': '<new_id>'}
    profile_mapper = {}
    for i in values:
        old_id = i[0]
        bio = i[2]
        display_name = i[5]
        email = i[8]
        highest_role = i[9]
        last_login = i[10]
        username = i[11]
        print('adding profile id %s, username: %s' % (old_id, username))
        if not display_name:
            display_name = username
        kwargs = {
            'bio': bio,
            'display_name': display_name,
            'email': email,
            'dn': username
        }
        # TODO: how to extract CN from DN?
        cn = username
        # sanitize username
        username = cn[0:30] # limit to 30 chars
        username = username.replace(' ', '_') # no spaces
        username = username.replace("'", "") # no apostrophes
        username = username.lower() # all lowercase

        # don't bother updating groups, organizations, permissions - this will
        # be done automatically the first time authorization is checked
        p = models.Profile.create_user(username, **kwargs)

        profile_mapper[i[0]] = str(p.id)
    return profile_mapper

def migrate_notification(profile_mapper):
    print('migrating notification...')
    columns = get_columns('notification')
    # ['id', 'version', 'created_by_id', 'created_date', 'edited_by_id', 'edited_date', 'message', 'expires_date']
    assert columns[0] == 'id'
    assert columns[1] == 'version'
    assert columns[2] == 'created_by_id'
    assert columns[3] == 'created_date'
    assert columns[4] == 'edited_by_id'
    assert columns[5] == 'edited_date'
    assert columns[6] == 'message'
    assert columns[7] == 'expires_date'
    values = get_values('notification', len(columns))
    # print('category columns: %s' % columns)
    print('number of type entries: %s' % len(values))
    # print('agency values: %s' % values)
    # map old ids to new ones for future migrations: {'<old_id>': '<new_id>'}
    notification_mapper = {}
    for i in values:
        old_id = i[0]
        message = i[6]
        expires_date = get_date_from_str(i[7])
        created_date = get_date_from_str(i[3])
        created_by_id = i[2]
        print('adding notification id %s, message: %s, expires_date: %s' % (old_id, message, expires_date))
        p = models.Profile.objects.get(id=profile_mapper[created_by_id])
        n = models.Notification(message=message, expires_date=expires_date, created_date=created_date, author=p)
        n.save()
        notification_mapper[i[0]] = str(n.id)
    return notification_mapper

def migrate_profile_dismissed_notifications(profile_mapper, notification_mapper):
    print('migrating migrate_profile_dismissed_notifications...')
    columns = get_columns('profile_dismissed_notifications')
    # ['notification_id', 'profile_id']
    assert columns[0] == 'notification_id'
    assert columns[1] == 'profile_id'
    values = get_values('profile_dismissed_notifications', len(columns))
    print('number of profile_dismissed_notifications entries: %s' % len(values))
    for i in values:
        notification_id = i[0]
        profile_id = i[1]
        notification = models.Notification.objects.get(id=notification_mapper[notification_id])
        profile = models.Profile.objects.get(id=profile_mapper[profile_id])
        notification.dismissed_by.add(profile)

def migrate_image(image_uuid, image_type):
    """
    Migrate an image

    A image_mapper is not needed, as the old uuid will be the new uuid
    """
    # determine the image's extension
    VALID_IMAGE_TYPES = ['png', 'jpg', 'jpeg', 'gif']
    file_extension = None
    for i in VALID_IMAGE_TYPES:
        filename = IMAGE_FILE_PATH + '/%s.%s' % (image_uuid, i)
        if os.path.isfile(filename):
            file_extension = i
            break
    if not file_extension:
        print('Error: no file extension found for image %s' % image_uuid)
        return

    # set default security marking
    image_type = models.ImageType.objects.get(name=image_type)
    img = models.Image(uuid=image_uuid, security_marking=DEFAULT_SECURITY_MARKING,
            file_extension=file_extension, image_type=image_type)
    img.save()

    src = filename
    dest = settings.MEDIA_ROOT + str(img.id) + '_' + img.image_type.name + '.' + file_extension
    shutil.copy(src, dest)
    return img

def migrate_listing(category_mapper, agency_mapper, type_mapper,
        contact_type_mapper, profile_mapper):
    print('migrating listings')
    columns = get_columns('listing')
    print('listing columns: %s' % columns)
    # ['id', 'version', 'agency_id', 'approval_status', 'approved_date', 'avg_rate',
    #   'created_by_id', 'created_date', 'description', 'description_short',
    #   'edited_by_id', 'edited_date', 'small_icon_id', 'large_icon_id',
    #   'banner_icon_id', 'featured_banner_icon_id', 'is_enabled', 'is_featured',
    #   'last_activity_id', 'launch_url', 'requirements', 'title', 'total_comments',
    #   'total_rate1', 'total_rate2', 'total_rate3', 'total_rate4', 'total_rate5',
    #   'total_votes', 'type_id', 'uuid', 'version_name', 'what_is_new',
    #   'width', 'singleton', 'height']
    assert columns[0] == 'id'
    assert columns[1] == 'version'
    assert columns[2] == 'agency_id'
    assert columns[3] == 'approval_status'
    assert columns[4] == 'approved_date'
    assert columns[5] == 'avg_rate'
    assert columns[6] == 'created_by_id'
    assert columns[7] == 'created_date'
    assert columns[8] == 'description'
    assert columns[9] == 'description_short'
    assert columns[10] == 'edited_by_id'
    assert columns[11] == 'edited_date'
    assert columns[12] == 'small_icon_id'
    assert columns[13] == 'large_icon_id'
    assert columns[14] == 'banner_icon_id'
    assert columns[15] == 'featured_banner_icon_id'
    assert columns[16] == 'is_enabled'
    assert columns[17] == 'is_featured'
    assert columns[18] == 'last_activity_id'
    assert columns[19] == 'launch_url'
    assert columns[20] == 'requirements'
    assert columns[21] == 'title'
    assert columns[22] == 'total_comments'
    assert columns[23] == 'total_rate1'
    assert columns[24] == 'total_rate2'
    assert columns[25] == 'total_rate3'
    assert columns[26] == 'total_rate4'
    assert columns[27] == 'total_rate5'
    assert columns[28] == 'total_votes'
    assert columns[29] == 'type_id'
    assert columns[30] == 'uuid'
    assert columns[31] == 'version_name'
    assert columns[32] == 'what_is_new'
    assert columns[33] == 'width'
    assert columns[34] == 'singleton'
    assert columns[35] == 'height'
    values = get_values('listing', len(columns))
    print('listing values: %s' % values)

    # map old ids to new ones for future migrations: {'<old_id>': '<new_id>'}
    listing_mapper = {}
    for i in values:
        try:
            old_id = i[0]
            agency = models.Agency.objects.get(id=agency_mapper[i[2]])
            title = i[21]
            # approval_status should be a 1-1 mapping
            approval_status = i[3]
            approved_date = get_date_from_str(i[4])
            avg_rate = i[5]
            created_by_id = i[6]
            created_date = get_date_from_str(i[7])
            description = i[8]
            description_short = i[9]
            edited_by_id = i[10]
            edited_date = get_date_from_str(i[11])
            small_icon_id = i[12]
            small_icon = migrate_image(small_icon_id, 'small_icon')
            large_icon_id = i[13]
            large_icon = migrate_image(large_icon_id, 'large_icon')
            banner_icon_id = i[14]
            banner_icon = migrate_image(banner_icon_id, 'banner_icon')
            featured_banner_icon_id = i[15]
            large_banner_icon = migrate_image(featured_banner_icon_id, 'large_banner_icon')
            is_enabled = i[16]
            is_featured = i[17]
            last_activity_id = i[18]
            launch_url = i[19]
            requirements = i[20]
            total_comments = i[22]
            total_rate1 = i[23]
            total_rate2 = i[24]
            total_rate3 = i[25]
            total_rate4 = i[26]
            total_rate5 = i[27]
            total_votes = i[28]
            listing_type = models.ListingType(id=type_mapper[i[29]])
            uuid = i[30]
            version_name = i[31]
            what_is_new = i[32]
            iframe_compatible = not i[34]

            print('adding listing id %s, title: %s' % (old_id, title))
            # TODO: unique_name?
            listing = models.Listing(title=title, agency=agency,
                approval_status=approval_status, approved_date=approved_date,
                edited_date=edited_date, description=description,
                description_short=description_short, is_enabled=is_enabled,
                is_featured=is_featured, launch_url=launch_url,
                listing_type=listing_type, version_name=version_name,
                what_is_new=what_is_new, iframe_compatible=iframe_compatible,
                requirements=requirements, small_icon=small_icon,
                large_icon=large_icon, banner_icon=banner_icon,
                large_banner_icon=large_banner_icon, avg_rate=avg_rate,
                total_votes=total_votes, total_rate5=total_rate5,
                total_rate4=total_rate4, total_rate3=total_rate3,
                total_rate2=total_rate2, total_rate1=total_rate1,
                total_reviews=total_comments, security_marking=DEFAULT_SECURITY_MARKING)
            listing.save()
            listing_mapper[old_id] = str(listing.id)

            # TODO:
            # current_rejection
            # last_activity
        except Exception as e:
            print('Error processing listing %s: %s' % (title, str(e)))

    return listing_mapper

def migrate_application_library_entry(profile_mapper, listing_mapper):
    print('migrating application_library_entry...')
    columns = get_columns('application_library_entry')
    # ['id', 'version', 'created_by_id', 'created_date', 'edited_by_id', 'edited_date', 'folder', 'listing_id', 'owner_id', 'application_library_idx']
    assert columns[0] == 'id'
    assert columns[1] == 'version'
    assert columns[2] == 'created_by_id'
    assert columns[3] == 'created_date'
    assert columns[4] == 'edited_by_id'
    assert columns[5] == 'edited_date'
    assert columns[6] == 'folder'
    assert columns[7] == 'listing_id'
    assert columns[8] == 'owner_id'
    values = get_values('application_library_entry', len(columns))
    # print('category columns: %s' % columns)
    print('number of application_library_entry entries: %s' % len(values))
    for i in values:
        try:
            old_id = i[0]
            folder = i[6]
            listing_id = i[7]
            listing = models.Listing.objects.get(id=listing_mapper[listing_id])
            owner = models.Profile.objects.get(id=profile_mapper[i[8]])
            print('adding application_library_entry for listing %s, owner %s' % (listing.title, owner.user.username))
            entry = models.ApplicationLibraryEntry(folder=folder, listing=listing, owner=owner)
            entry.save()
        except Exception as e:
            print('Error adding library entry: %s, values: %s' % (str(e), i))

def migrate_doc_url(listing_mapper):
    print('migrating doc_url...')
    columns = get_columns('doc_url')
    # ['id', 'version', 'listing_id', 'name', 'url']
    assert columns[0] == 'id'
    assert columns[1] == 'version'
    assert columns[2] == 'listing_id'
    assert columns[3] == 'name'
    assert columns[4] == 'url'
    values = get_values('doc_url', len(columns))
    # print('category columns: %s' % columns)
    print('number of doc_url entries: %s' % len(values))
    for i in values:
        try:
            old_id = i[0]
            listing_id = i[2]
            name = i[3]
            url = i[4]
            listing = models.Listing.objects.get(id=listing_mapper[listing_id])
            print('adding doc_url for listing %s, name %s' % (listing.title, name))
            doc_url = models.DocUrl(name=name, url=url, listing=listing)
            doc_url.save()
        except Exception as e:
            print('Error adding doc_url entry: %s, values: %s' % (str(e), i))

def migrate_item_comment(profile_mapper, listing_mapper):
    print('migrating item_comment...')
    columns = get_columns('item_comment')
    # ['id', 'version', 'listing_id', 'name', 'url']
    assert columns[0] == 'id'
    assert columns[1] == 'version'
    assert columns[2] == 'author_id'
    assert columns[3] == 'created_by_id'
    assert columns[4] == 'created_date'
    assert columns[5] == 'edited_by_id'
    assert columns[6] == 'edited_date'
    assert columns[7] == 'listing_id'
    assert columns[8] == 'rate'
    assert columns[9] == 'text'
    values = get_values('item_comment', len(columns))
    # print('category columns: %s' % columns)
    print('number of item_comment entries: %s' % len(values))
    for i in values:
        try:
            old_id = i[0]
            listing = models.Listing.objects.get(id=listing_mapper[i[7]])
            author = models.Profile.objects.get(id=profile_mapper[i[2]])
            edited_date = get_date_from_str(i[6])
            rate = i[8]
            text = i[9]
            review = models.Review(text=text, rate=rate,
                edited_date=edited_date, author=author, listing=listing)
            print('adding review for listing %s, rate: %s, text: %s' % (listing.title, rate, text))
            review.save()
        except Exception as e:
            print('Error adding review entry: %s, values: %s' % (str(e), i))

def migrate_iwc_data_object(profile_mapper):
    print('migrating iwc_data_object...')
    columns = get_columns('iwc_data_object')
    # ['id', 'version', 'content_type', 'entity', 'key', 'profile_id']
    assert columns[0] == 'id'
    assert columns[1] == 'version'
    assert columns[2] == 'content_type'
    assert columns[3] == 'entity'
    assert columns[4] == 'key'
    assert columns[5] == 'profile_id'
    values = get_values('iwc_data_object', len(columns))
    # print('category columns: %s' % columns)
    print('number of iwc_data_object entries: %s' % len(values))
    for i in values:
        try:
            old_id = i[0]
            profile = models.Profile.objects.get(id=profile_mapper[i[5]])
            key = i[4]
            content_type = i[2]
            entity = i[3]
            # TODO: any modification here to match new api?
            data = iwc_models.DataResource(key=key, entity=entity,
                content_type=content_type, username=profile.user.username)
            print('adding iwc DataObject for user %s, key: %s, content_type: %s' % (
                profile.user.username, key, content_type))
            data.save()
        except Exception as e:
            print('Error adding iwc DataObject entry: %s, values: %s' % (str(e), i))

def migrate_listing_category(listing_mapper, category_mapper):
    print('migrating listing_category...')
    columns = get_columns('listing_category')
    # ['listing_categories_id', 'category_id']
    assert columns[0] == 'listing_categories_id'
    assert columns[1] == 'category_id'
    values = get_values('listing_category', len(columns))
    # print('category columns: %s' % columns)
    print('number of listing_category entries: %s' % len(values))
    for i in values:
        try:
            listing_id = i[0]
            category_id = i[1]
            listing = models.Listing.objects.get(id=listing_mapper[listing_id])
            category = models.Category.objects.get(id=category_mapper[category_id])
            print('adding category for listing %s, name %s' % (listing.title, category.title))
            listing.categories.add(category)
        except Exception as e:
            print('Error adding category %s to listing: %s, values: %s' % (category.title, listing.title, i))

def migrate_listing_profile(profile_mapper, listing_mapper):
    # owners
    print('migrating listing_profile...')
    columns = get_columns('listing_profile')
    # ['listing_owners_id', 'profile_id']
    assert columns[0] == 'listing_owners_id'
    assert columns[1] == 'profile_id'
    values = get_values('listing_profile', len(columns))
    # print('category columns: %s' % columns)
    print('number of listing_profile entries: %s' % len(values))
    for i in values:
        try:
            listing_id = i[0]
            profile_id = i[1]
            listing = models.Listing.objects.get(id=listing_mapper[listing_id])
            profile = models.Profile.objects.get(id=profile_mapper[profile_id])
            print('adding owner for listing %s, username %s' % (listing.title, profile.user.username))
            listing.owners.add(profile)
        except Exception as e:
            print('Error adding owner %s to listing: %s, values: %s' % (profile.user.username, listing.title, i))

def migrate_listing_screenshot(listing_mapper):
    print('migrating screenshot...')
    columns = get_columns('screenshot')
    # ['id', 'version', 'listing_id', 'name', 'url']
    assert columns[0] == 'id'
    assert columns[1] == 'version'
    assert columns[2] == 'created_by_id'
    assert columns[3] == 'created_date'
    assert columns[4] == 'edited_by_id'
    assert columns[5] == 'edited_date'
    assert columns[6] == 'large_image_id'
    assert columns[7] == 'service_item_id'
    assert columns[8] == 'small_image_id'
    assert columns[9] == 'ordinal'
    values = get_values('screenshot', len(columns))
    # print('category columns: %s' % columns)
    print('number of screenshot entries: %s' % len(values))
    for i in values:
        try:
            old_id = i[0]
            large_image_id= i[6]
            small_image_id= i[8]
            listing_id = i[7]
            listing = models.Listing.objects.get(id=listing_mapper[listing_id])
            small_image = migrate_image(small_image_id, 'small_screenshot')
            large_image = migrate_image(large_image_id, 'large_screenshot')
            print('adding screenshot for listing %s, large_image_id %s' % (listing.title, large_image_id))
            screenshot = models.Screenshot(small_image=small_image, large_image=large_image, listing=listing)
            screenshot.save()
        except Exception as e:
            print('Error adding screenshot entry: %s, values: %s' % (str(e), i))

def migrate_listing_tags(listing_mapper):
    print('migrating listing_tags...')
    columns = get_columns('listing_tags')
    # ['listing_id', 'tags_string']
    assert columns[0] == 'listing_id'
    assert columns[1] == 'tags_string'
    values = get_values('listing_tags', len(columns))
    # print('category columns: %s' % columns)
    print('number of listing_tags entries: %s' % len(values))
    for i in values:
        try:
            listing_id = i[0]
            name = i[1]
            listing = models.Listing.objects.get(id=listing_mapper[listing_id])
            try:
                tag = models.Tag(name=name)
                tag.save()
            except Exception:
                tag = models.Tag.objects.get(name=name)
            print('adding tag for listing %s, name %s' % (listing.title, tag))
            listing.tags.add(tag)

        except Exception as e:
            print('Error adding tag entry: %s, values: %s' % (str(e), i))

def migrate_contact(listing_mapper, contact_type_mapper):
    print('migrating contact...')
    columns = get_columns('contact')
    # ['id', 'version', 'created_by_id', 'created_date', 'edited_by_id', 'edited_date', 'email',
    #   'listing_id', 'name', 'organization', 'secure_phone', 'type_id', 'unsecure_phone']
    assert columns[0] == 'id'
    assert columns[1] == 'version'
    assert columns[2] == 'created_by_id'
    assert columns[3] == 'created_date'
    assert columns[4] == 'edited_by_id'
    assert columns[5] == 'edited_date'
    assert columns[6] == 'email'
    assert columns[7] == 'listing_id'
    assert columns[8] == 'name'
    assert columns[9] == 'organization'
    assert columns[10] == 'secure_phone'
    assert columns[11] == 'type_id'
    assert columns[12] == 'unsecure_phone'

    values = get_values('contact', len(columns))
    # print('category columns: %s' % columns)
    print('number of contact entries: %s' % len(values))
    for i in values:
        try:
            email = i[6]
            listing_id = i[7]
            name = i[8]
            organization = i[9]
            secure_phone = i[10]
            type_id = i[11]
            contact_type = models.ContactType.objects.get(id=contact_type_mapper[type_id])
            unsecure_phone = i[12]
            listing = models.Listing.objects.get(id=listing_mapper[listing_id])
            try:
                contact = models.Contact(name=name, email=email, secure_phone=secure_phone,
                    unsecure_phone=unsecure_phone, contact_type=contact_type)
                contact.save()
            except Exception:
                print('Error: Found duplicate contact entry: %s' % name)
                contact = models.Tag.objects.get(name=name)
            print('adding contact %s for listing %s' % (name, listing.title))
            listing.contacts.add(contact)

        except Exception as e:
            print('Error adding contact entry: %s, values: %s' % (str(e), i))

def migrate_listing_activities(profile_mapper, listing_mapper):
    # includes change_details, rejection_listing, rejection_activity
    pass



if __name__ == "__main__":
    run()
