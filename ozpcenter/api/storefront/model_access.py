"""
Storefront and Metadata Model Access

Query to get user roles and orgs
SELECT
  ozpcenter_profile.id profile_id,
  ozpcenter_profile.display_name profile_display_name,
  auth_user.username profile_username,
  auth_group.name profile_group_name,
  CASE auth_group.name
    WHEN 'APPS_MALL_STEWARD' THEN 1
    WHEN 'ORG_STEWARD' THEN 2
    WHEN 'USER' THEN 3
  END role_priority,
  agency.title agency_title,
  steward_agency.title steward_agency

FROM ozpcenter_profile
  JOIN auth_user ON (ozpcenter_profile.user_id = auth_user.id)
  JOIN auth_user_groups ON (auth_user_groups.user_id = auth_user.id)
  JOIN auth_group ON (auth_user_groups.group_id = auth_group.id)

  LEFT JOIN agency_profile ON (ozpcenter_profile.id = agency_profile.profile_id)
  LEFT JOIN ozpcenter_agency agency ON (agency_profile.agency_id = agency.id)

  LEFT JOIN stewarded_agency_profile ON (ozpcenter_profile.id = stewarded_agency_profile.profile_id)
  LEFT JOIN ozpcenter_agency steward_agency ON (stewarded_agency_profile.agency_id = steward_agency.id)

ORDER BY profile_username, role_priority
"""
import logging

from django.core.urlresolvers import reverse
from django.db.models.functions import Lower
from django.db import connection
import msgpack

