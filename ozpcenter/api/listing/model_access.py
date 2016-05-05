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
import ozpcenter.constants as constants

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


def get_all_doc_urls():
    return models.DocUrl.objects.all()


def get_all_contacts():
    return models.Contact.objects.all()


def get_screenshots_for_listing(listing):
    return models.Screenshot.objects.filter(listing=listing)


def get_doc_urls_for_listing(listing):
    return models.DocUrl.objects.filter(listing=listing)


def get_listing_type_by_title(title):
    return models.ListingType.objects.get(title=title)


def get_listing_by_id(username, id):
    try:
        return models.Listing.objects.for_user(username).get(id=id)
    except models.Listing.DoesNotExist:
        return None


def get_listing_by_title(username, title):
    return models.Listing.objects.for_user(username).get(title=title)


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
    objects = models.Listing.objects.for_user(username).filter(
        approval_status=models.Listing.APPROVED).filter(is_enabled=True)
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

    objects = objects.order_by('-avg_rate', '-total_reviews')
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


def get_reviews(username):
    """
    Get Reviews this user can see

    Key: reviews:<username>
    """
    username = utils.make_keysafe(username)
    key = 'reviews:%s' % username
    data = cache.get(key)
    if data is None:
        try:
            data = models.Review.objects.for_user(username).all()
            cache.set(key, data)
            return data
        except ObjectDoesNotExist:
            return None
    else:
        return data


def get_review_by_id(id):
    return models.Review.objects.get(id=id)


def get_all_listing_types():
    return models.ListingType.objects.all()


def get_listing_activities_for_user(username):
    """
    Get all ListingActivities for listings that the user is an owner of
    """
    return models.ListingActivity.objects.for_user(username).filter(
        listing__owners__user__username__exact=username)


def get_all_listing_activities(username):
    """
    Get all ListingActivities visible to this user
    """
    return models.ListingActivity.objects.for_user(username).all()


def get_all_tags():
    return models.Tag.objects.all()


def get_all_screenshots():
    # access control enforced on images themselves, not the metadata
    return models.Screenshot.objects.all()


def _update_rating(username, listing):
    """
    Invoked each time a review is created, deleted, or updated
    """
    reviews = models.Review.objects.filter(listing=listing)
    rate1 = reviews.filter(rate=1).count()
    rate2 = reviews.filter(rate=2).count()
    rate3 = reviews.filter(rate=3).count()
    rate4 = reviews.filter(rate=4).count()
    rate5 = reviews.filter(rate=5).count()
    total_votes = reviews.count()
    total_reviews = total_votes - reviews.filter(text=None).count()

    # calculate weighted average
    if total_votes == 0:
        avg_rate = 0
    else:
        avg_rate = (5 * rate5 + 4 * rate4 + 3 * rate3 + 2 * rate2 + rate1) / total_votes
        avg_rate = float('{0:.1f}'.format(avg_rate))

    # update listing
    listing.total_rate1 = rate1
    listing.total_rate2 = rate2
    listing.total_rate3 = rate3
    listing.total_rate4 = rate4
    listing.total_rate5 = rate5
    listing.total_votes = total_votes
    listing.total_reviews = total_reviews
    listing.avg_rate = avg_rate
    listing.edited_date = utils.get_now_utc()
    listing.save()
    return listing


def get_rejection_listings(username):
    activities = models.ListingActivity.objects.for_user(username).filter(
        action=models.ListingActivity.REJECTED)
    return activities


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
    if listing_activity.action == models.ListingActivity.REJECTED:
        listing.current_rejection = listing_activity
    listing.edited_date = utils.get_now_utc()
    listing.save()
    return listing


def create_listing(author, listing):
    """
    Create a listing
    """
    listing = _add_listing_activity(author, listing, models.ListingActivity.CREATED)
    listing.approval_status = models.Listing.IN_PROGRESS
    listing.save()
    return listing


def log_listing_modification(author, listing, change_details):
    """
    Log a listing modification
    """
    listing = _add_listing_activity(author, listing, models.ListingActivity.MODIFIED,
        change_details)
    return listing


def submit_listing(author, listing):
    """
    Submit a listing for approval
    """
    # TODO: check that all required fields are set
    listing = _add_listing_activity(author, listing, models.ListingActivity.SUBMITTED)
    listing.approval_status = models.Listing.PENDING
    listing.edited_date = utils.get_now_utc()
    listing.save()
    return listing


