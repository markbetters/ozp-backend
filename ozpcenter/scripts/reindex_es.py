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
        # Clean Record
        for key in keys_to_remove:
            if key in record:
                del record[key]

        del record['agency']['icon']

        record_clean_obj = json.loads(json.dumps(record))

        # Sample Record (record_json)
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
        "settings" : {
            "number_of_shards": 1,
            "number_of_replicas": 0
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
