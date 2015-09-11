"""
Image model access
"""
import logging
import os.path

from django.conf import settings

import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

def get_all_images(username):
    # image objects (metadata), not actual images
    return models.Image.objects.for_user(username).all()

def get_all_image_types():
    return models.ImageType.objects.all()

def get_image_path(pk):
    """
    Return absolute file path to an image given its id (pk)
    """
    image = models.Image.objects.get(id=pk)
    image_path = settings.MEDIA_ROOT + '/' + image.id + '_' + image.image_type.name + '.' + image.file_extension
    if os.path.isfile(image_path):
        return image_path
    else:
        logger.error('image for pk %d does not exist' % pk)
        # TODO: raise exception
        return '/does/not/exist'

def get_image_by_id(id):
    # Since this is effectively only metadata about the image and not the image
    # itself, access control is not enforced here. That is done when the image
    # itself is served
    try:
        return models.Image.objects.get(id=id)
    except models.Image.DoesNotExist:
        return None