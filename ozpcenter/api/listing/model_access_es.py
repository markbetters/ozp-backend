"""
Listing Model Access For Elasticsearch

Code was developed to work with Elasticsearch 2.4.*
"""
import json
import logging

from django.conf import settings
from django.http.request import QueryDict
from rest_framework import serializers
from elasticsearch import exceptions

from ozpcenter import models
from ozpcenter import errors
from ozpcenter import constants
from plugins_util.plugin_manager import system_has_access_control
from ozpcenter.api.listing import elasticsearch_util

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))

# Create ES client
es_client = elasticsearch_util.es_client


class SearchParamParser(object):
    """
    Parser for Search Parameters

    Filter_params can contain - filter_params
        * List of category names (OR logic)
        * List of agencies (OR logic)
        * List of listing types (OR logic)
    """

    def __init__(self, request):
        self.base_url = '{scheme}://{host}'.format(scheme=request.scheme, host=request.get_host())

        self.search_string = request.query_params.get('search', None)

        if self.search_string:
            try:
                self.search_string = str(self.search_string).strip()
            except:
                self.search_string = None

        if request.query_params.get('limit', False):
            self.limit_set = True
        else:
            self.limit_set = False

        try:
            self.offset = int(request.query_params.get('offset', 0))
        except:
            self.offset = 0

        try:
            self.limit = int(request.query_params.get('limit', 100))
        except:
            self.limit = 100

        # Filtering
        self.tags = [str(record) for record in request.query_params.getlist('tag', [])]
        self.categories = [str(record) for record in request.query_params.getlist('category', [])]
        self.agencies = [str(record) for record in request.query_params.getlist('agency', [])]
        self.listing_types = [str(record) for record in request.query_params.getlist('type', [])]

        # Ordering Example: api/listings/essearch/?search=&limit=24&offset=24&ordering=-title
        self.ordering = [str(record) for record in request.query_params.getlist('ordering', [])]

        # Minscore
        try:
            self.min_score = float(request.query_params.get('minscore', constants.ES_MIN_SCORE))
        except:
            self.min_score = constants.ES_MIN_SCORE

        # Boost - Title
        try:
            self.boost_title = float(request.query_params.get('bti', constants.ES_BOOST_TITLE))
        except:
            self.boost_title = constants.ES_BOOST_TITLE

        # Boost - Description
        try:
            self.boost_description = float(request.query_params.get('bde', constants.ES_BOOST_DESCRIPTION))
        except:
            self.boost_description = constants.ES_BOOST_DESCRIPTION

        # Boost - Short Description
        try:
            self.boost_description_short = float(request.query_params.get('bds', constants.ES_BOOST_DESCRIPTION_SHORT))
        except:
            self.boost_description_short = constants.ES_BOOST_DESCRIPTION_SHORT

        # Boost - Tags
        try:
            self.boost_tags = float(request.query_params.get('btg', constants.ES_BOOST_TAGS))
        except:
            self.boost_tags = constants.ES_BOOST_TAGS

    def __str__(self):
        """
        Convert SearchParamParser Object into JSON String Representation
        """
        temp_dict = {'SearchParamParser': vars(self)}
        return json.dumps(temp_dict)


class ReadOnlyListingSerializer(serializers.ModelSerializer):
    """
    Serializer used to convert listing object into python friendly object
    """
    class Meta:
        model = models.Listing
        depth = 2


