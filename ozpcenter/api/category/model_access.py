"""
Category Model Access
"""
import logging

from django.db.models.functions import Lower

from ozpcenter import models

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


def get_all_categories():
    """
    Get all categories
    """
    return models.Category.objects.all().order_by(Lower('title'))


def get_category_by_title(title, reraise=False):
    """
    Get a category by title
    """
    try:
        return models.Category.objects.get(title=title)
    except models.Category.DoesNotExist as err:
        if reraise:
            raise err
        return None
