"""
Model access
"""
import logging

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

import ozpcenter.models as models
import ozpcenter.errors as errors
import ozpcenter.utils as utils
import ozpcenter.model_access as generic_model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

def filter_listings(username, filter_params):
    """
    Filter Listings

    Respects private apps (only from user's agency) and user's
    max_classification_level

    filter_params can contain:
        * list of category names (OR logic)
        * list of agencies (OR logic)
        * list of listing types (OR logic)

    Too many variations to cache
    """
    objects = models.Listing.objects.for_user(username).all()
    if 'categories' in filter_params:
        # TODO: this is OR logic not AND
        objects = objects.filter(
            categories__title__in=filter_params['categories'])
    if 'agencies' in filter_params:
        objects = objects.filter(
            agency__short_name__in=filter_params['agencies'])
    if 'listing_types' in filter_params:
        objects = objects.filter(
            listing_type__title__in=filter_params['listing_types'])

    return objects

def get_self_listings(username):
    """
    Get the Listings that belong to this user

    Key: self_listings:<username>
    """
    username = utils.make_keysafe(username)
    key = 'self_listings:%s' % username
    data = cache.get(key)
    if data is None:
        try:
            user = generic_model_access.get_profile(username)
            data = models.Listing.objects.for_user(username).filter(
                owners__in=[user.id])
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data

def get_listings(username):
    """
    Get Listings this user can see

    Key: listings:<username>
    """
    username = utils.make_keysafe(username)
    key = 'listings:%s' % username
    data = cache.get(key)
    if data is None:
        try:
            data = models.Listing.objects.for_user(username).all()
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data

def get_item_comments(username):
    """
    Get ItemComments this user can see

    Key: item_comments:<username>
    """
    username = utils.make_keysafe(username)
    key = 'item_comments:%s' % username
    data = cache.get(key)
    if data is None:
        try:
            data = models.ItemComment.objects.for_user(username).all()
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data

def _update_rating(username, listing):
    """
    Invoked each time a review is created, deleted, or updated
    """
    reviews = models.ItemComment.objects.filter(listing=listing)
    rate1 = reviews.filter(rate=1).count()
    rate2 = reviews.filter(rate=2).count()
    rate3 = reviews.filter(rate=3).count()
    rate4 = reviews.filter(rate=4).count()
    rate5 = reviews.filter(rate=5).count()
    total_votes = reviews.count()
    total_comments = total_votes - reviews.filter(text=None).count()

    # calculate weighted average
    avg_rate = (5*rate5 + 4*rate4 + 3*rate3 + 2*rate2 + rate1)/total_votes

    # update listing
    listing.total_rate1 = rate1
    listing.total_rate2 = rate2
    listing.total_rate3 = rate3
    listing.total_rate4 = rate4
    listing.total_rate5 = rate5
    listing.total_votes = total_votes
    listing.total_comments = total_comments
    listing.avg_rate = avg_rate
    listing.save()
    return listing

def _add_listing_activity(author, listing, action, change_details=None,
    description=None):
    """
    Adds a ListingActivity

    Args:
        author (models.Profile): author of the change
        listing (models.Listing): listing being affected
        action (models.Action): action being taken
        change_details (Optional(List)): change change details
            [
                {
                    "field_name": "name",
                    "old_value": "old_val",
                    "new_value": "new_val"
                },
                {
                ...
                }
            ]

    Returns:
        models.Listing: The listing being affected

    Raises:
        None

    """
    listing_activity = models.ListingActivity(action=action,
        author=author, listing=listing, description=description)
    listing_activity.save()
    if change_details:
        for i in change_details:
            change = models.ChangeDetail(field_name=i['field_name'],
                old_value=i['old_value'], new_value=i['new_value'])
            change.save()
            listing_activity.change_details.add(change)

    # update the listing
    listing.last_activity = listing_activity
    listing.save()
    return listing

def create_listing(author, listing):
    """
    Create a listing
    """
    listing = _add_listing_activity(author, listing, models.Action.CREATED)
    listing.approval_status = models.ApprovalStatus.IN_PROGRESS
    listing.save()
    return listing

def log_listing_modification(author, listing, change_details):
    """
    Log a listing modification
    """
    listing = _add_listing_activity(author, listing, models.Action.MODIFIED,
        change_details)
    return listing

def submit_listing(author, listing):
    """
    Submit a listing for approval
    """
    listing = _add_listing_activity(author, listing, models.Action.SUBMITTED)
    listing.approval_status = models.ApprovalStatus.PENDING
    listing.save()
    return listing