def check_elasticsearch():
    """
    Method used to check to see if elasticsearch is up
    """
    if settings.ES_ENABLED is False:
        raise errors.ElasticsearchServiceUnavailable('Elasticsearch is disabled in the settings')
    try:
        results = es_client.info()
        # Results: {'name': 'Human Top', 'version': {'build_snapshot': False, 'number': '2.4.0', 'build_hash': 'ce9f0c7394dee074091dd1bc4e9469251181fc55',
        # 'build_timestamp': '2016-08-29T09:14:17Z', 'lucene_version': '5.5.2'}, 'cluster_name': 'elasticsearch', 'tagline': 'You Know, for Search'}
        keys_to_check = ['name', 'version', 'cluster_name', 'tagline']
        for key in keys_to_check:
            if key not in results:
                raise errors.ElasticsearchServiceUnavailable('Elasticsearch Results missing keys')
        return True
    except exceptions.SerializationError:
        # Exception Value: Unknown mimetype, unable to deserialize: text/html
        raise errors.ElasticsearchServiceUnavailable('Elasticsearch Serialization Error')
    except exceptions.AuthenticationException:
        # Ngnix BasicAuth Fail: TransportError(401, '<html>\r\n<head><title>401 Authorization
        #   Required</title></head>\r\n<body bgcolor="white">\r\n<center><h1>401 Authorization Required</h1></center>\r\n<hr><center>nginx/1.11.6</center>\r\n</body>\r\n</html>\r\n')
        raise errors.ElasticsearchServiceUnavailable('Elasticsearch Authentication Exception')
    except exceptions.ConnectionError:
        # ConnectionError(<urllib3.connection.HTTPConnection object at 0x7f6343212c50>: Failed to establish a new connection: [Errno 111] Connection refused) ...
        raise errors.ElasticsearchServiceUnavailable('Elasticsearch Connection Error')
    except exceptions.TransportError:
        # Nginx reverse proxy can't find elasticsearch but correct BasicAuth
        #    TransportError(502, 'An error occurred.</h1>\n<p>Sorry, the page you are looking for is currently unavailable.<br/>\nPlease try again later.....
        raise errors.ElasticsearchServiceUnavailable('Elasticsearch Transport Error')
    raise errors.ElasticsearchServiceUnavailable('Elasticsearch Check Error')


def recreate_index_mapping():
    """
    Recreate Index Mapping
    """
    if settings.ES_ENABLED:
        check_elasticsearch()
        logger.info('Checking to see if Index [{}] exist'.format(settings.ES_INDEX_NAME))

        if es_client.indices.exists(settings.ES_INDEX_NAME):
            logger.info('Deleting [{}] index...'.format(settings.ES_INDEX_NAME))
            res = es_client.indices.delete(index=settings.ES_INDEX_NAME)
            logger.info('Delete acknowledged: {}'.format(res.get('acknowledged', False)))

        request_body = elasticsearch_util.get_mapping_setting_obj()

        logger.info('Creating [{}] index...'.format(settings.ES_INDEX_NAME))
        res = es_client.indices.create(index=settings.ES_INDEX_NAME, body=request_body)
        logger.info('Create Index Acknowledged: {}'.format(res.get('acknowledged', False)))

        es_client.cluster.health(wait_for_status='yellow', request_timeout=20)
    else:
        logger.debug('Elasticsearch is not enabled')


def bulk_reindex():
    """
    Reindex Listing Data into an Elasticsearch Index

    Steps:
        Checks to see if elasticsearch connection is good
        Removes the index if it already exist
        Creates the index with mapping
        Reindex data
        Wait for the cluster health to turn yellow

    To check index in elasticsearch:
        http://127.0.0.1:9200/appsmall/_search?size=10000&pretty
    """
    logger.info('Starting Indexing Process')
    check_elasticsearch()
    recreate_index_mapping()
    # Convert Listing Objects into Python Objects
    all_listings = models.Listing.objects.all()
    serializer = ReadOnlyListingSerializer(all_listings, many=True)
    serializer_results = serializer.data

    bulk_data = []

    for record in serializer_results:
        # Transform Serializer records into records for elasticsearch
        record_clean_obj = elasticsearch_util.prepare_clean_listing_record(record)

        op_dict = {
            'index': {
                '_index': settings.ES_INDEX_NAME,
                '_type': settings.ES_TYPE_NAME,
                '_id': record_clean_obj[settings.ES_ID_FIELD]
            }
        }

        bulk_data.append(op_dict)
        bulk_data.append(record_clean_obj)

    # Bulk index the data
    logger.info('Bulk indexing listings...')
    res = es_client.bulk(index=settings.ES_INDEX_NAME, body=bulk_data, refresh=True)

    if res.get('errors', True):
        logger.error('Error Bulk Indexing')
    else:
        logger.info('Bulk Indexing Successful')

    logger.debug('Waiting for cluster to turn yellow')
    es_client.cluster.health(wait_for_status='yellow', request_timeout=20)
    logger.debug('Finish waiting for cluster to turn yellow')


