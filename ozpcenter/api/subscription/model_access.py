"""
Model access

PRs for Subscription Feature
https://github.com/aml-development/ozp-backend/pull/275

"""
import logging

from django.core.exceptions import MultipleObjectsReturned
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

    try:
        subscription, created = Subscription.objects.get_or_create(
            target_profile=profile,
            entity_type=entity_type,
            entity_id=entity_id
        )
        return subscription
    except MultipleObjectsReturned:
        subscription_ids = Subscription.objects.filter(target_profile=profile, entity_type=entity_type, entity_id=entity_id).values_list("id", flat=True)
        Subscription.objects.filter(pk__in=subscription_ids[1:]).delete()  # Delete all except first occurence

        subscription = Subscription.objects.get(
            target_profile=profile,
            entity_type=entity_type,
            entity_id=entity_id
        )
        return subscription


def update_subscription(request_username,
                        subscription_instance,
                        entity_type,
                        entity_id):
    """
    Update Subscription's entity

    Args:
        Subscription_instance (Subscription): Subscription_instance
        author_username (str): Username of author

    Return:
        Subscription: Updated Subscription
    """
    request_profile = generic_model_access.get_profile(request_username)  # TODO: Check if user exist, if not throw Exception Error ?
    # Why does 'request_profile is not subscription_instance.target_profile' not work???
    if request_profile.highest_role() not in ['APPS_MALL_STEWARD', 'ORG_STEWARD']:
        if request_profile.user.id is not subscription_instance.target_profile.user.id:
            raise Exception('Can not update a subscription that you do not own')

    subscription_ids = Subscription.objects.filter(target_profile=subscription_instance.target_profile,
                                                   entity_type=entity_type,
                                                   entity_id=entity_id).values_list("id", flat=True)
    # If subscription_ids >= 1 if means that there is already that subscription that exist
    if len(subscription_ids) >= 1:
        if subscription_instance.id in subscription_ids:
            return subscription_instance
        else:
            raise Exception('Can not update a subscription that already exist')

    subscription_instance.entity_type = entity_type
    subscription_instance.entity_id = entity_id
    subscription_instance.save()
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
                                id=subscription_instance.id).delete()
    return True