import ozpcenter.api.listing.serializers as listing_serializers
from ozpcenter import models
from ozpcenter.pipe import pipes
from ozpcenter.pipe import pipeline
from ozpcenter.recommend import recommend_utils

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def get_sql_statement():
    schema_class_str = str(connection.SchemaEditorClass)
    is_deleted = None
    is_enabled = None

    if 'sqlite' in schema_class_str:
        is_deleted = '0'
        is_enabled = '1'
    elif 'postgres' in schema_class_str:
        is_deleted = 'False'
        is_enabled = 'True'
    else:
        raise Exception('Get SQL Statment ENGINE Error')

    sql_statement = '''
SELECT DISTINCT
  ozpcenter_listing.id,
  ozpcenter_listing.title,
  ozpcenter_listing.approved_date,
  ozpcenter_listing.edited_date,
  ozpcenter_listing.description,
  ozpcenter_listing.launch_url,
  ozpcenter_listing.version_name,
  ozpcenter_listing.unique_name,
  ozpcenter_listing.what_is_new,
  ozpcenter_listing.requirements,
  ozpcenter_listing.description_short,
  ozpcenter_listing.approval_status,
  ozpcenter_listing.is_enabled,
  ozpcenter_listing.is_featured,
  ozpcenter_listing.avg_rate,
  ozpcenter_listing.total_rate1,
  ozpcenter_listing.total_rate2,
  ozpcenter_listing.total_rate3,
  ozpcenter_listing.total_rate4,
  ozpcenter_listing.total_rate5,
  ozpcenter_listing.total_votes,
  ozpcenter_listing.total_reviews,
  ozpcenter_listing.iframe_compatible,
  ozpcenter_listing.security_marking,
  ozpcenter_listing.is_private,
  ozpcenter_listing.current_rejection_id,
  ozpcenter_listing.last_activity_id,
  ozpcenter_listing.listing_type_id,
  ozpcenter_listing.required_listings_id,
  ozpcenter_listing.is_deleted,

  /* One to Many */
  ozpcenter_listing.listing_type_id,
  ozpcenter_listingtype.title listing_type_title,

  /* One to Many Images*/
  ozpcenter_listing.agency_id agency_id,
  ozpcenter_agency.title agency_title,
  ozpcenter_agency.short_name agency_short_name,

  ozpcenter_listing.small_icon_id,
  small_icon.security_marking small_icon_security_marking,

  ozpcenter_listing.large_icon_id,
  large_icon.security_marking large_icon_security_marking,

  ozpcenter_listing.banner_icon_id,
  banner_icon.security_marking banner_icon_security_marking,

  ozpcenter_listing.large_banner_icon_id,
  large_banner_icon.security_marking large_banner_icon_security_marking,

  /* Many to Many */
  /* Category */
  category_listing.category_id,
  ozpcenter_category.title category_title,
  ozpcenter_category.description category_description,

  /* Contact */
  contact_listing.contact_id contact_id,
  ozpcenter_contact.contact_type_id contact_type_id, /* Check to see if contact_id and contact_type_id is correct*/
  ozpcenter_contacttype.name contact_type_name,
  ozpcenter_contact.secure_phone contact_secure_phone,
  ozpcenter_contact.unsecure_phone contact_unsecure_phone,
  ozpcenter_contact.email contact_email,
  ozpcenter_contact.name contact_name,
  ozpcenter_contact.organization contact_organization,

  /* Tags */
  tag_listing.tag_id,
  ozpcenter_tag.name tag_name,

  /* Owners */
  owners.profile_id,
  owner_profile.display_name owner_display_name,
  owner_profile.user_id owner_user_id,
  owner_user.username owner_username,

  /* Intents */
  intent_listing.intent_id,
  ozpcenter_intent.action intent_action,

  /* Bookmarks */
  lib_entries.bookmark_count
FROM
  ozpcenter_listing
/* One to Many Joins */
JOIN ozpcenter_agency ON (ozpcenter_listing.agency_id = ozpcenter_agency.id)
JOIN ozpcenter_listingtype ON (ozpcenter_listingtype.id = ozpcenter_listing.listing_type_id)
JOIN ozpcenter_image small_icon ON (small_icon.id = ozpcenter_listing.small_icon_id)
JOIN ozpcenter_image large_icon ON (large_icon.id = ozpcenter_listing.small_icon_id)
JOIN ozpcenter_image banner_icon ON (banner_icon.id = ozpcenter_listing.small_icon_id)
JOIN ozpcenter_image large_banner_icon ON (large_banner_icon.id = ozpcenter_listing.small_icon_id)
/* Many to Many Joins */

/* Categories */
LEFT JOIN category_listing ON (category_listing.listing_id = ozpcenter_listing.id)
LEFT JOIN ozpcenter_category on (category_listing.category_id = ozpcenter_category.id)

/* Contacts */
LEFT JOIN contact_listing ON (contact_listing.listing_id = ozpcenter_listing.id)
LEFT JOIN ozpcenter_contact on (contact_listing.contact_id = ozpcenter_contact.id)
LEFT JOIN ozpcenter_contacttype on (ozpcenter_contact.contact_type_id = ozpcenter_contacttype.id)

/* Tags */
LEFT JOIN tag_listing ON (tag_listing.listing_id = ozpcenter_listing.id)
LEFT JOIN ozpcenter_tag ON (tag_listing.tag_id = ozpcenter_tag.id)

/* Owners */
LEFT JOIN profile_listing owners ON (owners.listing_id = ozpcenter_listing.id)
LEFT JOIN ozpcenter_profile owner_profile ON (owners.profile_id = owner_profile.id)
LEFT JOIN auth_user owner_user ON (owner_profile.user_id = owner_user.id)

/* Intent */
LEFT JOIN intent_listing ON (intent_listing.listing_id = ozpcenter_listing.id)
LEFT JOIN ozpcenter_intent ON (intent_listing.intent_id = ozpcenter_intent.id)

/* Bookmarks */
LEFT JOIN (SELECT ozpcenter_applicationlibraryentry.listing_id, count(ozpcenter_applicationlibraryentry.listing_id) bookmark_count
           FROM ozpcenter_applicationlibraryentry
           GROUP BY ozpcenter_applicationlibraryentry.listing_id) lib_entries ON (lib_entries.listing_id = ozpcenter_listing.id)
/*
Get Listings that are enabled, not deleted, and approved
*/
WHERE ozpcenter_listing.is_enabled = {} AND
      ozpcenter_listing.is_deleted = {} AND
      ozpcenter_listing.approval_status = 'APPROVED'
ORDER BY ozpcenter_listing.approved_date DESC;
    '''.format(is_enabled, is_deleted)
    return sql_statement


