"""
Recommendations Engine
===============
Business Objective:
To recommend applications to users that they might find useful in their everyday objectives

Website Link: https://github.com/aml-development/ozp-documentation/wiki/Recommender-%282017%29

Data that could be used for recommendations
- Listing Bookmarked
- Keep track of folder apps

Recommendations are based on individual users

Assumptions:
    45,000 Users
    350 Listings

Worst Case Number of Recommendations = 15,750,000

Steps:
    - Load Data for each users
    - Process Data with recommendation algorthim
      - Produces a list of listing's id for each profile = Results
    - Iterate through the Results to call add_listing_to_user_profile function

Idea:
Jitting Result
"""
import logging
import time

import msgpack
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.db import transaction
from django.conf import settings

from ozpcenter import models
from ozpcenter.recommend import recommend_utils
from ozpcenter.recommend.graph_factory import GraphFactory
from ozpcenter.api.listing.elasticsearch_util import elasticsearch_factory

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class Recommender(object):
    """
    This class is to behave like a superclass for recommendation engine
    """
    friendly_name = None
    recommendation_weight = None

    def __init__(self):
        self.recommender_result_set = {}
        self.initiate()

    def initiate(self):
        """
        This method is used for the subclasses
        It is used for initiating variables, classes, objects, connecting to service
        """
        raise NotImplementedError()

    def recommendation_logic(self):
        """
        This method is used for the subclasses.
        It is used for put the recommendation logic
        """
        raise NotImplementedError()

    def add_listing_to_user_profile(self, profile_id, listing_id, score, cumulative=False):
        """
        Add listing and score to user profile

        recommender_result_set: Dictionary with profile id, nested listing id with score pairs
            {
                profile_id#1: {
                    listing_id#1: score#1,
                    listing_id#2: score#2
                },
                profile_id#2: {
                    listing_id#1: score#1,
                    listing_id#2: score#2,
                    listing_id#3: score#3,
                }
            }
        """
        if profile_id in self.recommender_result_set:
            if self.recommender_result_set[profile_id].get(listing_id):
                if cumulative:
                    self.recommender_result_set[profile_id][listing_id] = self.recommender_result_set[profile_id][listing_id] + float(score)
                else:
                    self.recommender_result_set[profile_id][listing_id] = float(score)
            else:
                self.recommender_result_set[profile_id][listing_id] = float(score)
        else:
            self.recommender_result_set[profile_id] = {}
            self.recommender_result_set[profile_id][listing_id] = float(score)

    def recommend(self):
        """
        Execute recommendation logic
        """
        start_ms = time.time() * 1000.0
        self.recommendation_logic()
        recommendation_ms = time.time() * 1000.0
        print('--------')  # Print statement for debugging output
        logger.info(self.recommender_result_set)
        print('--------')  # Print statement for debugging output
        logger.info('Recommendation Logic took: {} ms'.format(recommendation_ms - start_ms))
        return self.recommender_result_set


class SampleDataRecommender(Recommender):
    """
    Sample Data Recommender
    """
    friendly_name = 'Sample Data Gen'
    recommendation_weight = 0.5

    def initiate(self):
        """
        Initiate any variables needed for recommendation_logic function
        """
        pass

    def recommendation_logic(self):
        """
        Sample Recommendations for all users
        """
        all_profiles = models.Profile.objects.all()
        for profile in all_profiles:
            # Assign Recommendations
            # Get Listings this user can see
            current_listings = None
            try:
                current_listings = models.Listing.objects.for_user(profile.user.username)[:10]
            except ObjectDoesNotExist:
                current_listings = None

            if current_listings:
                for current_listing in current_listings:
                    self.add_listing_to_user_profile(profile.id, current_listing.id, 1.0)


