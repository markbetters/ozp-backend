"""
Model Access
"""
import logging

import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

def get_all_access_controls():
    return models.AccessControl.objects.all()

def get_access_control_by_title(title):
    try:
        return models.AccessControl.objects.get(title=title)
    except models.AccessControl.DoesNotExist:
        return None