def get_user_listings(username, request, exclude_orgs=None):
    """
    Get User listings

    Returns:
        Python object of listings
    """
    exclude_orgs = exclude_orgs or []

    mapping_dict = {}

    cursor = connection.cursor()

    cursor.execute(get_sql_statement())
    rows = dictfetchall(cursor)

    categories_set = set()
    tags_set = set()
    contacts_set = set()
    profile_set = set()
    intents_set = set()

    for row in rows:
        if row['id'] not in mapping_dict:
            mapping_dict[row['id']] = {
                "id": row['id'],
                "unique_name": row['unique_name'],
                "is_enabled": row['is_enabled'],
                "is_private": row['is_private'],

                "required_listings_id": row['required_listings_id'],

                "total_rate1": row['total_rate1'],
                "total_rate2": row['total_rate2'],
                "total_rate3": row['total_rate3'],
                "total_rate4": row['total_rate4'],
                "total_rate5": row['total_rate5'],
                "avg_rate": row['avg_rate'],
                "total_reviews": row['total_reviews'],
                "total_votes": row['total_votes'],

                "approved_date": row['approved_date'],

                "requirements": row['requirements'],
                "iframe_compatible": row['iframe_compatible'],

                "what_is_new": row['what_is_new'],

                "is_deleted": row['is_deleted'],
                "security_marking": row['security_marking'],
                "version_name": row['version_name'],
                "approval_status": row['approval_status'],
                "current_rejection_id": row['current_rejection_id'],
                "is_featured": row['is_featured'],
                "title": row['title'],
                "description_short": row['description_short'],


                "launch_url": row['launch_url'],
                "edited_date": row['edited_date'],
                "description": row['description'],

                # One to One
                "listing_type": {"title": row['listing_type_title']},

                "agency": {'title': row['agency_title'],
                           'short_name': row['agency_short_name']},

                "small_icon": {"id": row['small_icon_id'],
                               'url': request.build_absolute_uri(reverse('image-detail', args=[row['small_icon_id']])),
                               "security_marking": row['small_icon_security_marking']},

                "large_icon": {"id": row['large_icon_id'],
                               'url': request.build_absolute_uri(reverse('image-detail', args=[row['large_icon_id']])),
                               "security_marking": row['large_icon_security_marking']},

                "banner_icon": {"id": row['banner_icon_id'],
                                'url': request.build_absolute_uri(reverse('image-detail', args=[row['banner_icon_id']])),
                                "security_marking": row['banner_icon_security_marking']},

                "large_banner_icon": {"id": row['large_banner_icon_id'],
                                      'url': request.build_absolute_uri(reverse('image-detail', args=[row['large_banner_icon_id']])),
                                      "security_marking": row['large_banner_icon_security_marking']},

                "last_activity_id": row['last_activity_id']

            }

            if row['bookmark_count']:
                mapping_dict[row['id']]['is_bookmarked'] = True
            else:
                mapping_dict[row['id']]['is_bookmarked'] = False

        # Many to Many
        # Categorys

        if not mapping_dict[row['id']].get('categories'):
            mapping_dict[row['id']]['categories'] = {}
        if row['category_id']:
            current_data = {'title': row['category_title'], 'description': row['category_description']}
            categories_set.add(row['category_id'])

            if row['category_id'] not in mapping_dict[row['id']]['categories']:
                mapping_dict[row['id']]['categories'][row['category_id']] = current_data

        # Tags
        if not mapping_dict[row['id']].get('tags'):
            mapping_dict[row['id']]['tags'] = {}
        if row['tag_id']:
            current_data = {'name': row['tag_name']}
            tags_set.add(row['tag_id'])

            if row['tag_id'] not in mapping_dict[row['id']]['tags']:
                mapping_dict[row['id']]['tags'][row['tag_id']] = current_data

        # Contacts
        if not mapping_dict[row['id']].get('contacts'):
            mapping_dict[row['id']]['contacts'] = {}
        if row['contact_id']:
            current_data = {'id': row['contact_id'],
                            'secure_phone': row['contact_secure_phone'],
                            'unsecure_phone': row['contact_unsecure_phone'],
                            'email': row['contact_email'],
                            'name': row['contact_name'],
                            'organization': row['contact_organization'],
                            'contact_type': {'name': row['contact_type_name']}}
            contacts_set.add(row['contact_id'])

            if row['contact_id'] not in mapping_dict[row['id']]['contacts']:
                mapping_dict[row['id']]['contacts'][row['contact_id']] = current_data

        # Profile
        if not mapping_dict[row['id']].get('owners'):
            mapping_dict[row['id']]['owners'] = {}
        if row['profile_id']:
            current_data = {'display_name': row['owner_display_name'],
                'user': {'username': row['owner_username']}}
            profile_set.add(row['profile_id'])

            if row['profile_id'] not in mapping_dict[row['id']]['owners']:
                mapping_dict[row['id']]['owners'][row['profile_id']] = current_data

        # Intent
        if not mapping_dict[row['id']].get('intents'):
            mapping_dict[row['id']]['intents'] = {}
        if row['intent_id']:
            intents_set.add(row['intent_id'])
            if row['intent_id'] not in mapping_dict[row['id']]['intents']:
                mapping_dict[row['id']]['intents'][row['intent_id']] = None

    for profile_key in mapping_dict:
        profile_map = mapping_dict[profile_key]
        profile_map['owners'] = [profile_map['owners'][p_key] for p_key in profile_map['owners']]
        profile_map['tags'] = [profile_map['tags'][p_key] for p_key in profile_map['tags']]
        profile_map['categories'] = [profile_map['categories'][p_key] for p_key in profile_map['categories']]
        profile_map['contacts'] = [profile_map['contacts'][p_key] for p_key in profile_map['contacts']]
        profile_map['intents'] = [profile_map['intents'][p_key] for p_key in profile_map['intents']]

    output_list = []

    for listing_id in mapping_dict:
        listing_values = mapping_dict[listing_id]

        if listing_values['is_private'] is True:
            if listing_values['agency']['title'] not in exclude_orgs:
                output_list.append(listing_values)
        else:
            output_list.append(listing_values)

    return output_list