def approve_listing_by_org_steward(org_steward, listing):
    """
    Give Org Steward approval to a listing
    """
    listing = _add_listing_activity(org_steward, listing,
        models.ListingActivity.APPROVED_ORG)
    listing.approval_status = models.Listing.APPROVED_ORG
    listing.edited_date = utils.get_now_utc()
    listing.save()
    return listing


def approve_listing(steward, listing):
    """
    Give final approval to a listing
    """
    listing = _add_listing_activity(steward, listing,
        models.ListingActivity.APPROVED)
    listing.approval_status = models.Listing.APPROVED
    listing.approved_date = utils.get_now_utc()
    listing.edited_date = utils.get_now_utc()
    listing.save()
    return listing


def reject_listing(steward, listing, rejection_description):
    """
    Reject a submitted listing
    """
    listing = _add_listing_activity(steward, listing,
        models.ListingActivity.REJECTED, description=rejection_description)
    listing.approval_status = models.Listing.REJECTED
    listing.edited_date = utils.get_now_utc()
    listing.save()
    return listing


def enable_listing(user, listing):
    """
    Enable a listing
    """
    listing = _add_listing_activity(user, listing, models.ListingActivity.ENABLED)
    listing.is_enabled = True
    listing.edited_date = utils.get_now_utc()
    listing.save()
    return listing


def disable_listing(steward, listing):
    """
    Disable a listing
    """
    listing = _add_listing_activity(steward, listing, models.ListingActivity.DISABLED)
    listing.is_enabled = False
    listing.edited_date = utils.get_now_utc()
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
            "id": review.id
        }
    """
    author = generic_model_access.get_profile(username)
    review = models.Review(listing=listing, author=author,
                rate=rating, text=text)
    review.save()
    # update this listing's rating
    _update_rating(username, listing)

    resp = {
        "rate": rating,
        "text": text,
        "author": author.id,
        "listing": listing.id,
        "id": review.id
    }
    return resp


def edit_listing_review(username, review, rate, text=None):
    """
    Edit an existing review

    Args:
        username: user making this request
        review (models.Review): review to modify
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
    listing = _add_listing_activity(user, listing, models.ListingActivity.REVIEW_EDITED,
        change_details=change_details)

    review.rate = rate
    review.text = text
    review.edited_date = utils.get_now_utc()
    review.save()

    _update_rating(username, listing)
    return review


