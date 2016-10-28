"""
Listing Model Access For Elasticsearch
"""
import json
import logging

# from django.conf import settings  # TODO: Get Elasticsearch settings
from elasticsearch import Elasticsearch
from rest_framework import serializers

from ozpcenter import models
from plugins_util.plugin_manager import system_has_access_control

# import ozpcenter.model_access as generic_model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


ES_HOST = {
    "host": "localhost",
    "port": 9200
}

INDEX_NAME = 'appsmall'
TYPE_NAME = 'listings'
ID_FIELD = 'id'

# Create ES client
es_client = Elasticsearch(hosts=[ES_HOST])


def get_mapping_setting_obj():
    data = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "filter": {
                    "autocomplete_filter": {
                        "type": "edge_ngram",
                        "min_gram": 1,
                        "max_gram": 20
                    }
                },
                "analyzer": {
                    "autocomplete": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "autocomplete_filter"
                        ]
                    }
                }
            }
        },
        "mappings": {
            "listings": {
                "dynamic": "strict",
                "properties": {
                    "id": {
                        "type": "long"
                    },
                    "title": {
                        "type": "string",
                        "analyzer": "autocomplete",
                        "search_analyzer": "autocomplete"
                    },
                    "agency_id": {
                        "type": "long"
                    },
                    "agency_short_name": {
                        "type": "string"
                    },
                    "agency_title": {
                        "type": "string"
                    },
                    "approval_status": {
                        "type": "string"
                    },
                    "avg_rate": {
                        "type": "double"
                    },
                    "categories": {
                        "type": "nested",
                        "properties": {
                            "description": {
                                "type": "string"
                            },
                            "id": {
                                "type": "long"
                            },
                            "title": {
                                "type": "string"
                            }
                        }
                    },
                    "description": {
                        "type": "string",
                        "analyzer": "autocomplete",
                        "search_analyzer": "autocomplete"
                    },
                    "description_short": {
                        "type": "string",
                        "analyzer": "autocomplete",
                        "search_analyzer": "autocomplete"
                    },
                    "is_deleted": {
                        "type": "boolean"
                    },
                    "is_enabled": {
                        "type": "boolean"
                    },
                    "is_featured": {
                        "type": "boolean"
                    },
                    "is_private": {
                        "type": "boolean"
                    },
                    "listing_type_description": {
                        "type": "string"
                    },
                    "listing_type_id": {
                        "type": "long"
                    },
                    "listing_type_title": {
                        "type": "string"
                    },
                    "security_marking": {
                        "type": "string"
                    },
                    "tags": {
                        "type": "nested",
                        "properties": {
                            "id": {
                                "type": "long"
                            },
                            "name": {
                                "type": "string",
                                "analyzer": "autocomplete",
                                "search_analyzer": "autocomplete"
                            }
                        }
                    },
                    "total_rate1": {
                        "type": "long"
                    },
                    "total_rate2": {
                        "type": "long"
                    },
                    "total_rate3": {
                        "type": "long"
                    },
                    "total_rate4": {
                        "type": "long"
                    },
                    "total_rate5": {
                        "type": "long"
                    },
                    "total_reviews": {
                        "type": "long"
                    },
                    "total_votes": {
                        "type": "long"
                    },
                    "unique_name": {
                        "type": "string"
                    }
                }
            }
        }
    }
    return data


class ReadOnlyListingSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Listing
        depth = 2


