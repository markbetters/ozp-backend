"""
Model Access
"""
import logging

import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')


def get_all_agencies():
    return models.Agency.objects.all()


def get_agency_by_title(title):
    try:
        return models.Agency.objects.get(title=title)
    except models.Agency.DoesNotExist:
        return None