def get_recommendation_listing_ids(profile_instance):
    # Get Recommended Listings for owner
    target_profile_recommended_entry = models.RecommendationsEntry.objects.filter(target_profile=profile_instance).first()

    recommended_entry_data = {}
    if target_profile_recommended_entry:
        recommendation_data = target_profile_recommended_entry.recommendation_data
        if recommendation_data:
            recommended_entry_data = msgpack.unpackb(recommendation_data, encoding='utf-8')

    recommendation_combined_dict = {'profile': {}}

    for recommender_friendly_name in recommended_entry_data:
        recommender_name_data = recommended_entry_data[recommender_friendly_name]
        # print(recommender_name_data)
        recommender_name_weight = recommender_name_data['weight']
        recommender_name_recommendations = recommender_name_data['recommendations']

        for recommendation_tuple in recommender_name_recommendations:
            current_listing_id = recommendation_tuple[0]
            current_listing_score = recommendation_tuple[1]

            if current_listing_id in recommendation_combined_dict['profile']:
                recommendation_combined_dict['profile'][current_listing_id] = recommendation_combined_dict['profile'][current_listing_id] + (current_listing_score * recommender_name_weight)
            else:
                recommendation_combined_dict['profile'][current_listing_id] = current_listing_score * recommender_name_weight

    sorted_recommendations_combined_dict = recommend_utils.get_top_n_score(recommendation_combined_dict, 40)
    # sorted_recommendations_combined_dict = {'profile': [[11, 8.5], [112, 8.0], [85, 7.0], [86, 7.0], [87, 7.0],
    #    [88, 7.0], [89, 7.0], [90, 7.0], [81, 6.0], [62, 6.0],
    #    [21, 5.5], [1, 5.0], [113, 5.0], [111, 5.0], [114, 5.0], [64, 4.0], [66, 4.0], [68, 4.0], [70, 4.0], [72, 4.0]]}
    listing_ids_list = [entry[0] for entry in sorted_recommendations_combined_dict['profile']]
    return listing_ids_list, recommended_entry_data