def bulk_reindex():
    """
    Reindexing

    Users shall be able to search for listings'
     - title
     - description
     - description_short
     - tags
    Filter by
     - category
     - agency
     - listing types

    Users shall only see what they are authorized to see
      "is_private": false,
      "approval_status": "APPROVED",
      "is_deleted": false,
      "is_enabled": true,
      "security_marking": "UNCLASSIFIED",

    Sorted by Relevance
      "avg_rate": 0,
      "total_votes": 0,
      "total_rate5": 0,
      "total_rate4": 0,
      "total_rate3": 0,
      "total_rate2": 0,
      "total_rate1": 0,
      "total_reviews": 0,
      "is_featured": true,

    Resources:
    https://www.elastic.co/guide/en/elasticsearch/reference/2.4/analyzer.html
    https://qbox.io/blog/quick-and-dirty-autocomplete-with-elasticsearch-completion-suggest
    """
    print('Starting Indexing Process')
    all_listings = models.Listing.objects.all()
    serializer = ReadOnlyListingSerializer(all_listings, many=True)
    serializer_results = serializer.data

    keys_to_remove = ['small_icons', 'contacts', 'last_activity',
                      'required_listings', 'large_icon', 'small_icon',
                      'banner_icon', 'large_banner_icon', 'owners',
                      'current_rejection', 'launch_url', 'what_is_new',
                      'iframe_compatible', 'approved_date',
                      'edited_date', 'version_name', 'requirements',
                      'intents']

    bulk_data = []

    for record in serializer_results:
        # Sample Record (record_json) after clean
        '''
        {
          "id": 316,
          "title": "JotSpot 28",
          "description": "Jot things down",
          "unique_name": "ozp.test.jotspot.28",
          "description_short": "Jot stuff down",
          "approval_status": "APPROVED",
          "is_enabled": true,
          "is_featured": true,
          "is_deleted": false,
          "avg_rate": 4,
          "total_votes": 1,
          "total_rate5": 0,
          "total_rate4": 1,
          "total_rate3": 0,
          "total_rate2": 0,
          "total_rate1": 0,
          "total_reviews": 1,
          "security_marking": "UNCLASSIFIED",
          "is_private": false,
          "agency": {
            "id": 1,
            "title": "Ministry of Truth",
            "short_name": "Minitrue"
          },
          "listing_type": {
            "id": 1,
            "title": "web application",
            "description": "web applications"
          },
          "categories": [
            {
              "id": 4,
              "title": "Education",
              "description": "Educational in nature"
            },
            {
              "id": 14,
              "title": "Tools",
              "description": "Tools and Utilities"
            }
          ],
          "tags": [
            {
              "id": 1,
              "name": "demo"
            }
          ]
        }
        '''
        # Clean Record
        for key in keys_to_remove:
            if key in record:
                del record[key]

        del record['agency']['icon']

        record_clean_obj = json.loads(json.dumps(record))

        # title_suggest = {"input": [ record_clean_obj['title'] ] }
        # record_clean_obj['title_suggest'] =title_suggest

        # Flatten Agency Obj - Makes the search query easier
        record_clean_obj['agency_id'] = record_clean_obj['agency']['id']
        record_clean_obj['agency_short_name'] = record_clean_obj['agency']['short_name']
        record_clean_obj['agency_title'] = record_clean_obj['agency']['title']
        del record_clean_obj['agency']

        # Flatten listing_type Obj - - Makes the search query easier
        record_clean_obj['listing_type_id'] = record_clean_obj['listing_type']['id']
        record_clean_obj['listing_type_description'] = record_clean_obj['listing_type']['description']
        record_clean_obj['listing_type_title'] = record_clean_obj['listing_type']['title']
        del record_clean_obj['listing_type']

        # Transform Serializer records into records for elasticsearch
        # print(record_clean_obj)
        # print('-----------')

        op_dict = {
            "index": {
                "_index": INDEX_NAME,
                "_type": TYPE_NAME,
                "_id": record_clean_obj[ID_FIELD]
            }
        }

        bulk_data.append(op_dict)
        bulk_data.append(record_clean_obj)

    # create ES client, create index
    es = Elasticsearch(hosts=[ES_HOST])

    if es.indices.exists(INDEX_NAME):
        print("deleting '%s' index..." % (INDEX_NAME))
        res = es.indices.delete(index=INDEX_NAME)
        print(" response: '%s'" % (res))

    request_body = get_mapping_setting_obj()

    print("Creating '%s' index..." % (INDEX_NAME))
    res = es.indices.create(index=INDEX_NAME, body=request_body)
    print(" response: '%s'" % (res))

    # Bulk index the data
    print("Bulk indexing listings...")
    res = es.bulk(index=INDEX_NAME, body=bulk_data, refresh=True)
    # print(" response: '%s'" % (res))

    print("Done Indexing")
    # http://127.0.0.1:9200/appsmall/_search?size=10000&pretty


def ping_elasticsearch():
    """
    Used to check to see if elasticsearch is up
    """
    return es_client.ping()


def suggest(username, params_dict):
    """
    suggest
    """
    search_input = params_dict['search']
    if search_input is None:
        return []

    # Override Limit - Only 10 results should come
    params_dict['limit'] = 10
    search_query = make_search_query_obj(params_dict, min_score=0.3)
    search_query['_source'] = ['title', 'security_marking']

    # print(json.dumps(search_query, indent=4))
    res = es_client.search(index=INDEX_NAME, body=search_query)

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
        if not system_has_access_control(username, source.get('security_marking')):
            exclude_bool = True

        if exclude_bool is False:
            hit_titles.append(source['title'])

    return hit_titles


def search(username, params_dict):
    search_input = params_dict['search']
    if search_input is None:
        return []

    search_query = make_search_query_obj(params_dict, min_score=0.3, exclude_agencies=['miniluv', 'minitrue'])

    print(json.dumps(search_query, indent=4))
    res = es_client.search(index=INDEX_NAME, body=search_query)

    hits = res.get('hits', {})
    inner_hits = hits.get('hits', None)
    if not hits:
        return []

    hit_titles = []

    excluded_count = 10

    for current_innter_hit in inner_hits:
        source = current_innter_hit.get('_source')
        source['_score'] = current_innter_hit.get('_score')

        exclude_bool = False
        if not source.get('security_marking'):
            exclude_bool = True
            logger.debug('Listing {0!s} has no security_marking'.format(source.get('title')))
        if not system_has_access_control(username, source.get('security_marking')):
            exclude_bool = True

        if exclude_bool is False:
            hit_titles.append(source)
        else:
            excluded_count = excluded_count + 1

    final_results = {
        "count": hits.get('total') - excluded_count,
        "next": None,
        "previous": "/api/listings/search/?category=Education&limit=10&offset=13&search=6&type=web+application",
        "results": hit_titles
    }

    return final_results


