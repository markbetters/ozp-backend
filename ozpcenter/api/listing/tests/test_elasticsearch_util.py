"""
Elasticsearch Utils tests

Test this class indiviual with command:
python manage.py test ozpcenter.api.listing.tests.test_elasticsearch_util
"""
from unittest import skip
from django.test import TestCase

from ozpcenter.scripts import sample_data_generator as data_gen
from ozpcenter.api.listing import elasticsearch_util


class ElasticsearchUtilTest(TestCase):

    def setUp(self):
        """
        setUp is invoked before each test method
        """
        pass

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the whole TestCase (only run once for the TestCase)
        """
        data_gen.run()
        # elasticsearch_util.

    def test_get_mapping_setting_obj(self):
        mapping_obj = elasticsearch_util.get_mapping_setting_obj()
        self.assertTrue('settings' in mapping_obj)

    def test_encode_special_characters(self):
        actual_string = elasticsearch_util.encode_special_characters('Air^Por>')
        expected_string = 'Air\\^Por\\>'
        self.assertEquals(actual_string, expected_string)

        actual_string = elasticsearch_util.encode_special_characters(None)
        expected_string = ''
        self.assertEquals(actual_string, expected_string)

    @skip("TODO Finish (rivera 20161207)")
    def test_prepare_clean_listing_record(self):
        raw_record = {}
        clean_record = elasticsearch_util.prepare_clean_listing_record(raw_record)
        self.assertTrue('settings' in clean_record)

    @skip("TODO Finish (rivera 20161207)")
    def test_make_search_query_obj(self):
        expected = {
          "min_score": 0.4,
          "query": {
            "bool": {
              "should": [{
                  "match": {
                    "title": {
                      "query": "Clipboard",
                      "boost": 10
                    }}},
                {"match": {
                    "description": {
                      "query": "Clipboard",
                      "boost": 3
                    }}},
                {"match": {
                    "description_short": {
                      "query": "Clipboard",
                      "boost": 3
                    }}},
                {"nested": {
                    "boost": 1,
                    "query": {
                      "query_string": {
                        "query": "Clipboard",
                        "fields": [
                          "tags.name"
                        ]
                      }},
                    "path": "tags"
                  }}],
              "filter": [
                {"query": {
                    "term": {
                      "is_deleted": 0
                    }}},
                {"query": {
                    "term": {
                      "is_enabled": 1
                    }}},
                {"query": {"match": {
                    "approval_status": "APPROVED"
                    }}},
                {"query": {"bool": {
                    "should": [
                        {"match": {
                            "agency_short_name": "Minitrue"
                          }},
                        {"match": {
                            "agency_short_name": "Miniluv"
                          }}
                      ]}}},
                {"query": {
                    "bool": {
                      "must_not": [
                        {"bool": {
                            "filter": [
                              {
                                "match": {
                                  "agency_short_name": "Minipax"
                                }
                              },
                              {
                                "match": {
                                  "is_private": 1
                                }
                              }
                            ]
                          }
                        },
                        {"bool": {
                            "filter": [{
                                "match": {
                                  "agency_short_name": "Minitrue"
                                }
                              },
                              {
                                "match": {
                                  "is_private": 1
                                }
                              }
                            ]}},
                        {
                          "bool": {
                            "filter": [
                              {
                                "match": {
                                  "agency_short_name": "Ministry of Plenty"
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
                      ]
                    }
                  }
                },
                {
                  "query": {
                    "bool": {
                      "should": [
                        {
                          "match": {
                            "listing_type_title": "web application"
                          }
                        }
                      ]
                    }
                  }
                },
                {
                  "nested": {
                    "boost": 1,
                    "query": {
                      "bool": {
                        "should": [
                          {
                            "match": {
                              "categories.title": "Education"
                            }
                          }
                        ]
                      }
                    },
                    "path": "categories"
                  }
                }
              ]
            }
          },
          "size": 24
        }

        self.assertTrue('size' in expected)

    # TODO Add more test
