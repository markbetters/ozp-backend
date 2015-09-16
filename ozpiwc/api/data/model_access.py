"""
Model access
"""
import logging

import ozpiwc.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

def set_data(username, key, value):
    data = models.data(username, key, value)
    data.save()
    return data

def get_data(username, key):
    return models.Data.objects.get(username=username, key=key)

def get_all_data(username):
    return models.Data.objects.filter(username=username)