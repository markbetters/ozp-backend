"""
storage

from io import StringIO; from ozp.storage import MediaFilesStorage; MediaFilesStorage().save('file.txt',StringIO('dkkdkd'))

http://stackoverflow.com/questions/29383373/creating-signed-cookies-for-amazon-cloudfront

Steps for Minio:

# Make Local Dev
make dev

wget https://dl.minio.io/server/minio/release/linux-amd64/minio
chmod +x minio
./minio server media

# Login into minio and create bucket called ozp-media

export AWS_ACCESS_KEY_ID=2Q87EJPVQ0739BYNXMGH;export AWS_SECRET_ACCESS_KEY=UmjiZ8qnNqGSexo49yVcJmzaJ1x835/na0TcIFFa;export DEFAULT_MEDIA_FILE_STORAGE=ozp.storage.MediaS3Storage

Under MediaS3Storage in ozp/storage.py uncomment endpoint_url
    python manage.py runscript upload_media
    make run
"""
import os

from django.utils.module_loading import import_string
from django.conf import settings
# from django.contrib.staticfiles.utils import check_settings
from django.core.files.storage import FileSystemStorage

from storages.backends.s3boto3 import S3Boto3Storage


def get_media_storage_class(import_path=None):
    return import_string(import_path or settings.DEFAULT_MEDIA_FILE_STORAGE)


class MediaFileStorage(FileSystemStorage):
    """
    Standard file system storage for static files.
    The defaults for ``location`` and ``base_url`` are
    ``MEDIA_ROOT`` and ``MEDIA_URL``.
    """

    def __init__(self, location=None, base_url=None, *args, **kwargs):
        if location is None:
            location = settings.MEDIA_ROOT
        if base_url is None:
            base_url = settings.MEDIA_URL
        # check_settings(base_url)
        super().__init__(location, base_url, *args, **kwargs)
        # FileSystemStorage fallbacks to MEDIA_ROOT when location
        # is empty, so we restore the empty value.
        if not location:
            self.base_location = None
            self.location = None

    def get_available_name(self, name):
        """Returns a filename that's free on the target storage system, and
        available for new content to be written to.

        Found at http://djangosnippets.org/snippets/976/

        This file storage solves overwrite on upload problem. Another
        proposed solution was to override the save method on the model
        like so (from https://code.djangoproject.com/ticket/11663):

        def save(self, *args, **kwargs):
            try:
                this = MyModelName.objects.get(id=self.id)
                if this.MyImageFieldName != self.MyImageFieldName:
                    this.MyImageFieldName.delete()
            except: pass
            super(MyModelName, self).save(*args, **kwargs)
        """
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return os.path.join(settings.MEDIA_ROOT, name)

    def path(self, name):
        if not self.location:
            raise RuntimeError("You're using the staticfiles app "
                               "without having set the MEDIA_ROOT "
                               "setting to a filesystem path.")
        return super().path(name)


class MediaS3Storage(S3Boto3Storage):
    """
    https://github.com/jschneier/django-storages/blob/master/storages/backends/s3boto3.py
    """
    # location = settings.MEDIA_ROOT
    custom_domain = settings.AWS_MEDIA_S3_CUSTOM_DOMAIN
    bucket_name = settings.AWS_MEDIA_STORAGE_BUCKET_NAME
    default_acl = settings.AWS_MEDIA_DEFAULT_ACL
    # Use endpoint_url for testing with minio
    # endpoint_url = 'http://127.0.0.1:9000'


media_storage = get_media_storage_class()()
