"""
Model Access
"""
import logging

import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center.'+str(__name__))


def get_all_contact_types():
    return models.ContactType.objects.all()


def get_contact_type_by_name(name):
    try:
        return models.ContactType.objects.get(name=name)
    except models.ContactType.DoesNotExist:
        return None