def make_search_query_obj(filter_params, exclude_agencies=[], min_score=0.8):
    """
    Function is used to make elasticsearch query for searching

    user_string="", categories=[], agencies=[], exclude_agencies=[], listing_types=[], size=10000

    Args:
        filter_params(dict): Dictionary with search parameters
    """
    user_string = filter_params.get('search', '')

    # Pagination
    user_offset = filter_params.get('offset', 0)
    user_limit = filter_params.get('limit', 100)  # Size
    # user_limit_set = filter_params.get('limit_set', False)

    # Filtering
    categories = filter_params.get('categories', [])
    agencies = filter_params.get('agencies', [])
    listing_types = filter_params.get('listing_types', [])

    # Default Filter - A Listing needs to enabled, not deleted, and approved
    filter_data = [
        {
          "query": {
            "term": {
              "is_deleted": 0
            }
          }
        },
        {
          "query": {
            "term": {
              "is_enabled": 1
            }
          }
        },
        {
          "query": {
            "match": {
              "approval_status": "APPROVED"
            }
          }
        }
    ]

    if agencies:
        should_data = []

        for agency_title in agencies:
            current_agency_data = {
                "match": {
                    "agency_short_name": agency_title
                }
            }
            should_data.append(current_agency_data)

        agencies_data = {
            "query": {
                "bool": {
                    "should": should_data
                    }
                }
        }

        filter_data.append(agencies_data)

    if exclude_agencies:
        agencies_must_not_data = []

        for exclude_agency_short_name in exclude_agencies:

            temp_filter = {
              "bool": {
                "filter": [
                  {
                    "match": {
                      "agency_short_name": exclude_agency_short_name
                    }
                  },
                  {
                    "match": {
                      "is_private": 1
                    }
                  }
                ]
              }
            }

            agencies_must_not_data.append(temp_filter)

        agencies_query_data = {
            "query": {
                "bool": {
                    "must_not": agencies_must_not_data
                }
            }
        }

        filter_data.append(agencies_query_data)

    if listing_types:
        should_data = []

        for listing_type_title in listing_types:
            current_listing_type_data = {
                "match": {
                    "listing_type_title": listing_type_title
                }
            }
            should_data.append(current_listing_type_data)

        listing_type_data = {
            "query": {
                "bool": {
                    "should": should_data
                }
            }
        }
        filter_data.append(listing_type_data)

    if categories:
        should_data = []

        for category in categories:
            current_category_data = {
                "match": {
                    "categories.title": category
                }
            }
            should_data.append(current_category_data)

        categories_data = {
            "nested": {
                "boost": 1,
                "path": "categories",
                "query": {
                    "bool": {
                        "should": should_data
                    }
                }
            }
        }

        filter_data.append(categories_data)

    search_query = {
      "size": user_limit,
      "min_score": min_score,
      "query": {
        "bool": {
          "should": [
            {
              "match": {
                "title": {
                  "query": user_string,
                  "boost": 10
                }
              }
            },
            {
              "match": {
                "description": {
                  "query": user_string,
                  "boost": 2
                }
              }
            },
            {
              "match": {
                "description_short": {
                  "query": user_string,
                  "boost": 2
                }
              }
            },
            {
              "nested": {
                "boost": 1,
                "query": {
                  "query_string": {
                    "fields": [
                      "tags.name"
                    ],
                    "query": user_string
                  }
                },
                "path": "tags"
              }
            }
          ],
          "filter": filter_data
        }
      }
    }

    if user_offset:
        search_query['from'] = user_offset

    return search_query


def filter_listings(username, filter_params):
    """
    Filter Listings

    It must respects restrictions
     - Private apps (apps only from user's agency)
     - User's max_classification_level

    Search Fields - user_search_input
     - title
     - description
     - description_short
     - tags__name

    Filter_params can contain - filter_params
        * List of category names (OR logic)
        * List of agencies (OR logic)
        * List of listing types (OR logic)

    Too many variations to cache

    Args:
        username(str): username
        user_search_input: user provided search keywords
        filter_params({}):
            categories = self.request.query_params.getlist('category', False)
            agencies = self.request.query_params.getlist('agency', False)
            listing_types = self.request.query_params.getlist('type', False)
    """
    user = models.Profile.objects.get(user__username=username)

    # Filter out private listings - private apps (apps only from user's agency) requirement
    if user.highest_role() == 'APPS_MALL_STEWARD':
        exclude_orgs = []
    elif user.highest_role() == 'ORG_STEWARD':
        user_orgs = user.stewarded_organizations.all()
        user_orgs = [i.title for i in user_orgs]
        exclude_orgs = models.Agency.objects.exclude(title__in=user_orgs)
    else:
        user_orgs = user.organizations.all()
        user_orgs = [i.title for i in user_orgs]
        exclude_orgs = models.Agency.objects.exclude(title__in=user_orgs)

    print(exclude_orgs)
    # exclude_orgs is availble

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