def get_storefront_new(username, request):
    """
    Returns data for /storefront api invocation including:
        * recommended listings (max=10)
        * featured listings (max=12)
        * recent (new) listings (max=24)
        * most popular listings (max=36)

    Args:
        username

    Returns:
        {
            'recommended': [Listing],
            'featured': [Listing],
            'recent': [Listing],
            'most_popular': [Listing]
        }
    """
    extra_data = {}
    profile = models.Profile.objects.get(user__username=username)

    if profile.highest_role() == 'APPS_MALL_STEWARD':
        exclude_orgs = []
    elif profile.highest_role() == 'ORG_STEWARD':
        user_orgs = profile.stewarded_organizations.all()
        user_orgs = [i.title for i in user_orgs]
        exclude_orgs = [agency.title for agency in models.Agency.objects.exclude(title__in=user_orgs)]
    else:
        user_orgs = profile.organizations.all()
        user_orgs = [i.title for i in user_orgs]
        exclude_orgs = [agency.title for agency in models.Agency.objects.exclude(title__in=user_orgs)]

    current_listings = get_user_listings(username, request, exclude_orgs)

    # Get Recommended Listings for owner
    if profile.is_beta_user():
        recommendation_listing_ids, recommended_entry_data = get_recommendation_listing_ids(profile)
        listing_ids_list = set(recommendation_listing_ids)

        recommended_listings_raw = []
        for current_listing in current_listings:
            if current_listing['id'] in listing_ids_list:
                recommended_listings_raw.append(current_listing)

        recommended_listings = pipeline.Pipeline(recommend_utils.ListIterator(recommended_listings_raw),
                                            [pipes.JitterPipe(),
                                             pipes.ListingDictPostSecurityMarkingCheckPipe(username),
                                             pipes.LimitPipe(10)]).to_list()
    else:
        recommended_listings = []

    # Get Featured Listings
    featured_listings = pipeline.Pipeline(recommend_utils.ListIterator(current_listings),
                                      [pipes.ListingDictPostSecurityMarkingCheckPipe(username, featured=True),
                                       pipes.LimitPipe(12)]).to_list()
    # Get Recent Listings
    recent_listings = pipeline.Pipeline(recommend_utils.ListIterator(current_listings),
                                      [pipes.ListingDictPostSecurityMarkingCheckPipe(username),
                                       pipes.LimitPipe(24)]).to_list()

    most_popular_listings = pipeline.Pipeline(recommend_utils.ListIterator(sorted(current_listings, key=lambda k: (k['avg_rate'], ['total_reviews']), reverse=True)),
                                      [pipes.ListingDictPostSecurityMarkingCheckPipe(username),
                                       pipes.LimitPipe(36)]).to_list()
    # TODO 2PI filtering
    data = {
        'recommended': recommended_listings,
        'featured': featured_listings,
        'recent': recent_listings,
        'most_popular': most_popular_listings
    }

    return data, extra_data


def get_storefront_recommended(username, pre_fetch=True):
    """
    Get Recommended Listings for storefront
    """
    extra_data = {}

    profile = models.Profile.objects.get(user__username=username)

    if not profile.is_beta_user():
        return [], extra_data

    # Retrieve List of Recommended Apps for profile:
    listing_ids_list, recommended_entry_data = get_recommendation_listing_ids(profile)
    extra_data['recommended_entry_data'] = recommended_entry_data

    # Retrieve Profile Bookmarks and remove bookmarked from recommendation list
    bookmarked_apps_list = set([application_library_entry.listing.id for application_library_entry in models.ApplicationLibraryEntry.objects.for_user(username)])

    listing_ids_list_temp = []

    for current_listing_id in listing_ids_list:
        if current_listing_id not in bookmarked_apps_list:
            listing_ids_list_temp.append(current_listing_id)

    listing_ids_list = listing_ids_list_temp

    # Send new recommendation list minus bookmarked apps to User Interface
    recommended_listings_queryset = models.Listing.objects.for_user_organization_minus_security_markings(username).filter(pk__in=listing_ids_list,
                                                                                                                          approval_status=models.Listing.APPROVED,
                                                                                                                          is_enabled=True,
                                                                                                                          is_deleted=False).all()

    if pre_fetch:
        recommended_listings_queryset = listing_serializers.ListingSerializer.setup_eager_loading(recommended_listings_queryset)

    # Fix Order of Recommendations
    id_recommended_object_mapper = {}
    for recommendation_entry in recommended_listings_queryset:
        id_recommended_object_mapper[recommendation_entry.id] = recommendation_entry

    # recommended_listings_raw = [id_recommended_object_mapper[listing_id] for listing_id in listing_ids_list]

    recommended_listings_raw = []

    for listing_id in listing_ids_list:
        if listing_id in id_recommended_object_mapper:
            recommended_listings_raw.append(id_recommended_object_mapper[listing_id])

    # Post security_marking check - lazy loading
    recommended_listings = pipeline.Pipeline(recommend_utils.ListIterator([recommendations_listing for recommendations_listing in recommended_listings_raw]),
                                      [pipes.JitterPipe(),
                                       pipes.ListingPostSecurityMarkingCheckPipe(username),
                                       pipes.LimitPipe(10)]).to_list()

    return recommended_listings, extra_data


def get_storefront_featured(username, pre_fetch=True):
    """
    Get Featured Listings for storefront
    """
    # Get Featured Listings
    featured_listings_raw = models.Listing.objects.for_user_organization_minus_security_markings(
        username).filter(
            is_featured=True,
            approval_status=models.Listing.APPROVED,
            is_enabled=True,
            is_deleted=False)

    if pre_fetch:
        featured_listings_raw = listing_serializers.ListingSerializer.setup_eager_loading(featured_listings_raw)

    featured_listings = pipeline.Pipeline(recommend_utils.ListIterator([listing for listing in featured_listings_raw]),
                                      [pipes.ListingPostSecurityMarkingCheckPipe(username)]).to_list()
    return featured_listings


