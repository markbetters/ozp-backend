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
import ozpcenter.api.profile.model_access as model_access
from ozpcenter.recommend import recommend_utils
from ozpcenter.recommend.graph_factory import GraphFactory
from ozpcenter.api.listing.elasticsearch_util import elasticsearch_factory
# from ozpcenter.recommend.es_recommend_utils import ESRecommendUtils

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))

# Store if ES index has been created:
es_table_created = False
# Static Variables to get ratings greater than this value entered into ES User Profile Table:
MIN_ES_RATING = 3.5


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

    @staticmethod
    def get_index_mapping():
        """
        Mapping to be used for Elasticsearch Table for both Content and Collaborative Recommendation Engines:
            Structure to setup for storing Elasticsearch data:
                Mapping of data:
                    MAPPING:
                        recommend - document property to store the contents under
                            fields used:
                                author_id - Id of the user the data is about
                                author - String of username, not full name
                                titles - List of titles that the the author has bookmarked or rated that is greater than
                                         the MIN_ES_RATING
                                descriptions - List of the descriptions that correspond to the titles that have been stored
                                description_shorts - List of the description_shorts that correspond to the titles that have been stored
                                (Not Implemented yet) - agency_short_name - Store the agency that the author is associated with currently
                                tags - Store all of the tags for a title that has been stored
                                categories_text - List of the categories text associated with the titles
                                ratings - Nested object
                                    - listing_id - Listing Id for rated app
                                    - rate - Rating given to app by user
                                    - listing_categories - Category(ies) that the app is listed under in text form
                                    - category_ids - List of the category ids in numeric format
                                bookmark_ids - Stores a list of bookmarks ids that the user has bookmarked
                                categories - List of the categories in text format all listings associated with the user that are bookmarked or greater than MIN_ES_RATING
        """

        number_of_shards = settings.ES_NUMBER_OF_SHARDS
        number_of_replicas = settings.ES_NUMBER_OF_REPLICAS

        # Initialize ratings table for Elasticsearch to perform User Based and Content Recommendations:
        index_mapping = {
            "settings": {
                "number_of_shards": number_of_shards,
                "number_of_replicas": number_of_replicas
            },
            "mappings": {
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
                            "analyzer": "english"
                        },
                        "ratings": {
                            "type": "nested",
                            "properties": {
                                "listing_id": {
                                    "type": "long",
                                    "index": "not_analyzed"
                                },
                                "rate": {
                                    "type": "long",
                                    "boost": 1
                                },
                                "listing_categories": {
                                    "type": "string"
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

    @staticmethod
    def load_data_into_es_table():
        """
        Prequisites: Elasticsearch table must be checked before hand to make sure that it is empty before running this
                     routine.  Table should also be created before running this procedure.

        - Get Mapping for Elasticsearch Table
        - Cycle through all profiles:
            - For each profile:
                Get Reviewed Listings with Categories, Title, Description, and Description Short Text
                Get Bookmarked Listings with Categories, Title, Description, and Description Short Text
                Add information to Elasticsearch Table for profile
        """
        es_client = elasticsearch_factory.get_client()
        request_body = ElasticsearchRecommender.get_index_mapping()
        # Preventive measure to make sure that the ES Table has been cleared before executing this method.
        # Assumption is that by executing this routine, a new ES Table of data is needed, there for no checks
        # on the validity of the old data is performed here:
        if es_client.indices.exists(settings.ES_RECOMMEND_USER):
            resdel = es_client.indices.delete(index=settings.ES_RECOMMEND_USER)
            logger.info("Deleting Existing ES Index Result: '{}'".format(resdel))

        # Create ES Index since it has not been created or is deleted above:
        connect_es_record_exist = es_client.indices.create(index=settings.ES_RECOMMEND_USER, body=request_body)

        if connect_es_record_exist['acknowledged'] is False:
            logger.error("ERROR: Creating ES Index after Deletion Failed Result: '{}'".format(connect_es_record_exist))
            exit(1)

        # Retreive all of the profiles from database:
        all_profiles = models.Profile.objects.all()
        all_profiles_count = all_profiles.count()

        current_profile_count = 0

        for profile in all_profiles:
            # Initialize list for: Title, Description, Description Short, Categories and Tag Text to store for user:
            title_text_list = set()
            description_text_list = set()
            description_short_text_list = set()
            categories_text_list = set()
            category_id_list = set()
            tags_text_list = set()
            profile_info = model_access.get_profile_by_id(profile.user_id)
            profile_username = profile_info.user.username
            # Initialize Counter for tracking progress on creation:
            current_profile_count = current_profile_count + 1

            # Get all apps Reviews for profile:
            # review_listings = models.Review.objects.filter(author=profile.user_id)
            # Get reviews for user that are greater than a rate of 3:
            profile_listings_review = []
            for review_listing_query in models.Review.objects.filter(author=profile.user_id):

                # Get the details of the Listing by querying the listing object linked to the Review:
                listing_obj = review_listing_query.listing

                if review_listing_query.rate > MIN_ES_RATING:
                    # Add Title text to list of Titles:
                    title_text_list.add(listing_obj.title)

                    # Add Description to list of Descriptions:
                    description_text_list.add(listing_obj.description)

                    # Add Description Short to list of Description Shorts:
                    description_short_text_list.add(listing_obj.description_short)

                    # Get Tags for Reviewed apps by User:
                    for tagitem in listing_obj.tags.all():
                        tags_text_list.add(str(tagitem))

                # Take the listing information and add it to the reviews object:
                # Get Categories for all Reviewed apps by User:
                listing_categories = set()
                listing_category_id_list = set()
                for cat_item in review_listing_query.listing.categories.all():
                    listing_categories.add(str(cat_item))
                    listing_category_id_list.add(cat_item.id)
                    categories_text_list.add(str(cat_item))
                    category_id_list.add(cat_item.id)

                update_item = {"listing_id": review_listing_query.listing_id, "rate": review_listing_query.rate, "listing_categories": list(categories_text_list), "category_ids": list(listing_category_id_list)}
                profile_listings_review.append(update_item)

            # Get all apps Bookmarked for profile:
            # Initialize bookmark fields:
            bookmarked_id_list = []
            # Cycke through list to prevent looping each time and perform one loop:
            for bookmark_item in models.ApplicationLibraryEntry.objects.for_user(profile.user.username):
                # Get the details of the Bookmarked Listing by querying the listing object linked to the Bookmark:
                bookmarked_listing_obj = bookmark_item.listing

                # Add Listing ID to Bookmarked Listings:
                bookmarked_id_list.append(bookmarked_listing_obj.id)

                # Add Title text to list of Titles:
                title_text_list.add(bookmarked_listing_obj.title)

                # Add Description to list of Descriptions:
                description_text_list.add(bookmarked_listing_obj.description)

                # Add Description Short to list of Description Shorts:
                description_short_text_list.add(bookmarked_listing_obj.description_short)

                # Get Categories for all Bookmarked apps by User:
                for cat_item in bookmarked_listing_obj.categories.all():
                    categories_text_list.add(str(cat_item))

                # Get Tags for Reviewed apps by User:
                for tagitem in bookmarked_listing_obj.tags.all():
                    tags_text_list.add(str(tagitem))

            # Create Elasticsearch table entry:
            # Take results of the all reviews by user and create a concatenated list to add to
            # the Elastic Table:

            result_es = es_client.create(
                index=settings.ES_RECOMMEND_USER,
                doc_type=settings.ES_RECOMMEND_TYPE,
                id=profile.user_id,
                refresh=True,
                body={
                    "author_id": profile.user_id,
                    "author": profile_username,
                    "titles": list(title_text_list),
                    "descriptions": list(description_text_list),
                    "description_shorts": list(description_short_text_list),
                    "tags": list(tags_text_list),
                    "categories_text": list(categories_text_list),
                    "bookmark_ids": list(bookmarked_id_list),
                    "categories_id": list(category_id_list),
                    "ratings": profile_listings_review
                }
            )

            if result_es['created'] is False:
                logger.error("ERROR: Creating ES input item has failed for User {} with Result: '{}'".format(result_es['_id'], result_es))

            logger.info("= ES RECOMMENDATION Creation of profile {}/{} =".format(current_profile_count, all_profiles_count))

        return

    @staticmethod
    def es_user_based_recommendation(profile_id):
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
        #########################
        # Information on Algorithms: (as per Elasticsearch: https://www.elastic.co/guide/en/elasticsearch/reference/2.4/search-aggregations-bucket-significantterms-aggregation.html)
        #       significant_terms (JLH) - Measures the statistical significance of the results of the search vs the entire set of results
        #                                 Calculated as follows: (ForegroundPercentage / BackgroundPercentage) * (ForegroundPercentage - BackgroundPercentage)
        #                                 =====> Results in a balance between the rare and the common items.
        #       chi_square              - Can add siginificant scoring by adding parameters such as include_negatives and background_is_superset.
        #       gnd (google normalized distance) - Used to determine similarity between words and phrases using the distance between them.
        #########################

        # Set Aggrelation List size for number of results to return:
        AGG_LIST_SIZE = 50  # Will return up to 50 results based on query.  Default is 10 if parameter is left out of query.

        es_client = elasticsearch_factory.get_client()
        # Create ES profile to search records:
        es_profile_search = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"author_id": profile_id}}
                    ],
                }
            }
        }

        # Retrieve results from ES Table for matching profile to update and get recommendations:
        es_search_result = es_client.search(
            index=settings.ES_RECOMMEND_USER,
            body=es_profile_search
        )

        agg_query_term = {}
        # Get list of category ids, bookmark ids and app ids that have been rated to create the recommendation query:
        categories_to_match = es_search_result['hits']['hits'][0]['_source']['categories_id']
        bookmarks_to_match = es_search_result['hits']['hits'][0]['_source']['bookmark_ids']
        rated_apps_list = list([rate['listing_id'] for rate in es_search_result['hits']['hits'][0]['_source']['ratings']])
        rated_apps_list_match = list([rate['listing_id'] for rate in es_search_result['hits']['hits'][0]['_source']['ratings'] if rate['rate'] > MIN_ES_RATING])

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
                                        "gte": MIN_ES_RATING
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
                                # To change algorithm add the following after "size" parameter:
                                # Add either: (No paraneters has JLH algorithm being used)
                                #   "gnd": {} # optional parameters can be added if needed
                                #   "chi_square": {} # optional parameters can be added if needed
                            }
                        }
                    }
                }
            }
        }
        # print("+++++++++++++++++++++++++++++++++++++")
        # print("QUERY TERM: ", agg_search_query)
        # print("+++++++++++++++++++++++++++++++++++++")
        es_query_result = es_client.search(
            index=settings.ES_RECOMMEND_USER,
            body=agg_search_query
        )

        recommended_items = es_query_result['aggregations']['the_listing']['aggs']['buckets']

        return recommended_items

    @staticmethod
    def es_content_based_recommendation(profile_id, RESULT_SIZE):
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

        # Query the results for the profile passed in to get details to
        # base recommendation on:
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"author_id": profile_id}}
                    ]
                }
            }
        }

        # Query Elasticsearch:
        es_profile_result = es_client.search(
            index=settings.ES_RECOMMEND_USER,
            body=query
        )

        each_profile_source = es_profile_result['hits']['hits'][0]['_source']

        query_object = []

        # Add categories to query to try and limit the results:
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

        # Add title to the query:
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

        # Add description to the query:
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

        # Add description_short to the query:
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

        query_compare = {}

        # Add a restriction to remove bookmarked apps and rated apps from the query if they are present in
        # the profile.  This will eliminate unnecessary items to be queried and returned:
        # The reason that the size is so large is because we do not want to limit the results to just a few
        # which then might be eleiminated when displayed to the user.  Hence the max result set is returned.
        query_compare = {
            "size": RESULT_SIZE,
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

        # Query the Elasticsearch application table listing and compare with query that has been developed:
        es_query_result = es_client.search(
            index=settings.ES_INDEX_NAME,
            body=query_compare
        )

        return(es_query_result)

    @staticmethod
    def new_user_return_list(RESULT_SIZE):
        """
        This procedure is a uses all profile contents to create recommendations for a new user.
        TODO: This is a solution to solve New User problem and will need to be revisited when
        live recommendations are implemented.

        It takes the entire population of applications and performs an analysis on them to determine
        the best applications to recommend to a new user.

        It uses key values returned by the Elasticsearch query for aggregations to develop a query to perform against
        the application listings.  This query then checks the title, description and description_short to search for
        the results.

        This might look similar to most popular, but is using the keywords from the most popular applications that people
        have bookmarked to create a new list of applications to recommend to the user.

        RETURN: The procedure will return a query results of applications matching query of RESULT_SIZE to be used for
                populating new user recommendations.
        """
        # Initialize variables:
        es_client = elasticsearch_factory.get_client()
        title_to_search_list = []

        # Create a search query to get a list of aggregations for users based on the title keywords:
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

        # Submit the query for results:
        es_content_init = es_client.search(
            index=settings.ES_RECOMMEND_USER,
            body=content_search_term
        )

        # For each item in the list of aggregations create a query for the titles that it should match in
        # in the applications list:
        for item_key in es_content_init['aggregations']['most_common_titles']['buckets']:
            title_to_search_list_item = {
                "multi_match": {
                    "query": item_key['key'],
                    "type": "cross_fields",
                    "fields": ["title", "description", "description_short"],
                    "minimum_should_match": "20%"
                }
            }
            # Append each title to the search paramter:
            title_to_search_list.append(title_to_search_list_item)

        # After creating the search paramter, create a query and limit it to the results to the first
        # max_result_set_new_user results since more than that are not necessary:
        max_result_set_new_user = RESULT_SIZE
        query_compare = {
            "size": max_result_set_new_user,
            "_source": ["id", "title"],
            "query": {
                "bool": {
                    "should": title_to_search_list
                }
            }
        }

        # Get the results from the query of Apps listings:
        es_query_result = es_client.search(
            index=settings.ES_INDEX_NAME,
            body=query_compare
        )

        return es_query_result


class ElasticsearchContentBaseRecommender(ElasticsearchRecommender):
    """
    Elasticsearch Content based recommendation engine
    Steps:
    - Initialize Mappings by calling common Utils command to create table if it has not already been created recently
    -
    - Import listings into main Elasticsearch table (if not already created recently)
        - Cycle through all reviews and add information to table (including text)
            - Add rating that the user given
        - Add all users that have bookmarked the app to the table
        - Go through User tables and add text to each record of a User Table
    - Perform calculations via query on data
    The Elasticsearch recommendation engine will find all listings that have a similar characteristics as the user
    and then will rank them based on parameters that are specified in the boost after comparing them to the current listings.
    Currently the weight will be based on the overall review ratings (only those that are 4 or 5 will be considered) for the applicaiton.
    Then the frequency of the weights and bookmarks will then be used to calculate the foreground and background
    occurrences to create a score that will then lead to the overall ranking of the apps.
    In addition all of the text will be retrieved from each listing to add to the user profile.  Then content that matches items in the
    user profile will be used against the listings table.  The highest ranked items will be returned upon a successful match.
    The results will only be based on the profile text matches and should use all of the text in the code to make a successful match.
    Content Based is based on User Based profiles and gets an updated one by adding the content to the user profiles.
    By adding the content to the user profiles, we can get content that matches what the user has bookmarked and
    reviewed.
    """
    friendly_name = 'Elasticsearch Content Filtering'
    # The weights that are returned by Elasticsearch will range between 0 and a any possible maximum because of query results.  Hence the reason
    # that we need to normalize the data.  Normailization is accomplished by moving the scale to be comprable with other engines using map_numbers function.
    # Reasoning: Results being possibly any range need to the results scaled up or down to be comporable with other engine results.
    # The weight being used is toning down the results so that they do not overwhelm other results solely based on content.
    recommendation_weight = 0.9  # Weighting is based on rebasing the results
    RESULT_SIZE = 20  # Get only the top 50 results
    min_new_score = 4  # Min value to set for rebasing of results
    max_new_score = 9  # Max value to rebase results to so that values
    content_norm_factor = 0.05  # Amount to increase the max value found so that saturation does not occur.

    def initiate(self):
        """
        Make sure the Elasticsearch is up and running

        Initialize any variables needed for recommendation_logic function
        - Load all listings into Elasticsearch if already not loaded
        - Cycle through all profiles and create a query that matches against content in
          listings
            - If a user does not have any results returned, then a new user algorithm will be used
              to create a standard list of recommendations based on items that other users have bookmarked
              and rated.  It uses the text from the most occurring items to create a search criteria that is
              used to provide recommendations.
           - Rebase each user's recommendations according to the max score for that user's recommendations to
             create a normalized baseline to compare with other listings from other engines.
        - Take recommendations and add them to the user profile
        """
        # Global variable to maintain if ES Table has been crated already or not (not persistant):
        global es_table_created

        # Ensure that Elasticsearch is running, otherwise will exit:
        elasticsearch_factory.check_elasticsearch()

        # Initialize ratings table for Elasticsearch to perform User Based Recommendations if needed:
        # If the ES table has not been created already then delete old one and create new one with
        # load_data_into_es_table routine:
        self.es_client = elasticsearch_factory.get_client()
        if not es_table_created:
            elasticsearch_factory.recreate_index_mapping(settings.ES_RECOMMEND_USER, ElasticsearchRecommender.get_index_mapping())

            # Load data into Table:
            ElasticsearchRecommender.load_data_into_es_table()
            # Set Table Created variable so that it does not run a second time in the same run:
            es_table_created = True

    def recommendation_logic(self):
        """
        Recommendation logic is where the use of Collaborative vs Content differ.  Both use the User Profile to get
        infromation on the user, but with Content, it takes the content from user profiles on apps based on criteria
        that is implemented in the calling method and gets a recommended list of apps to return to the user as
        recommendations.
        The list is then normalized and added to the recommendations database.
        """
        logger.info('= Elasticsearch Content Base Recommendation Engine= ')
        # Retreive all of the profiles from database:
        all_profiles = models.Profile.objects.all()
        all_profiles_count = all_profiles.count()

        performed_search_request = False
        new_user_return_list = []
        current_profile_count = 0

        for profile in all_profiles:
            # Increment Counter to track progress:
            current_profile_count = current_profile_count + 1

            # Get the profile id so that it can be used in later items:
            profile_id = profile.id
            """
            Check if results have been returned and if not then this is a NEW USER Problem.
            If no results are returned call the new user method in ESRecommendUtils to get the list of most common apps based on content
            that is being used by other users.
            """
            es_query_result = self.es_content_based_recommendation(profile_id, self.RESULT_SIZE)

            # Check if results returned are returned or if it is empty (New User):
            if es_query_result['hits']['total'] == 0:
                # New User routine, first check to make sure that the results have already not been populated:
                if not performed_search_request:
                    # If the results have not been retrieved for New User already once then retrieve them.
                    # Take half the result size for new users content search:
                    new_user_return_list = self.new_user_return_list(int(self.RESULT_SIZE / 2))

                    # Set the search parameter to True so that subsequent searches will not be performed:
                    performed_search_request = True

                # Get the recommended items from return list:
                recommended_items = new_user_return_list['hits']['hits']

                # Max score for Elasticsearch Content Based Recommendation to nomalize the data (New User):
                max_score_es_content = new_user_return_list['hits']['max_score'] + self.content_norm_factor * new_user_return_list['hits']['max_score']
            else:
                # Otherwise return recommendations that were returned:
                # Get only the results necessary from the returned JSON object:
                recommended_items = es_query_result['hits']['hits']

                # Max score for Elasticsearch Content Based Recommendation to nomalize the data:
                max_score_es_content = es_query_result['hits']['max_score'] + self.content_norm_factor * es_query_result['hits']['max_score']

            # Loop through all of the items and add them to the recommendation list for Content Based Filtering:
            for indexitem in recommended_items:
                score = recommend_utils.map_numbers(indexitem['_score'], 0, max_score_es_content, self.min_new_score, self.max_new_score)
                itemtoadd = indexitem['_source']['id']
                self.add_listing_to_user_profile(profile_id, itemtoadd, score, False)
            logger.info("= ES CONTENT RECOMMENDER Engine Completed Results for {}/{} =".format(current_profile_count, all_profiles_count))

        logger.info("= ES CONTENT RECOMMENDATION Results Completed =")
        ############################
        # END ES CONTENT BASED RECOMMENDATION
        ############################


class ElasticsearchUserBaseRecommender(ElasticsearchRecommender):
    """
    Elasticsearch User based recommendation engine
    Steps:
       - Initialize Mappings for Reviews Table to import
       - Import Ratings Table
       - Perform aggregations on data to obtain recommendation list
       - Need to ensure that user apps and bookmarked apps are not in list
       - Output with query and put into recommendation table:
       Output format:
                 profile_id#1: {
                     recommender_friendly_name#1:{
                         recommendations:[
                             [listing_id#1, score#1],
                             [listing_id#2, score#2]
                         ]
                         weight: <weight_constant>
                         ms_took: <time that process took>
                     },
    Algorithm detailed information:
    Theory Information for Elasticsearch:
    Information on Significant Term Aggregations that is used in this algorithm can be found here:
        https://www.elastic.co/guide/en/elasticsearch/reference/2.4/search-aggregations-bucket-significantterms-aggregation.html
    The Elasticsearch Collaborative process is based on significant terms aggregations of data.
    The process will derive scores based on frequencies in the foreground and background sets.
    The terms are then considered significant if there is a noticeable difference in
      frequency in how it appears in the subset and also in the background data set.
    The frequency is based on bookmarked, reviewed items and categories that the listings are based
      on per user to create the background and foreground items for calculating the term frequency between users.
    There is no clear way to explain how this works, but based on implementation if you were to have people
      review similar listings in the same category and then a person that has those categories bookmarked but
      not all of tha apps should see the other apps from the category that are reviewed and bookmarked by other users.
    The apps will be then ranked based on the number of occurrences that they have compared to the total number in the set.
    Once the score is created one will show the ranking based on the number of matching documents including occurrences
      versus the total number of documents in the set that is being compared.

    To explain simply, the more of a category items that are bookmarked and reviewed the chances are the items
      will be recommended.  Items that have no reviews or bookmarks will not be included in the recommended items.
      Recommendation depends on having items that have been reviewed and/or bookmarked to even appear in the list.
    """

    friendly_name = 'Elasticsearch User Based Filtering'
    # The weights that are returned by Elasticsearch will be 0.X and hence the reason that we need to normalize the data.
    # Normailization is accomplished by moving the scale to be comprable with other engines using map_numbers function.
    # Reasoning: Results of scores are between 0 and 1 with results mainly around 0.0X, thus the normalization is necessary.
    recommendation_weight = 1.0  # Weight that the overall results are multiplied against.  The rating for user based is less than 1.
    # Results are between 0 and 1 and then converted to between min_new_score and max_new_score and then are multiplied by the weight
    # to be slightly better than the baseline recommendation systems if necessary.
    min_new_score = 5  # Min value to set for rebasing of results
    max_new_score = 10  # Max value to rebase results to so that values

    def initiate(self):
        """
        Initiate any variables needed for recommendation_logic function
        Make sure the Elasticsearch is up and running
        Steps:
        - Make sure that Elasticsearch is running
        - Check if Elasticsearch Table has been created already
            - If so and the conditions match that it has been recently created then skip creating it again
            - Else create a new index and populate with user data
        """
        global es_table_created

        elasticsearch_factory.check_elasticsearch()
        # Initialize ratings table for Elasticsearch to perform User Based Recommendations if not already initialized:
        # If the ES table has not been created already then delete old one and create new one with
        # load_data_into_es_table routine:
        self.es_client = elasticsearch_factory.get_client()
        if not es_table_created:
            elasticsearch_factory.recreate_index_mapping(settings.ES_RECOMMEND_USER, self.get_index_mapping())
            logger.info("Recreated ES Index")

            # Load data into Table:
            ElasticsearchRecommender.load_data_into_es_table()
            # Set Table Created variable so that it does not run a second time in the same run:
            es_table_created = True

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
            # Increment Counter to track progress:
            current_profile_count = current_profile_count + 1

            # ID to advise on recommendation:
            profile_id = profile.id

            # Call staticmethod to get recommendaiton list based on profile_id:
            recommended_items = ElasticsearchRecommender.es_user_based_recommendation(profile_id)

            # If a recommendaiton list is returned then get the max score,
            # otherwise it is a new user or there is no profile to base recommendations on:
            if recommended_items:
                max_score_es_user = recommended_items[0]['score']

            # Add items to recommended list for the profile:
            for indexitem in recommended_items:
                # Rescale Results:
                score = recommend_utils.map_numbers(indexitem['score'], 0, max_score_es_user, self.min_new_score, self.max_new_score)
                # print("INDEX ITEM: ", indexitem)
                # print('Key {}, Score {}'.format(indexitem['key'], score))
                self.add_listing_to_user_profile(profile_id, indexitem['key'], score, False)

            logger.info("= ES USER RECOMMENDER Engine Completed Results for {}/{} =".format(current_profile_count, all_profiles_count))
        logger.info("= ES USER RECOMMENDATION Results Completed =")
        ############################
        # END ES USER BASED RECOMMENDATION
        ############################


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
