"""
Model access
"""
import logging

# from django.db.models import Q
# from ozpcenter import errors
from ozpcenter.models import Subscription

import ozpcenter.model_access as generic_model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


def get_self(username):
    """
    Get Profile for username

    Args:
        username (str): current username

    Returns:
        Profile if username exist, None if username does not exist
    """
    return generic_model_access.get_profile(username)


def get_all_subscriptions():
    """
    Get all subscriptions

    Includes
    * Category subscriptions
    * Tag subscriptions

    Returns:
        django.db.models.query.QuerySet(Subscription): List of all subscriptions
    """
    return Subscription.objects.all()


def get_self_subscriptions(username):
    """
    Get subscriptions for current user

    Args:
        username (str): current username to get subscriptions

    Returns:
        django.db.models.query.QuerySet(Subscription): List of subscriptions for username
    """
    subscriptions = Subscription.objects.filter(target_profile=get_self(username))
    return subscriptions


def create_subscription(author_username, entity_type=None, entity_id=None):
    """
    Create Subscription

    Subscriptions Types:
        * Category Subscription is made up of [author_username, category]
        * Tag Subscription is made up of [author_username, tag]

    Args:
        author_username (str): Username of author
        entity_obj (models.Category/models.Tag)-Optional: Listing

    Return:
        Subscription: Created Subscription

    Raises:
        AssertionError: If author_username is None
    """
    assert (author_username is not None), 'Author Username is necessary'
    # entity_type = str(entity_obj.__class__.__name__).lower()
    # entity_id = entity_obj.id
    assert (entity_type is not None and entity_id is not None), 'Subscription can not have entity_type or entity_id'

    profile = generic_model_access.get_profile(author_username)

    subscription = Subscription(
        target_profile=profile,
        entity_type=entity_type,
        entity_id=entity_id
    )

    subscription.save()

    return subscription


def update_subscription(author_username, subscription_instance):
    """
    Update Subscription

    Args:
        Subscription_instance (Subscription): Subscription_instance
        author_username (str): Username of author

    Return:
        Subscription: Updated Subscription
    """
    # user = generic_model_access.get_profile(author_username)  # TODO: Check if user exist, if not throw Exception Error ?
    subscription_instance.save()
    # TODO Update
    return subscription_instance


def delete_self_subscription(subscription_instance, username):
    """
    Delete a Subscription (unsubscribe)

    Args:
        subscription_instance (Subscription): subscription_instance
        username (string)

    Return:
        bool: Subscription Deleted
    """
    profile_instance = get_self(username)
    Subscription.objects.filter(target_profile=profile_instance,
                                id=subscription_instance).delete()
    return True
