"""
Model Access
"""
import logging

import ozpcenter.models as models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

def get_all_intents():
    return models.Intent.objects.all()

def get_intent_by_action(action):
    try:
        return models.Intent.objects.get(action=action)
    except models.Intent.DoesNotExist:
        return None

def get_intent_by_id(id):
    try:
        return models.Intent.objects.get(id=id)
    except models.Intent.DoesNotExist:
        return None