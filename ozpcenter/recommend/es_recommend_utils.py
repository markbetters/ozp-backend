"""
ESRecommendUtils
Elasticsearch Utils to setup tables and perform searches
"""
import logging

from django.conf import settings

from ozpcenter import models
import ozpcenter.api.profile.model_access as model_access
from ozpcenter.api.listing import model_access_es

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))

# Create ES client
es_client = model_access_es.es_client

# Static Variables to get ratings greater than this value entered into ES User Profile Table:
MIN_ES_RATING = 3.5


class ESRecommendUtils(object):
    """
    Create mappings based on if User Based ES Recommendation Table exists or not.
    Populate Elasticsearch table with data needed to be used by both Elasticsearch
    Recommendation Algorithms (Collaborative/User and Content)
    """

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
        request_body = ESRecommendUtils.initialize_es_recommender_table()
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
