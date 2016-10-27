"""
Listing Model Access For Elasticsearch
"""
import logging

# from django.core.exceptions import ObjectDoesNotExist
#
#
# from ozpcenter import models
# from ozpcenter import constants
# from ozpcenter import errors
# from ozpcenter import utils
# import ozpcenter.model_access as generic_model_access
# from plugins_util.plugin_manager import system_anonymize_identifiable_data

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


def filter_listings(username, filter_params):
    """
    Filter Listings

    It must respects restrictions
     - private apps (apps only from user's agency) and user's
     - max_classification_level

    Search Fields
     - title
     - description
     - description_short
     - tags__name

    Filter_params can contain:
        * List of category names (OR logic)
        * List of agencies (OR logic)
        * List of listing types (OR logic)

    Too many variations to cache

    Args:
        username(str): username
        filter_params({}):
            categories = self.request.query_params.getlist('category', False)
            agencies = self.request.query_params.getlist('agency', False)
            listing_types = self.request.query_params.getlist('type', False)
    """
    # TODO: Rewrite 'Filter_params' and 'Search Fields' logic for elasticsearch
    # Use def make_search_query_obj(user_string="", categories=[], agency=None, listing_type=None, size=10)
    # --------------
    # objects = models.Listing.objects.for_user(username).filter(
    #     approval_status=models.Listing.APPROVED).filter(is_enabled=True)
    # if 'categories' in filter_params:
    #     # TODO: this is OR logic not AND
    #     objects = objects.filter(
    #         categories__title__in=filter_params['categories'])
    # if 'agencies' in filter_params:
    #     objects = objects.filter(
    #         agency__short_name__in=filter_params['agencies'])
    # if 'listing_types' in filter_params:
    #     objects = objects.filter(
    #         listing_type__title__in=filter_params['listing_types'])
    #
    # objects = objects.order_by('-avg_rate', '-total_reviews')
    # return objects
    # --------------

    # TODO: Rewrite 'restrictions' logic for elasticsearch
    # --------------
    # # get all listings
    # objects = super(AccessControlListingManager, self).get_queryset()
    # # filter out private listings
    # user = Profile.objects.get(user__username=username)
    # if user.highest_role() == 'APPS_MALL_STEWARD':
    #     exclude_orgs = []
    # elif user.highest_role() == 'ORG_STEWARD':
    #     user_orgs = user.stewarded_organizations.all()
    #     user_orgs = [i.title for i in user_orgs]
    #     exclude_orgs = Agency.objects.exclude(title__in=user_orgs)
    # else:
    #     user_orgs = user.organizations.all()
    #     user_orgs = [i.title for i in user_orgs]
    #     exclude_orgs = Agency.objects.exclude(title__in=user_orgs)
    #
    # objects = objects.exclude(is_private=True,
    #                           agency__in=exclude_orgs)
    #
    # # Filter out listings by user's access level
    # ids_to_exclude = []
    # for i in objects:
    #     if not i.security_marking:
    #         logger.debug('Listing {0!s} has no security_marking'.format(i.title))
    #     if not system_has_access_control(username, i.security_marking):
    #         ids_to_exclude.append(i.id)
    # objects = objects.exclude(pk__in=ids_to_exclude)
    # return objects
    # --------------

    pass