def delete_listing_review(username, review):
    """
    Delete an existing review

    Args:
        username: user making this request
        review (models.Review): review to delete

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
        models.ListingActivity.REVIEW_DELETED, change_details=change_details)

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


def put_counts_in_listings_endpoint(queryset):
    """
    Add counts to the listing/ endpoint

    Args:
        querset: models.Listing queryset
    Returns:
        {
            "total": <total listings>,
            "organizations": {
                <org_id>: <count>,
                ...
            },
            "enabled": <enabled listings>,
            "IN_PROGRESS": <num>,
            "PENDING": <num>,
            "REJECTED": <num>,
            "APPROVED_ORG": <num>,
            "APPROVED": <num>
        }
    """
    data = {"total": queryset.count(), "organizations": {}}
    num_enabled = queryset.filter(is_enabled=True).count()
    num_in_progress = queryset.filter(
        approval_status=models.Listing.IN_PROGRESS).count()
    num_pending = queryset.filter(
        approval_status=models.Listing.PENDING).count()
    num_rejected = queryset.filter(
        approval_status=models.Listing.REJECTED).count()
    num_approved_org = queryset.filter(
        approval_status=models.Listing.APPROVED_ORG).count()
    num_approved = queryset.filter(
        approval_status=models.Listing.APPROVED).count()
    data['enabled'] = num_enabled
    data[models.Listing.IN_PROGRESS] = num_in_progress
    data[models.Listing.PENDING] = num_pending
    data[models.Listing.REJECTED] = num_rejected
    data[models.Listing.APPROVED_ORG] = num_approved_org
    data[models.Listing.APPROVED] = num_approved

    orgs = models.Agency.objects.all()
    for i in orgs:
        data['organizations'][str(i.id)] = queryset.filter(
            agency__id=i.id).count()
    return data


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   Methods to convert Response representations of objects to strings for use
#   in the change_details of a listing's activity
#
#   For simple strings this is obvious (and a separate method is unnecessary),
#   but for representing objects (and collections of objects), such utilities
#   are useful
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def doc_urls_to_string(doc_urls, queryset=False):
    """
    Args:
        doc_urls: [{"name": "wiki", "url": "http://www.wiki.com"}, ...] OR
        doc_urls: [models.DocUrl] (if queryset=True)
    Returns:
        '(wiki, http://www.wiki.com), ...'
    """
    if queryset:
        new_doc_urls = [(i.name, i.url) for i in doc_urls]
    else:
        new_doc_urls = [(i['name'], i['url']) for i in doc_urls]
    return str(sorted(new_doc_urls))


def screenshots_to_string(screenshots, queryset=False):
    """
    Args:
        screenshots: [({"small_image": {"id": 1}, "large_image": {"id": 2}}), ...] OR
        screenshots: [models.Screenshot] (if queryset=True)
    Returns:
        "[(<small_image_id>, <large_image_id>), ...]"
    """
    if queryset:
        new_screenshots = [(i.small_image.id,
                            i.small_image.security_marking,
                            i.large_image.id,
                            i.large_image.security_marking) for i in screenshots]
    else:
        new_screenshots = [(i['small_image']['id'],
                            i['small_image'].get('security_marking', constants.DEFAULT_SECURITY_MARKING),
                            i['large_image']['id'],
                            i['large_image'].get('security_marking', constants.DEFAULT_SECURITY_MARKING)) for i in screenshots]
    return str(sorted(new_screenshots))


def image_to_string(image, queryset=False, extra_str=None):
    """
    Args:

    Returns:

    """
    if image is None:
        return None

    if queryset:
        image_str = '%s.%s' % (image.id, image.security_marking)
    else:
        image_str = '%s.%s' % (image.get('id'), image.get('security_marking', constants.DEFAULT_SECURITY_MARKING))
    return image_str


def contacts_to_string(contacts, queryset=False):
    """
    Args:
        contacts: [
            {"contact_type": {"name": "Government"},
                "secure_phone": "111-222-3434",
                "unsecure_phone": "444-555-4545",
                "email": "a@a.com",
                "name": "me",
                "organization": null}] OR
            [models.Contact] (if queryset=True)
    Returns:
        [('name', 'email'), ...]
    """
    if queryset:
        new_contacts = [(i.name, i.email, i.secure_phone,
                        i.unsecure_phone, i.organization,
                        i.contact_type.name) for i in contacts]
    else:
        new_contacts = [(i['name'], i['email'], i.get('secure_phone'),
                         i.get('unsecure_phone'), i.get('organization'),
                         i.get('contact_type', {}).get('name')) for i in contacts]
    return str(sorted(new_contacts))


def intents_to_string(intents, queryset=False):
    """
    Args:
        intents: [{"action": "/application/json/view"}, ...] OR
                    [models.Intent] (if queryset=True)
    Returns:
        ['<intent.action', ...]
    """
    if queryset:
        new_intents = [i.action for i in intents]
    else:
        new_intents = [i['action'] for i in intents]
    return str(sorted(new_intents))


def categories_to_string(categories, queryset=False):
    """
    Args:
        categories: [{"title": "Business"}, ...] OR
                    [models.Category] (if queryset=True)
    Returns:
        ['<category.title', ...]
    """
    if queryset:
        new_categories = [i.title for i in categories]
    else:
        new_categories = [i['title'] for i in categories]
    return str(sorted(new_categories))


def tags_to_string(tags, queryset=False):
    """
    Args:
        tags: [{"name": "Demo"}, ...] OR
                    [models.Tag] (if queryset=True)
    Returns:
        ['<tag.name', ...]
    """
    if queryset:
        new_tags = [i.name for i in tags]
    else:
        new_tags = [i['name'] for i in tags]
    return str(sorted(new_tags))


def owners_to_string(owners, queryset=False):
    """
    Args:
        owners: [{"user": {"username": "jack"}}, ...] OR
                    [models.Profile] (if queryset=True)
    Returns:
        ['<Profile.user.username', ...]
    """
    if queryset:
        new_owners = [i.user.username for i in owners]
    else:
        new_owners = [i['user']['username'] for i in owners]
    return str(sorted(new_owners))


def bool_to_string(var):
    return str(var).lower()