class BaselineRecommender(Recommender):
    """
    Baseline Recommender

    Assumptions:
    - Listing has ratings and possible not to have ratings
    - Listing can be featured
    - User bookmark Listings
    - User have bookmark folder, a collection of listing in a folder.
    - Listing has total_reviews field

    Requirements:
    - Recommendations should be explainable and believable
    - Must respect private apps
    - Does not have to repect security_marking while saving to db
    """
    friendly_name = 'Baseline'
    recommendation_weight = 1.0

    def initiate(self):
        """
        Initiate any variables needed for recommendation_logic function
        """
        pass

    def recommendation_logic(self):
        """
        Sample Recommendations for all users
        """
        all_profiles = models.Profile.objects.all()
        all_profiles_count = all_profiles.count()

        current_profile_count = 0
        for profile in all_profiles:
            current_profile_count = current_profile_count + 1
            logger.info('Calculating Profile {}/{}'.format(current_profile_count, all_profiles_count))

            profile_id = profile.id
            profile_username = profile.user.username
            # Get Featured Listings
            featured_listings = models.Listing.objects.for_user_organization_minus_security_markings(
                profile_username).order_by('-approved_date').filter(
                    is_featured=True,
                    approval_status=models.Listing.APPROVED,
                    is_enabled=True,
                    is_deleted=False)[:36]

            for current_listing in featured_listings:
                self.add_listing_to_user_profile(profile_id, current_listing.id, 3.0, True)

            # Get Recent Listings
            recent_listings = models.Listing.objects.for_user_organization_minus_security_markings(
                profile_username).order_by(
                    '-approved_date').filter(
                        is_featured=False,
                        approval_status=models.Listing.APPROVED,
                        is_enabled=True,
                        is_deleted=False)[:36]

            for current_listing in recent_listings:
                self.add_listing_to_user_profile(profile_id, current_listing.id, 2.0, True)

            # Get most popular listings via a weighted average
            most_popular_listings = models.Listing.objects.for_user_organization_minus_security_markings(
                profile_username).filter(
                    approval_status=models.Listing.APPROVED,
                    is_enabled=True,
                    is_deleted=False).order_by('-avg_rate', '-total_reviews')[:36]

            for current_listing in most_popular_listings:
                if current_listing.avg_rate != 0:
                    self.add_listing_to_user_profile(profile_id, current_listing.id, current_listing.avg_rate, True)

            # Get most popular bookmarked apps for all users
            # Would it be faster it this code was outside the loop for profiles?
            library_entries = models.ApplicationLibraryEntry.objects.for_user_organization_minus_security_markings(profile_username)
            library_entries = library_entries.filter(listing__is_enabled=True)
            library_entries = library_entries.filter(listing__is_deleted=False)
            library_entries = library_entries.filter(listing__approval_status=models.Listing.APPROVED)
            library_entries_group_by_count = library_entries.values('listing_id').annotate(count=Count('listing_id')).order_by('-count')
            # [{'listing_id': 1, 'count': 1}, {'listing_id': 2, 'count': 1}]

            # Calculation of Min and Max new scores dynamically.  This will increase the values that are lower
            # to a range within 2 and 5, but will not cause values higher than new_min and new_max to become even
            # larger.
            old_min = 1
            old_max = 1
            new_min = 2
            new_max = 5

            for entry in library_entries_group_by_count:
                count = entry['count']
                if count == 0:
                    continue
                if count > old_max:
                    old_max = count
                if count < old_min:
                    old_min = count

            for entry in library_entries_group_by_count:
                listing_id = entry['listing_id']
                count = entry['count']

                calculation = recommend_utils.map_numbers(count, old_min, old_max, new_min, new_max)
                self.add_listing_to_user_profile(profile_id, listing_id, calculation, True)


