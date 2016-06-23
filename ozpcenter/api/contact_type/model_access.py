"""
Contact Types Model Access
"""
import logging

from ozpcenter import models

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


def get_all_contact_types():
    return models.ContactType.objects.all()


def get_contact_type_by_name(name, reraise=True):
    try:
        return models.ContactType.objects.get(name=name)
    except models.ContactType.DoesNotExist as err:
        if reraise:
            raise err
        return None
