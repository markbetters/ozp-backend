"""
Reindex data script

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

************************************WARNING************************************
Running this script will delete existing data in elasticsearch
************************************WARNING************************************
"""
from PIL import Image
import datetime
import json
import os
import pytz
import sys

from elasticsearch import Elasticsearch

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../../')))

from django.contrib import auth
from django.conf import settings

from ozpcenter import models
from ozpcenter import model_access
from rest_framework import serializers
from rest_framework.response import Response
import json

TEST_IMG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_images') + '/'
DEMO_APP_ROOT = settings.OZP['DEMO_APP_ROOT']

# TODO: Put elasticsearch settings in settings.py
ES_HOST = {
    "host" : "localhost",
    "port" : 9200
}

INDEX_NAME = 'appsmall'
TYPE_NAME = 'listings'

ID_FIELD = 'id'


class ReadOnlyListingSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Listing
        depth = 2


def make_search_query_obj(user_string="", categories=[], agency=None, listing_type=None, size=10):
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

    if agency:
        agency_data = {
            "nested": {
              "path": "agency",
              "query": {
                "match": {
                  "agency.short_name": "Minitrue"
                }
              }
            }
         }
        filter_data.append(agency_data)

    if listing_type:
        listing_type_data = {
            "nested": {
              "path": "listing_type",
              "query": {
                "match": {
                  "listing_type.title": listing_type
                }
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
      "size": size,
      "query": {
        "bool": {
          "should": [
            {
              "match": {
                "title": {
                  "query": user_string,
                  "boost": 2
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
    return search_query



def search(user_string="", categories=[], agency=None, listing_type=None,size=10):
        search_query = make_search_query_obj()

        # sanity check
        print("searching...")
        res = es.search(index = INDEX_NAME, size=2, body=search_query)
        print(" response: '%s'" % (res))

        print("results:")
        for hit in res['hits']['hits']:
            print(hit["_source"])


def run():
    """
    Reindex Data
    """
    print('Starting Indexing Process')
    all_listings = models.Listing.objects.all()
    serializer = ReadOnlyListingSerializer(all_listings, many=True)
    serializer_results = serializer.data

    keys_to_remove = ['small_icons', 'contacts', 'last_activity',
                        'required_listings', 'large_icon', 'small_icon',
                        'banner_icon','large_banner_icon', 'owners',
                        'current_rejection', 'launch_url','what_is_new',
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
    es = Elasticsearch(hosts = [ES_HOST])

    if es.indices.exists(INDEX_NAME):
        print("deleting '%s' index..." % (INDEX_NAME))
        res = es.indices.delete(index = INDEX_NAME)
        print(" response: '%s'" % (res))

    request_body = {
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
              "dynamic":      "strict",
              "properties": {
                "id": {
                  "type": "long"
                },
                # Agency
                "agency": {
                  "type": "nested",
                  "properties": {
                    "id": {
                      "type": "long"
                    },
                    "short_name": {
                      "type": "string"
                    },
                    "title": {
                      "type": "string"
                    }
                  }
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
                  "type": "string"
                },
                "description_short": {
                  "type": "string"
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
                "listing_type": {
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
                      "type": "string"
                    }
                  }
                },
                "title": {
                  "type": "string",
                  "analyzer": "autocomplete",
                  "search_analyzer": "autocomplete"
                },
                # "title_suggest":{
                #   "type": "completion",
                #   #"index_analyzer": "simple",
                #   "analyzer": "autocomplete",
                #   "search_analyzer": "autocomplete",
                #   "payloads": False
                # },
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

    print("Creating '%s' index..." % (INDEX_NAME))
    res = es.indices.create(index = INDEX_NAME, body = request_body)
    print(" response: '%s'" % (res))

    # Bulk index the data
    print("Bulk indexing listings...")
    res = es.bulk(index = INDEX_NAME, body = bulk_data, refresh = True)
    # print(" response: '%s'" % (res))

    print("Done Indexing")
    # http://127.0.0.1:9200/appsmall/_search?size=10000&pretty

    print(json.dumps(make_search_query_obj(agency='Minitrue',
                                listing_type='web application',
                                categories=['Communication']),indent=2))