class ElasticsearchRecommender(Recommender):
    """
    Elasticsearch methods to create mappings, populate data, and run core recommendation queries for both Content and
    Collaborative based recommendations.  This is meant to be in a fashion so that it will also allow for execution
    from outside in other classes.  Thus will then facilitate a realtime execution when needed.
    """
    # Static Contstant to get ratings greater than this value entered into ES User Profile Table:
    MIN_ES_RATING = 3.5
    WAIT_TIME = 30  # Wait time in Minutes before running recreation of index
    TIMESTAMP_INDEX_TYPE = 'custom_meta'

    @staticmethod
    def set_timestamp_record():
        """
        Method to set timestamp for creation and last update of ES Recommendation Table data
        """
        es_client = elasticsearch_factory.get_client()

        index_name = settings.ES_RECOMMEND_USER
        timestamp = time.time()
        result_es = None

        if es_client.indices.exists(index_name):
            result_es = es_client.create(
                index=settings.ES_RECOMMEND_USER,
                doc_type=ElasticsearchRecommender.TIMESTAMP_INDEX_TYPE,
                id=0,
                refresh=True,
                body={
                    "lastupdated": timestamp
                }
            )

        return result_es

    @staticmethod
    def is_data_old():
        """
        Method to determine if the ES Recommendation Table data is out of date and needs to be recreated
        """
        # time.time() returns time in seconds since epoch.  To convert wait time to seconds need to multiply
        # by 60.  REF: https://docs.python.org/3/library/time.html
        trigger_recreate = ElasticsearchRecommender.WAIT_TIME * 60
        es_client = elasticsearch_factory.get_client()

        query_es_date = {
            "query": {
                "term": {
                    "_type": "custom_meta"
                }
            }
        }

        if es_client.indices.exists(settings.ES_RECOMMEND_USER):
            result_es = es_client.search(
                index=settings.ES_RECOMMEND_USER,
                body=query_es_date
            )
        else:
            # There is no index created and need to create one, return True to do so:
            logger.info("== ES Table Does not exist, create a new one ==")
            return True

        if result_es['hits']['total'] == 0:
            lastupdate = 0
        else:
            lastupdate = result_es['hits']['hits'][0]['_source']['lastupdated']
        currenttime = time.time()
        logger.info("== ES Table Last Update: {}, Current Time: {}, Recreate Index: {} ==".format(currenttime, lastupdate, ((currenttime - lastupdate) > trigger_recreate)))
        if (currenttime - lastupdate) > trigger_recreate:
            return True
        else:
            return False

    @staticmethod
    def get_index_mapping():
        """
        Mapping to be used for Elasticsearch Table for both Content and Collaborative Recommendation Engines
        """
        number_of_shards = settings.ES_NUMBER_OF_SHARDS
        number_of_replicas = settings.ES_NUMBER_OF_REPLICAS

        index_mapping = {
            "settings": {
                "number_of_shards": number_of_shards,
                "number_of_replicas": number_of_replicas,
                "analysis": {
                    "analyzer": {
                       "keyword_lowercase_analyzer": {
                         "tokenizer": "keyword",
                         "filter": ["lowercase"]
                       }
                     }
                }
            },
            "mappings": {
                "custom_meta": {
                    "dynamic": "strict",
                    "properties": {
                        "lastupdated": {
                            "type": "long"
                        }
                    }
                },
                "recommend": {
                    "dynamic": "strict",
                    "properties": {
                        "author_id": {
                            "type": "long"
                        },
                        "author": {
                            "type": "string",
                            "analyzer": "english"
                        },
                        "titles": {
                            "type": "string",
                            "analyzer": "english"
                        },
                        "descriptions": {
                            "type": "string",
                            "analyzer": "english"
                        },
                        "description_shorts": {
                            "type": "string",
                            "analyzer": "english"
                        },
                        "agency_short_name": {
                            "type": "string",
                            "analyzer": "english"
                        },
                        "tags": {
                            "type": "string",
                            "analyzer": "english"
                        },
                        "categories_text": {
                            "type": "string",
                            "analyzer": "keyword_lowercase_analyzer"
                        },
                        "ratings": {
                            "type": "nested",
                            "properties": {
                                "listing_id": {
                                    "type": "long"
                                },
                                "rate": {
                                    "type": "long",
                                    "boost": 1
                                },
                                "listing_categories": {
                                    "type": "string",
                                    "analyzer": "keyword_lowercase_analyzer"
                                },
                                "category_ids": {
                                    "type": "long"
                                }
                            }
                        },
                        "bookmark_ids": {
                            "type": "long"
                        },
                        "categories_id": {
                            "type": "long"
                        }
                    }
                }
            }
        }
        return index_mapping

    def initiate(self):
        """
        Make sure the Elasticsearch is up and running
        Making profiles for Elasticsearch Recommendations
        """
        elasticsearch_factory.check_elasticsearch()

        if ElasticsearchRecommender.is_data_old():
            elasticsearch_factory.recreate_index_mapping(settings.ES_RECOMMEND_USER, ElasticsearchRecommender.get_index_mapping())
            ElasticsearchRecommender.load_data_into_es_table()

    @staticmethod
    def load_data_into_es_table():
        """
        - Get Mapping for Elasticsearch Table
        - Cycle through all profiles:
            - For each profile:
                Get Reviewed Listings with Categories, Title, Description, and Description Short Text
                Get Bookmarked Listings with Categories, Title, Description, and Description Short Text
                Add information to Elasticsearch Table for profile
        - Set timestamp for data creation
        """
        es_client = elasticsearch_factory.get_client()

        all_profiles = models.Profile.objects.all()

        data_to_bulk_index = []
        for profile in all_profiles:
            profile_username = profile.user.username

            title_text_list = set()
            description_text_list = set()
            description_short_text_list = set()
            categories_text_list = set()
            category_id_list = set()
            tags_text_list = set()

            profile_listings_review = []
            for review_object in models.Review.objects.filter(author=profile.user_id):
                listing_obj = review_object.listing

                if review_object.rate > ElasticsearchRecommender.MIN_ES_RATING:
                    title_text_list.add(listing_obj.title)
                    description_text_list.add(listing_obj.description)
                    description_short_text_list.add(listing_obj.description_short)

                for tagitem in listing_obj.tags.all():
                    tags_text_list.add(tagitem.name)

                listing_categories = set()
                listing_category_id_list = set()
                for cat_item in review_object.listing.categories.all():
                    listing_categories.add(cat_item.title)
                    listing_category_id_list.add(cat_item.id)
                    categories_text_list.add(cat_item.title)
                    category_id_list.add(cat_item.id)

                update_item = {"listing_id": review_object.listing_id,
                               "rate": review_object.rate,
                               "listing_categories": list(categories_text_list),
                               "category_ids": list(listing_category_id_list)}
                profile_listings_review.append(update_item)

            bookmarked_id_list = []
            for bookmark_item in models.ApplicationLibraryEntry.objects.for_user(profile.user.username):
                bookmarked_listing_obj = bookmark_item.listing
                bookmarked_id_list.append(bookmarked_listing_obj.id)
                title_text_list.add(bookmarked_listing_obj.title)
                description_text_list.add(bookmarked_listing_obj.description)
                description_short_text_list.add(bookmarked_listing_obj.description_short)

                for cat_item in bookmarked_listing_obj.categories.all():
                    categories_text_list.add(cat_item.title)

                for tagitem in bookmarked_listing_obj.tags.all():
                    tags_text_list.add(tagitem.name)

            data_to_bulk_index.append({"author_id": profile.user_id,
                "author": profile_username,
                "titles": list(title_text_list),
                "descriptions": list(description_text_list),
                "description_shorts": list(description_short_text_list),
                "tags": list(tags_text_list),
                "categories_text": list(categories_text_list),
                "bookmark_ids": list(bookmarked_id_list),
                "categories_id": list(category_id_list),
                "ratings": profile_listings_review})

        # TODO data_to_bulk_index = [1..19500] > [[1..5000],[5001..10000], .., [15001..19500]]
        bulk_data = []
        for record in data_to_bulk_index:
            op_dict = {
                "index": {
                    "_index": settings.ES_RECOMMEND_USER,
                    "_type": settings.ES_RECOMMEND_TYPE,
                    "_id": record['author_id']
                }
            }

            bulk_data.append(op_dict)
            bulk_data.append(record)

        # Bulk index the data
        logger.info('Bulk indexing Users...')
        res = es_client.bulk(index=settings.ES_RECOMMEND_USER, body=bulk_data, refresh=True)
        if res.get('errors', True):
            logger.error('Error Bulk Recommendation Indexing')
        else:
            logger.info('Bulk Recommendation Indexing Successful')

        logger.info("Done Indexing")

        ElasticsearchRecommender.set_timestamp_record()


