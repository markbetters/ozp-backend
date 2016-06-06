"""
Model access
"""
import logging

import ozpiwc.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


def get_data_resource(username, key):
    return models.DataResource.objects.filter(
        key=key, username=username).first()


def get_all_keys(username):
    return models.DataResource.objects.filter(username=username).values_list(
        'key', flat=True)