def approve_listing_by_org_steward(org_steward, listing):
    """
    Give Org Steward approval to a listing
    """
    listing = _add_listing_activity(org_steward, listing,
        models.Action.APPROVED_ORG)
    listing.approval_status = models.ApprovalStatus.APPROVED_ORG
    listing.save()
    return listing

def approve_listing(steward, listing):
    """
    Give final approval to a listing
    """
    listing = _add_listing_activity(steward, listing,
        models.Action.APPROVED)
    listing.approval_status = models.ApprovalStatus.APPROVED
    listing.save()
    return listing

def reject_listing(steward, listing, rejection_description):
    """
    Reject a submitted listing
    """
    listing = _add_listing_activity(steward, listing,
        models.Action.REJECTED, description=rejection_description)
    listing.approval_status = models.ApprovalStatus.REJECTED
    listing.save()
    return listing

def enable_listing(user, listing):
    """
    Enable a listing
    """
    listing = _add_listing_activity(user, listing,
        models.Action.ENABLED)
    listing.is_enabled = True
    listing.save()
    return listing

def disable_listing(steward, listing):
    """
    Disable a listing
    """
    listing = _add_listing_activity(steward, listing, models.Action.DISABLED)
    listing.is_enabled = False
    listing.save()
    return listing

def create_listing_review(username, listing, rating, text=None):
    """
    Create a new review for a listing

    Args:
        username (str): author's username
        rating (int): rating, 1-5
        text (Optional(str)): review text
    Returns:
        {
            "rate": rate,
            "text": text,
            "author": author.id,
            "listing": listing.id,
            "id": comment.id
        }
    """
    author = generic_model_access.get_profile(username)
    comment = models.ItemComment(listing=listing, author=author,
                rate=rating, text=text)
    comment.save()
    # update this listing's rating
    _update_rating(username, listing)

    resp = {
        "rate": rating,
        "text": text,
        "author": author.id,
        "listing": listing.id,
        "id": comment.id
    }
    return resp

def edit_listing_review(username, review, rate, text=None):
    """
    Edit an existing review

    Args:
        username: user making this request
        review (models.ItemComment): review to modify
        rate (int): rating (1-5)
        text (Optional(str)): review text

    Returns:
        The modified review
    """
    # only the author of a review can edit it
    user = generic_model_access.get_profile(username)
    if review.author.user.username != username:
        raise errors.PermissionDenied()

    change_details = [
        {
            'field_name': 'rate',
            'old_value': review.rate,
            'new_value': rate
        },
        {
            'field_name': 'text',
            'old_value': review.text,
            'new_value': text
        }
    ]

    listing = review.listing
    listing = _add_listing_activity(user, listing, models.Action.REVIEW_EDITED,
        change_details=change_details)

    review.rate = rate
    review.text = text
    review.save()

    _update_rating(username, listing)
    return review

def delete_listing_review(username, review):
    """
    Delete an existing review

    Args:
        username: user making this request
        review (models.ItemComment): review to delete

    Returns: Listing associated with this review
    """
    user = generic_model_access.get_profile(username)
    # ensure user is the author of this review, or that user is an org
    # steward or apps mall steward
    priv_roles = ['APPS_MALL_STEWARD', 'ORG_STEWARD']
    if user.highest_role() in priv_roles:
        pass
    elif review.author.user.username != username:
        raise errors.PermissionDenied()

    # make a note of the change
    change_details = [
        {
            'field_name': 'rate',
            'old_value': review.rate,
            'new_value': None
        },
        {
            'field_name': 'text',
            'old_value': review.text,
            'new_value': None
        }
    ]
    # add this action to the log
    listing = review.listing
    listing = _add_listing_activity(review.author, listing,
        models.Action.REVIEW_DELETED, change_details=change_details)

    # delete the review
    review.delete()
    # update this listing's rating
    _update_rating(username, listing)
    return listing

def delete_listing(username, listing):
    """
    TODO: need a way to keep track of this listing as being deleted.

    for now just remove
    """
    user = generic_model_access.get_profile(username)
    app_owners = [i.user.username for i in listing.owners.all()]
    # ensure user is the author of this review, or that user is an org
    # steward or apps mall steward
    priv_roles = ['APPS_MALL_STEWARD', 'ORG_STEWARD']
    if user.highest_role() in priv_roles:
        pass
    elif username not in app_owners:
        raise errors.PermissionDenied()

    listing.delete()

