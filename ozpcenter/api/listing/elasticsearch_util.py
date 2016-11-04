import json
import logging
import time

from elasticsearch import Elasticsearch

from ozpcenter import constants

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))

# Create ES client
es_client = Elasticsearch(hosts=[constants.ES_HOST])


def update_es_listing(current_listing_id, record, is_new):
    """
    Args:
        is_new: backend is new
    """
    if not es_client.ping():
        logger.warn('ElasticsearchServiceUnavailable')
        # raise errors.ElasticsearchServiceUnavailable()
    else:

        if not es_client.indices.exists(constants.ES_INDEX_NAME):
            request_body = get_mapping_setting_obj()

            print("Creating '%s' index..." % (constants.ES_INDEX_NAME))
            res = es_client.indices.create(index=constants.ES_INDEX_NAME, body=request_body)
            print(" response: '%s'" % (res))

            time.sleep(20)   # Seems like there needs to be a delay if not a 503 error will happen

        es_record_exist = es_client.exists(
            index=constants.ES_INDEX_NAME,
            doc_type=constants.ES_TYPE_NAME,
            id=current_listing_id,
            refresh=True
        )

        # print(es_record_exist)
        # print('is_new:%s, es_record_exist: %s , current_listing_id: %s'%(is_new, es_record_exist, current_listing_id))
        record_clean_obj = prepare_clean_listing_record(record)
        if is_new is not None:
            if es_record_exist:
                es_client.update(
                    index=constants.ES_INDEX_NAME,
                    doc_type=constants.ES_TYPE_NAME,
                    id=current_listing_id,
                    refresh=True,
                    body={"doc": record_clean_obj}
                )
            else:
                es_client.create(
                    index=constants.ES_INDEX_NAME,
                    doc_type=constants.ES_TYPE_NAME,
                    id=current_listing_id,
                    refresh=True,
                    body=record_clean_obj
                )
        else:
            if es_record_exist:
                es_client.update(
                    index=constants.ES_INDEX_NAME,
                    doc_type=constants.ES_TYPE_NAME,
                    id=current_listing_id,
                    refresh=True,
                    body={"doc": record_clean_obj}
                )
            else:
                # Ensure if doc exist in es, then update
                es_client.create(
                    index=constants.ES_INDEX_NAME,
                    doc_type=constants.ES_TYPE_NAME,
                    id=current_listing_id,
                    refresh=True,
                    body=record_clean_obj
                )


def get_mapping_setting_obj():
    """
    Mapping Object
    """
    data = {
        "settings": {
            # "refresh_interval" : 5,
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


def make_search_query_obj(filter_params, exclude_agencies=[], min_score=0.4):
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


def prepare_clean_listing_record(record):
    """
    Clean Record

    # Sample Record (record_json) after clean

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

    Args:
        record: One record of ReadOnlyListingSerializer
    """
    keys_to_remove = ['small_icons', 'contacts', 'last_activity',
                      'required_listings', 'large_icon', 'small_icon',
                      'banner_icon', 'large_banner_icon', 'owners',
                      'current_rejection', 'launch_url', 'what_is_new',
                      'iframe_compatible', 'approved_date',
                      'edited_date', 'version_name', 'requirements',
                      'intents']

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
    return record_clean_obj
