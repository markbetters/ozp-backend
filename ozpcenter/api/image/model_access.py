"""
Image Model Access
"""
import logging

from ozpcenter import models

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


def get_all_images(username):
    """
    Get all the images a user has access to
    """
    # image objects (metadata), not actual images
    return models.Image.objects.for_user(username).all()


def get_all_image_types():
    """
    Get all the image types
    """
    return models.ImageType.objects.all()


def get_image_by_id(id):
    """
    Get an image by id

    Since this is effectively only metadata about the image and not the image
    itself, access control is not enforced here. That is done when the image
    itself is served
    """
    try:
        return models.Image.objects.get(id=id)
    except models.Image.DoesNotExist:
        return None
