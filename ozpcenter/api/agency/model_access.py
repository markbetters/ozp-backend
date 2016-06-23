"""
Agency Model Access
"""
import logging

from ozpcenter import models

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


def get_all_agencies():
    return models.Agency.objects.all()


def get_agency_by_title(title, reraise=False):
    try:
        return models.Agency.objects.get(title=title)
    except models.Agency.DoesNotExist as err:
        if reraise:
            raise err
        return None


def get_agency_by_id(id, reraise=False):
    try:
        return models.Agency.objects.get(id=id)
    except models.Agency.DoesNotExist as err:
        if reraise:
            raise err
        return None