def get_user_exclude_orgs(username):
    """
    Get User's Orgs to exclude
    """
    exclude_orgs = None

    user = models.Profile.objects.get(user__username=username)

    # Filter out private listings - private apps (apps only from user's agency) requirement
    if user.highest_role() == 'APPS_MALL_STEWARD':
        exclude_orgs = []
    elif user.highest_role() == 'ORG_STEWARD':
        user_orgs = user.stewarded_organizations.all()
        user_orgs = [i.title for i in user_orgs]
        exclude_orgs_obj = models.Agency.objects.exclude(title__in=user_orgs)
        exclude_orgs = [agency.short_name for agency in exclude_orgs_obj]
    else:
        user_orgs = user.organizations.all()
        user_orgs = [i.title for i in user_orgs]
        exclude_orgs_obj = models.Agency.objects.exclude(title__in=user_orgs)
        exclude_orgs = [agency.short_name for agency in exclude_orgs_obj]

    return exclude_orgs


def suggest(request_username, search_param_parser):
    """
    Suggest

    It must respects restrictions
     - Private apps (apps only from user's agency)
     - User's max_classification_level

    Args:
        request_username(string)
        search_param_parser(SearchParamParser): Parsed Request Search Object

    Returns:
        listing titles in a list
    """
    check_elasticsearch()

    if search_param_parser.search_string is None:
        return []

    user_exclude_orgs = get_user_exclude_orgs(request_username)

    # Override Limit - Only 15 results should come if limit was not set
    if search_param_parser.limit_set is False:
        search_param_parser.limit = constants.ES_SUGGEST_LIMIT

    search_query = elasticsearch_util.make_search_query_obj(search_param_parser, exclude_agencies=user_exclude_orgs)
    # Only Retrieve ['title', 'security_marking', 'id'] fields from Elasticsearch for suggestions
    search_query['_source'] = ['title', 'security_marking', 'id']

    # print(json.dumps(search_query, indent=4))  #  Print statement for debugging output
    res = es_client.search(index=settings.ES_INDEX_NAME, body=search_query)

    hits = res.get('hits', {}).get('hits', None)
    if not hits:
        return []

    hit_titles = []

    for hit in hits:
        source = hit.get('_source')

        exclude_bool = False
        if not source.get('security_marking'):
            exclude_bool = True
            logger.debug('Listing {0!s} has no security_marking'.format(source.get('title')))
        if not system_has_access_control(request_username, source.get('security_marking')):
            exclude_bool = True

        if exclude_bool is False:
            temp = {'title': source['title'], 'id': source['id']}
            hit_titles.append(temp)

    return hit_titles


def generate_link(search_param_parser, offset_prediction):
    """
    Generate next/previous URL links

    Args:
        search_param_parser(SearchParamParser): Parsed Request Search Object
        offset_prediction: offset prediction number

    Returns:
        URL for next/previous links (string)
    """
    query_temp = QueryDict(mutable=True)
    query_temp.update({'search': search_param_parser.search_string})
    query_temp.update({'offset': offset_prediction})
    query_temp.update({'limit': search_param_parser.limit})  # Limit stays the same

    [query_temp.update({'category': current_category}) for current_category in search_param_parser.categories]
    [query_temp.update({'agency': current_category}) for current_category in search_param_parser.agencies]
    [query_temp.update({'type': current_category}) for current_category in search_param_parser.listing_types]

    return '{!s}/api/listings/essearch/?{!s}'.format(search_param_parser.base_url, query_temp.urlencode())