def get_storefront_recent(username, pre_fetch=True):
    """
    Get Recent Listings for storefront
    """
    # Get Recent Listings
    recent_listings_raw = models.Listing.objects.for_user_organization_minus_security_markings(
        username).order_by('-approved_date').filter(
        approval_status=models.Listing.APPROVED,
        is_enabled=True,
        is_deleted=False)

    if pre_fetch:
        recent_listings_raw = listing_serializers.ListingSerializer.setup_eager_loading(recent_listings_raw)

    recent_listings = pipeline.Pipeline(recommend_utils.ListIterator([listing for listing in recent_listings_raw]),
                                      [pipes.ListingPostSecurityMarkingCheckPipe(username),
                                       pipes.LimitPipe(24)]).to_list()
    return recent_listings


def get_storefront_most_popular(username, pre_fetch=True):
    """
    Get Most Popular Listings for storefront
    """
    # Get most popular listings via a weighted average
    most_popular_listings_raw = models.Listing.objects.for_user_organization_minus_security_markings(
        username).filter(
            approval_status=models.Listing.APPROVED,
            is_enabled=True,
            is_deleted=False).order_by('-avg_rate', '-total_reviews')

    if pre_fetch:
        most_popular_listings_raw = listing_serializers.ListingSerializer.setup_eager_loading(most_popular_listings_raw)

    most_popular_listings = pipeline.Pipeline(recommend_utils.ListIterator([listing for listing in most_popular_listings_raw]),
                                      [pipes.ListingPostSecurityMarkingCheckPipe(username),
                                       pipes.LimitPipe(36)]).to_list()
    return most_popular_listings


def get_storefront(username, pre_fetch=False):
    """
    Returns data for /storefront api invocation including:
        * recommended listings (max=10)
        * featured listings (no limit)
        * recent (new) listings (max=24)
        * most popular listings (max=36)

    NOTE: think about adding Bookmark status to this later on

    Args:
        username

    Returns:
        {
            'recommended': [Listing],
            'featured': [Listing],
            'recent': [Listing],
            'most_popular': [Listing]
        }
    """
    try:
        recommended_listings, extra_data = get_storefront_recommended(username, pre_fetch)

        data = {
            'recommended': recommended_listings,
            'featured': get_storefront_featured(username, pre_fetch),
            'recent': get_storefront_recent(username, pre_fetch),
            'most_popular': get_storefront_most_popular(username, pre_fetch)
        }
    except Exception:
        # raise Exception({'error': True, 'msg': 'Error getting storefront: {0!s}'.format(str(e))})
        raise  # Should be catch in the django framwork
    return data, extra_data


def values_query_set_to_dict(vqs):
    return [item for item in vqs]


def get_metadata(username):
    """
    Returns metadata including:
        * categories
        * organizations (agencies)
        * listing types
        * intents
        * contact types

    Key: metadata
    """
    try:
        data = {}
        data['categories'] = values_query_set_to_dict(models.Category.objects.all().values(
            'id', 'title', 'description').order_by(Lower('title')))

        data['listing_types'] = values_query_set_to_dict(models.ListingType.objects.all().values(
            'title', 'description'))

        data['agencies'] = values_query_set_to_dict(models.Agency.objects.all().values(
            'title', 'short_name', 'icon', 'id'))

        data['contact_types'] = values_query_set_to_dict(models.ContactType.objects.all().values(
            'name', 'required'))

        data['intents'] = values_query_set_to_dict(models.Intent.objects.all().values(
            'action', 'media_type', 'label', 'icon', 'id'))

        # return icon/image urls instead of the id and get listing counts
        for i in data['agencies']:
            # i['icon'] = models.Image.objects.get(id=i['icon']).image_url()
            # i['icon'] = '/TODO'
            i['listing_count'] = models.Listing.objects.for_user(
                username).filter(agency__title=i['title'], approval_status=models.Listing.APPROVED, is_enabled=True).count()

        for i in data['intents']:
            # i['icon'] = models.Image.objects.get(id=i['icon']).image_url()
            i['icon'] = '/TODO'

        return data
    except Exception as e:
        return {'error': True, 'msg': 'Error getting metadata: {0!s}'.format(str(e))}