class ElasticsearchContentBaseRecommender(ElasticsearchRecommender):
    """
    Elasticsearch Content based recommendation engine
    Steps:
    - Initialize Mappings by calling common Utils command to create table if it has not already been created recently
    - Import listings into main Elasticsearch table (if not already created recently)
        - Cycle through all reviews and add information to table (including text)
            - Add rating that the user given
        - Add all users that have bookmarked the app to the table
        - Go through User tables and add text to each record of a User Table
    - Perform calculations via query on data
    """
    friendly_name = 'Elasticsearch Content Filtering'
    recommendation_weight = 0.9  # Weighting is based on rebasing the results
    result_size = 20  # Get only the top 50 results
    min_new_score = 4  # Min value to set for rebasing of results
    max_new_score = 9  # Max value to rebase results to so that values
    content_norm_factor = 0.05  # Amount to increase the max value found so that saturation does not occur.

    def es_content_based_recommendation(self, profile_id, result_size):
        """
        Recommendation Logic for Content Based Recommendations:

        Recommendation logic
        - Take profile passed in and SIZE of result set requested
        - Get information from profile to match against listings
        - Exclude apps that are already in the profile
        - Perform search based on queries and return results
        - Return list of recommended items back to calling method for the profile
        """
        es_client = elasticsearch_factory.get_client()

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"author_id": profile_id}}
                    ]
                }
            }
        }

        es_profile_result = es_client.search(
            index=settings.ES_RECOMMEND_USER,
            body=query
        )

        each_profile_source = es_profile_result['hits']['hits'][0]['_source']

        query_object = []

        categories_to_query = {
            "nested": {
                "path": "categories",
                "query": {
                    "bool": {
                        "should": [
                            {"terms": {"categories.id": each_profile_source['categories_id']}}
                        ]
                    }
                }
            }
        }
        query_object.append(categories_to_query)

        title_list = {}
        for items in each_profile_source['titles']:
            title_list = {
                "multi_match": {
                    "query": items,
                    "type": "cross_fields",
                    "fields": ["title", "description", "description_short"],
                    "minimum_should_match": "20%"
                }
            }
            query_object.append(title_list)

        description_list = {}
        for items in each_profile_source['descriptions']:
            description_list = {
                "multi_match": {
                    "query": items,
                    "type": "cross_fields",
                    "fields": ["title", "description", "description_short"],
                    "minimum_should_match": "20%"
                }
            }
            query_object.append(description_list)

        description_short_list = {}
        for items in each_profile_source['description_shorts']:
            description_short_list = {
                "multi_match": {
                    "query": items,
                    "type": "cross_fields",
                    "fields": ["title", "description", "description_short"],
                    "minimum_should_match": "20%"
                }
            }
            query_object.append(description_short_list)

        rated_apps_list = list([rate['listing_id'] for rate in each_profile_source['ratings']])

        query_compare = {
            "size": result_size,
            "_source": ["id", "title"],
            "query": {
                "bool": {
                    "must_not": {
                        # id is the id of the listing when it searches the listings:
                        "terms": {"id": each_profile_source['bookmark_ids']},
                        "terms": {"id": rated_apps_list}
                    },
                    "should": [
                        query_object
                    ]
                }
            }
        }

        es_query_result = es_client.search(
            index=settings.ES_INDEX_NAME,
            body=query_compare
        )

        return es_query_result

    def new_user_return_list(self, result_size):
        """
        This procedure is a uses all profile contents to create recommendations for a new user.
        RETURN: The procedure will return a query results of applications matching query of result_size to be used for
                populating new user recommendations.
        """
        es_client = elasticsearch_factory.get_client()
        title_to_search_list = []

        content_search_term = {
            "size": 0,
            "aggs": {
                "most_common_titles": {
                    "significant_terms": {
                        "field": "titles"
                    }
                }
            }
        }

        es_content_init = es_client.search(
            index=settings.ES_RECOMMEND_USER,
            body=content_search_term
        )

        for item_key in es_content_init['aggregations']['most_common_titles']['buckets']:
            title_to_search_list_item = {
                "multi_match": {
                    "query": item_key['key'],
                    "type": "cross_fields",
                    "fields": ["title", "description", "description_short"],
                    "minimum_should_match": "20%"
                }
            }
            title_to_search_list.append(title_to_search_list_item)

        query_compare = {
            "size": result_size,
            "_source": ["id", "title"],
            "query": {
                "bool": {
                    "should": title_to_search_list
                }
            }
        }

        es_query_result = es_client.search(
            index=settings.ES_INDEX_NAME,
            body=query_compare
        )

        return es_query_result

    def recommendation_logic(self):
        """
        Recommendation logic is where the use of Collaborative vs Content differ.  Both use the User Profile to get
        infromation on the user, but with Content, it takes the content from user profiles on apps based on criteria
        that is implemented in the calling method and gets a recommended list of apps to return to the user as
        recommendations.
        The list is then normalized and added to the recommendations database.
        """
        logger.info('= Elasticsearch Content Base Recommendation Engine= ')
        all_profiles = models.Profile.objects.all()
        all_profiles_count = all_profiles.count()

        performed_search_request = False
        new_user_return_list = []
        current_profile_count = 0

        for profile in all_profiles:
            current_profile_count = current_profile_count + 1
            profile_id = profile.id
            es_query_result = self.es_content_based_recommendation(profile_id, self.result_size)

            # Check if results returned are returned or if it is empty (New User):
            if es_query_result['hits']['total'] == 0:
                if not performed_search_request:
                    new_user_return_list = self.new_user_return_list(int(self.result_size / 2))
                    performed_search_request = True

                recommended_items = new_user_return_list['hits']['hits']
                max_score_es_content = new_user_return_list['hits']['max_score'] + self.content_norm_factor * new_user_return_list['hits']['max_score']
            else:
                recommended_items = es_query_result['hits']['hits']
                max_score_es_content = es_query_result['hits']['max_score'] + self.content_norm_factor * es_query_result['hits']['max_score']

            for indexitem in recommended_items:
                score = recommend_utils.map_numbers(indexitem['_score'], 0, max_score_es_content, self.min_new_score, self.max_new_score)
                itemtoadd = indexitem['_source']['id']
                self.add_listing_to_user_profile(profile_id, itemtoadd, score, False)
            logger.info("= ES CONTENT RECOMMENDER Engine Completed Results for {}/{} =".format(current_profile_count, all_profiles_count))

        logger.info("= ES CONTENT RECOMMENDATION Results Completed =")