def search(request_username, search_param_parser):
    """
    Filter Listings
    Too many variations to cache results

    Users shall be able to search for listings'
     - title
     - description
     - description_short
     - tags__name

    Filter by
     - category
     - agency
     - listing types

    Users shall only see what they are authorized to see
      'is_private': false,
      'approval_status': 'APPROVED',
      'is_deleted': false,
      'is_enabled': true,
      'security_marking': 'UNCLASSIFIED',

    Sorted by Relevance
      'avg_rate': 0,
      'total_votes': 0,
      'total_rate5': 0,
      'total_rate4': 0,
      'total_rate3': 0,
      'total_rate2': 0,
      'total_rate1': 0,
      'total_reviews': 0,
      'is_featured': true,

    It must respects restrictions
     - Private apps (apps only from user's agency)
     - User's max_classification_level

    Args:
        username(str): username
        search_param_parser(SearchParamParser): parameters
    """
    check_elasticsearch()

    user_exclude_orgs = get_user_exclude_orgs(request_username)
    search_query = elasticsearch_util.make_search_query_obj(search_param_parser, exclude_agencies=user_exclude_orgs)

    # print(json.dumps(search_query, indent=4))
    res = es_client.search(index=settings.ES_INDEX_NAME, body=search_query)

    hits = res.get('hits', {})
    inner_hits = hits.get('hits', None)
    if not hits:
        return []

    hit_titles = []

    excluded_count = 0

    for current_innter_hit in inner_hits:
        source = current_innter_hit.get('_source')
        source['_score'] = current_innter_hit.get('_score')

        # Add URLs to icons
        image_keys_to_add_url = ['large_icon',
                                 'small_icon',
                                 'banner_icon',
                                 'large_banner_icon']

        for image_key in image_keys_to_add_url:
            if source.get(image_key) is not None:
                if search_param_parser.base_url:
                    source[image_key]['url'] = '{!s}/api/image/{!s}/'.format(search_param_parser.base_url, source[image_key]['id'])
                else:
                    source[image_key]['url'] = '/api/image/{!s}/'.format(source[image_key]['id'])

        exclude_bool = False
        if not source.get('security_marking'):
            exclude_bool = True
            logger.debug('Listing {0!s} has no security_marking'.format(source.get('title')))
        if not system_has_access_control(request_username, source.get('security_marking')):
            exclude_bool = True

        if exclude_bool is False:
            hit_titles.append(source)
        else:
            excluded_count = excluded_count + 1

    # Total Records in Elasticsearch
    final_count = hits.get('total')
    # Total Records minus what the user does not have access to see, this count should never be below zero
    # TODO: Figure out smarter logic for excluded_count compensation (rivera 11/14/2016)
    final_count_with_excluded = final_count - excluded_count

    final_results = {
        'count': final_count_with_excluded,
        'results': hit_titles
    }

    final_results['previous'] = None
    final_results['next'] = None

    # if final_count_with_excluded < 0 then previous and next should be None
    if final_count_with_excluded < 0:
        return final_results

    previous_offset_prediction = search_param_parser.offset - search_param_parser.limit
    next_offset_prediction = search_param_parser.offset + search_param_parser.limit

    final_results['next_offset_prediction'] = next_offset_prediction

    # Previous URL - previous_offset_prediction is less than zero, previous should be None
    if previous_offset_prediction >= 0:
        final_results['previous'] = generate_link(search_param_parser, previous_offset_prediction)

    # Next URL
    if next_offset_prediction <= final_count_with_excluded:
        final_results['next'] = generate_link(search_param_parser, next_offset_prediction)

    return final_results
