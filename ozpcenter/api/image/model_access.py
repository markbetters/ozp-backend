"""
Image model access
"""
import logging
import os.path

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

import ozpcenter.models as models
import ozpcenter.utils as utils

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

def get_all_images(username):
    """
    Get all models.Image objects for user

    key = images:<username>
    """
    key = 'images:%s' % username
    data = cache.get(key)
    if data is None:
        try:
            data = models.Image.objects.for_user(username).all()
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data

def get_all_image_types():
    """
    Returns all models.ImageType objects

    key: image_types
    """
    key = 'image_types'
    data = cache.get(key)
    if data is None:
        try:
            data = models.ImageType.objects.all()
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data

def get_image_path(pk):
    """
    Return absolute file path to an image given its id (pk)
    """
    image = models.Image.objects.get(id=pk)
    image_path = settings.MEDIA_ROOT + '/' + image.uuid + '.' + image.file_extension
    if os.path.isfile(image_path):
        return image_path
    else:
        logger.error('image for pk %d does not exist' % pk)
        # TODO: raise exception
        return '/does/not/exist'