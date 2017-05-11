"""
Upload files into S3

https://github.com/jschneier/django-storages/blob/master/storages/backends/s3boto.py

To Upload to s3:

In S3 Website create a bucket called 'ozp-media'

in the settings.py file set.
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY

DEFAULT_MEDIA_FILE_STORAGE = ozp.storage.MediaS3Storage


Then run: python manage.py runscript upload_media
"""
import sys
import os

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../../')))

from django.conf import settings
from ozp.storage import media_storage
from ozp.storage import MediaS3Storage


def run():
    """
    Upload Data from File System Media Root to S3 Bucket
    """
    print('Starting to copy media files to remote location')

    if isinstance(media_storage, MediaS3Storage):
        local_media_storage_location = os.path.realpath(settings.MEDIA_ROOT)
        if os.path.exists(local_media_storage_location):
            # Get all file on the top-level of directory
            for filename in os.listdir(local_media_storage_location):
                filename_path = os.path.join(local_media_storage_location, filename)
                with open(filename_path, 'rb') as source_file:
                    if media_storage.exists(filename):
                        print('File already exist: {}'.format(filename))
                    else:
                        print('Copying File: {}'.format(filename))
                        media_storage.save(filename, source_file)

            print('Finished uploading media files')
        else:
            print('Local Media directory [{}] does not exist'.format(local_media_storage_location))
    else:
        print('The media storage must be MediaS3Storage')
