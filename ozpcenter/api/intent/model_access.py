"""
Intent Model Access
"""
import logging

from ozpcenter import models

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


def get_all_intents():
    """
    Get all intents

    Return:
        [Intent]: List of All Intent Entry Objects
    """
    return models.Intent.objects.all()


def get_intent_by_action(action, reraise=False):
    """
    Get intent by action

    Return:
        Intent: Intent Entry Object for action ?more than one
    """
    try:
        return models.Intent.objects.get(action=action)
    except models.Intent.DoesNotExist as err:
        if reraise:
            raise err
        return None


def get_intent_by_id(id, reraise=False):
    """
    Get intent by id

    Return:
        Intent: Intent Entry Object for id
    """
    try:
        return models.Intent.objects.get(id=id)
    except models.Intent.DoesNotExist as err:
        if reraise:
            raise err
        return None