class ElasticsearchUserBaseRecommender(ElasticsearchRecommender):
    """
    Elasticsearch User based recommendation engine
    Steps:
       - Perform aggregations on data to obtain recommendation list
       - Need to ensure that user apps and bookmarked apps are not in list
       - Output with query and put into recommendation table:
    """
    friendly_name = 'Elasticsearch User Based Filtering'
    recommendation_weight = 1.0  # Weight that the overall results are multiplied against.  The rating for user based is less than 1.
    min_new_score = 5  # Min value to set for rebasing of results
    max_new_score = 10  # Max value to rebase results to so that values

    def es_user_based_recommendation(self, profile_id):
        """
        Recommendation Logic for Collaborative/User Based Recommendations:
        Recommendation logic
        - Take profile id passed in
        - Get User Profile information based on id
        - Get Categories, Bookmarks, Rated Apps (all and ones only greater than MIN_ES_RATING)
        - Compose Query to match profile of bookmarked and rated apps, but remove apps that have been
          identified by user already.
        - Perform ES Query and get the aggregations that have all of the apps already identified by the user
          removed.
        - Return list of recommended items back to calling method
        """
        AGG_LIST_SIZE = 50  # Default is 10 if parameter is left out of query.

        es_client = elasticsearch_factory.get_client()
        es_profile_search = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"author_id": profile_id}}
                    ],
                }
            }
        }

        es_search_result = es_client.search(
            index=settings.ES_RECOMMEND_USER,
            body=es_profile_search
        )

        agg_query_term = {}
        categories_to_match = es_search_result['hits']['hits'][0]['_source']['categories_id']
        bookmarks_to_match = es_search_result['hits']['hits'][0]['_source']['bookmark_ids']
        rated_apps_list = list([rate['listing_id'] for rate in es_search_result['hits']['hits'][0]['_source']['ratings']])
        rated_apps_list_match = list([rate['listing_id'] for rate in es_search_result['hits']['hits'][0]['_source']['ratings'] if rate['rate'] > ElasticsearchRecommender.MIN_ES_RATING])

        agg_query_term = {
            "constant_score": {
                "filter": {
                    "bool": {
                        "should": [
                            {"terms": {"bookmark_ids": bookmarks_to_match}},
                            {"terms": {"categories": categories_to_match}},
                            {
                                "nested": {
                                    "path": "ratings",
                                    "query": {
                                        "bool": {
                                            "should": [
                                                {"terms": {"ratings.listing_id": bookmarks_to_match}},
                                                {"terms": {"ratings.listing_id": rated_apps_list_match}}
                                            ]
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }

        agg_search_query = {
            "size": 0,
            "query": agg_query_term,
            "aggs": {
                "the_listing": {
                    "nested": {
                        "path": "ratings"
                    },
                    "aggs": {
                        "listings": {
                            "filter": {
                                "range": {
                                    "ratings.rate": {
                                        "gte": ElasticsearchRecommender.MIN_ES_RATING
                                    }
                                }
                            }
                        },
                        "aggs": {
                            "significant_terms": {
                                "field": "ratings.listing_id",
                                "exclude": bookmarks_to_match + rated_apps_list,
                                "min_doc_count": 1,
                                "size": AGG_LIST_SIZE
                            }
                        }
                    }
                }
            }
        }

        es_query_result = es_client.search(
            index=settings.ES_RECOMMEND_USER,
            body=agg_search_query
        )

        recommended_items = es_query_result['aggregations']['the_listing']['aggs']['buckets']

        return recommended_items

    def recommendation_logic(self):
        """
        Recommendation logic is where the use of Collaborative vs Content differ.  Both use the User Profile to get
        infromation on the user, but with Collaborative, it then matches against other users that have similar profiles to
        return a recommendation.

        Recommendation logic
        - Cycle through each profile:
            - Call ESRecommendUtils method to get User based Recommendations
            - Take max score from results for profile and rebase all results while adding them to the recommendation list
            - For each recommendation add it to the list while rescalling the score based on the max score returned
        """
        logger.info('= Elasticsearch User Base Recommendation Engine =')

        # Retreive all of the profiles from database:
        all_profiles = models.Profile.objects.all()
        all_profiles_count = all_profiles.count()

        current_profile_count = 0
        for profile in all_profiles:
            current_profile_count = current_profile_count + 1

            profile_id = profile.id
            recommended_items = self.es_user_based_recommendation(profile_id)

            # If a recommendaiton list is returned then get the max score,
            # otherwise it is a new user or there is no profile to base recommendations on:
            if recommended_items:
                max_score_es_user = recommended_items[0]['score']

            for indexitem in recommended_items:
                score = recommend_utils.map_numbers(indexitem['score'], 0, max_score_es_user, self.min_new_score, self.max_new_score)
                self.add_listing_to_user_profile(profile_id, indexitem['key'], score, False)

            logger.info("= ES USER RECOMMENDER Engine Completed Results for {}/{} =".format(current_profile_count, all_profiles_count))
        logger.info("= ES USER RECOMMENDATION Results Completed =")


class GraphCollaborativeFilteringBaseRecommender(Recommender):
    """
    Graph Collaborative Filtering based on Bookmarkes
    """
    friendly_name = 'Bookmark Collaborative Filtering'
    recommendation_weight = 5.0

    def initiate(self):
        """
        Initiate any variables needed for recommendation_logic function
        """
        pass

    def recommendation_logic(self):
        """
        Recommendation logic
        """
        all_profiles = models.Profile.objects.all()
        all_profiles_count = all_profiles.count()

        graph = GraphFactory.load_db_into_graph()

        current_profile_count = 0
        for profile in all_profiles:
            current_profile_count = current_profile_count + 1
            logger.info('Calculating Profile {}/{}'.format(current_profile_count, all_profiles_count))

            profile_id = profile.id

            results = graph.algo().recommend_listings_for_profile('p-{}'.format(profile_id))  # bigbrother

            for current_tuple in results:
                listing_raw = current_tuple[0]  # 'l-#'
                listing_id = int(listing_raw.split('-')[1])
                score = current_tuple[1]

                # No need to rebase since results are within the range of others based on testing:
                self.add_listing_to_user_profile(profile_id, listing_id, score)


# Method is decorated with @transaction.atomic to ensure all logic is executed in a single transaction
@transaction.atomic
def bulk_recommendations_saver(recommendation_entries):
    # Loop over each store and invoke save() on each entry
    for recommendation_entry in recommendation_entries:
        target_profile = recommendation_entry['target_profile']
        recommendation_data = recommendation_entry['recommendation_data']

        try:
            obj = models.RecommendationsEntry.objects.get(target_profile=target_profile)
            obj.recommendation_data = recommendation_data
            obj.save()
        except models.RecommendationsEntry.DoesNotExist:
            obj = models.RecommendationsEntry(target_profile=target_profile, recommendation_data=recommendation_data)
            obj.save()


class RecommenderDirectory(object):
    """
    Wrapper for all Recommenders
    It maps strings to classes.

    recommender_result_set
    {
        profile_id#1: {
            recommender_friendly_name#1:{
                recommendations:[
                    [listing_id#1, score#1],
                    [listing_id#2, score#2]
                ]
                weight: 1.0
                ms_took: 5050
            },
            recommender_friendly_name#2:{
                recommendations:[
                    [listing_id#1, score#1],
                    [listing_id#2, score#2]
                ]
                weight: 2.0
                ms_took: 5050
            }
        },
        profile_id#2: {
            recommender_friendly_name#1:{
                recommendations:[
                    [listing_id#1, score#1],
                    [listing_id#2, score#2]
                ]
                weight: 1.0,
                ms_took: 5050
            },
            recommender_friendly_name#2:{
                recommendations:[
                    [listing_id#1, score#1],
                    [listing_id#2, score#2]
                ]
                weight: 1.0
                ms_took: 5050
            }
        }
    }

    recommendations key is a list of tuples of listing_id and scores in which it is sorted by value
    """

    def __init__(self):
        self.recommender_classes = {
            'elasticsearch_user_base': ElasticsearchUserBaseRecommender,
            'elasticsearch_content_base': ElasticsearchContentBaseRecommender,
            'sample_data': SampleDataRecommender,
            'baseline': BaselineRecommender,
            'graph_cf': GraphCollaborativeFilteringBaseRecommender,
        }
        self.recommender_result_set = {}

    def get_recommender_class_obj(self, recommender_class_string):
        """
        Get Recommender class and make a instance of it
        """
        if recommender_class_string in self.recommender_classes:
            return self.recommender_classes[recommender_class_string]()
        else:
            raise Exception('Recommender Engine [{}] Not Found'.format(recommender_class_string))

    def merge(self, recommender_friendly_name, recommendation_weight, recommendations_results, recommendations_time):
        """
        Purpose is to merge all of the different Recommender's algorthim recommender result together.
        This function is responsible for merging the results of the other Recommender recommender_result_set diction into self recommender_result_set

        Args:
            friendly_name: Recommender friendly name
            recommendation_weight: Recommender weight
            recommendations_results: Recommender results
                {
                    profile_id#1: {
                        listing_id#1: score#1,
                        listing_id#2: score#2
                    },
                    profile_id#2: {
                        listing_id#1: score#1,
                        listing_id#2: score#2,
                        listing_id#3: score#3,
                    }
                }
            recommendations_time: Recommender time
        """
        # print('recommender_friendly_name: {}'.format(recommender_friendly_name))
        # print('recommendation_weight: {}'.format(recommendation_weight))
        # print('recommendations_results: {}'.format(recommendations_results))
        # print('recommendations_time: {}'.format(recommendations_time))
        sorted_recommendations = recommend_utils.get_top_n_score(recommendations_results, 20)

        if recommendations_results is None:
            return False
        for profile_id in sorted_recommendations:
            current_recommendations = sorted_recommendations[profile_id]

            if profile_id not in self.recommender_result_set:
                self.recommender_result_set[profile_id] = {}
            if recommender_friendly_name not in self.recommender_result_set[profile_id]:
                self.recommender_result_set[profile_id][recommender_friendly_name] = {
                    'recommendations': current_recommendations,
                    'weight': recommendation_weight,
                    'ms_took': recommendations_time
                }

        return True

    def recommend(self, recommender_string):
        """
        Creates Recommender Object, and execute the recommend

        Args:
            recommender_string: Comma Delimited list of Recommender Engine to execute
        """
        recommender_list = [self.get_recommender_class_obj(current_recommender.strip()) for current_recommender in recommender_string.split(',')]

        start_ms = time.time() * 1000.0

        for current_recommender_obj in recommender_list:
            logger.info('=={}=='.format(current_recommender_obj.__class__.__name__))

            friendly_name = current_recommender_obj.__class__.__name__
            if hasattr(current_recommender_obj.__class__, 'friendly_name'):
                friendly_name = current_recommender_obj.__class__.friendly_name

            recommendation_weight = 1.0
            if hasattr(current_recommender_obj.__class__, 'recommendation_weight'):
                recommendation_weight = current_recommender_obj.__class__.recommendation_weight

            recommender_obj = current_recommender_obj

            recommendations_start_ms = time.time() * 1000.0
            recommendations_results = recommender_obj.recommend()
            recommendations_end_ms = time.time() * 1000.0
            recommendations_time = recommendations_end_ms - recommendations_start_ms

            logger.info('Merging {} into results'.format(friendly_name))
            self.merge(friendly_name, recommendation_weight, recommendations_results, recommendations_time)

        start_db_ms = time.time() * 1000.0
        self.save_to_db()
        end_db_ms = time.time() * 1000.0
        logger.info('Save to database took: {} ms'.format(end_db_ms - start_db_ms))
        logger.info('Whole Process: {} ms'.format(end_db_ms - start_ms))

    def save_to_db(self):
        """
        This function is responsible for storing the recommendations into the database

        Performance:
            transaction.atomic() - 430 ms
            Without Atomic and Batch - 1400 ms
        """
        batch_list = []

        for profile_id in self.recommender_result_set:
            # print('*-*-*-*-'); import json; print(json.dumps(self.recommender_result_set[profile_id])); print('*-*-*-*-')
            profile = None
            try:
                profile = models.Profile.objects.get(pk=profile_id)
            except ObjectDoesNotExist:
                profile = None

            if profile:
                # Clear Recommendations Entries before putting new ones.
                recommendations_query = models.RecommendationsEntry.objects.filter(target_profile=profile)

                if recommendations_query.count() > 1:
                    recommendations_query.delete()

                for current_recommender_friendly_name in self.recommender_result_set[profile_id]:
                    output_current_tuples = []

                    current_recommendations = self.recommender_result_set[profile_id][current_recommender_friendly_name]['recommendations']

                    for current_recommendation_tuple in current_recommendations:
                        current_listing_id = current_recommendation_tuple[0]
                        # current_listing_score = current_recommendation_tuple[1]

                        current_listing = None
                        try:
                            current_listing = models.Listing.objects.get(pk=current_listing_id)
                        except ObjectDoesNotExist:
                            current_listing = None

                        if current_listing:
                            output_current_tuples.append(current_recommendation_tuple)

                    self.recommender_result_set[profile_id][current_recommender_friendly_name]['recommendations'] = output_current_tuples

                batch_list.append({'target_profile': profile,
                                   'recommendation_data': msgpack.packb(self.recommender_result_set[profile_id])})

                if len(batch_list) >= 1000:
                    bulk_recommendations_saver(batch_list)
                    batch_list = []

        if batch_list:
            bulk_recommendations_saver(batch_list)
