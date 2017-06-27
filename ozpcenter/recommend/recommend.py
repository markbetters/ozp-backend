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
from ozpcenter.api.listing import model_access_es
from ozpcenter.api.listing.model_access_es import check_elasticsearch
from ozpcenter.recommend import recommend_utils
from ozpcenter.recommend.graph_factory import GraphFactory
# from ozpcenter.recommend.graph_factory import GraphFactory


# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))

# Create ES client
es_client = model_access_es.es_client


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


class ElasticsearchContentBaseRecommender(Recommender):
    """
    Elasticsearch Content based recommendation engine
    """
    friendly_name = 'Elasticsearch Filtering'
    recommendation_weight = 1.0

    def initiate(self):
        """
        Initiate any variables needed for recommendation_logic function
        Make sure the Elasticsearch is up and running
        """
        check_elasticsearch()
        # TODO: Make sure the elasticsearch index is created here with the mappings

    def recommendation_logic(self):
        """
        Recommendation logic

        Template Code to make sure that Elasticsearch client is working
        This code should be replace by real algorthim
        """
        logger.debug('Elasticsearch Content Base Recommendation Engine')
        logger.debug('Elasticsearch Health : {}'.format(es_client.cluster.health()))


class ElasticsearchUserBaseRecommender(Recommender):
    """
    Elasticsearch User based recommendation engine
    Steps:
       - Initialize Mappings for Reviews Table to import
       - Import Ratings Table
       - Perform aggregations on data to obtain recommendation list
         - Need to ensure that user apps and bookmarked apps are not in list
       - Output with query and put into recommendation table:
       Format should be:
                 profile_id#1: {
                     recommender_friendly_name#1:{
                         recommendations:[
                             [listing_id#1, score#1],
                             [listing_id#2, score#2]
                         ]
                         weight: 1.0
                         ms_took: 5050
                     },
    """
    '''
    # Algorithm detailed information
    # Structure to setup for storing Elasticsearch data:
        Mapping of data:
            MAPPING:
                recommend - document property to store the contents under
                    fields used:
                        author_id - Stores the id of the user the data is about
                        bookmark_ids - Stores a list of bookmarks ids that the user has bookmarked
                        categories - Stores a list of the categories for associating with the user
                        ratings - Nested object
                            - listing_id - Listing Id for rated app
                            - rate - Rating given to app by user
                            - listing_categories - Category(ies) that the app is listed under
                (All of the fields are of type long so as to store numeric values)
                TODO: Need to check if storing as a String might be better

    # Theory Information for Elasticsearch:
    # Information on Significant Term Aggregations that is used in this algorithm can be found here:
    #        https://www.elastic.co/guide/en/elasticsearch/reference/2.4/search-aggregations-bucket-significantterms-aggregation.html
    # The Elasticsearch process is based on significant terms aggregations of data.
    # The process will derive scores based on frequencies in the foreground and background sets.
    #   The terms are then considered significant if there is a noticeable difference in
    #   frequency in how it appears in the subset and also in the background data set.
    # The frequency is based on bookmarked, reviewed items and categories that the listings are based
    #   on per user to create the background and foreground items for calculating the term frequency.
    # There is no clear way to explain how this works, but based on implementation if you were to have people
    #   review similar listings in the same category and then a person that has those categories bookmarked but
    #   not all of tha apps should see the other apps from the category that are reviewed and bookmarked by other users.
    # The apps will be then ranked based on the number of occurrences that they have compared to the total number in the set.
    # Once the score is created one will show the ranking based on the number of matching documents including occurrences
    #   versus the total number of documents in the set that is being compared.
    #
    # To explain simply, the more of a category items that are bookmarked and reviewed the chances are the items
    #   will be recommended.  Items that have no reviews or bookmarks will not be included in the recommended items.
    #   Recommendation depends on having items that have been reviewed and/or bookmarked to even appear in the list.
    '''

    friendly_name = 'Elasticsearch User Based Filtering'
    # The weights that are returned by Elasticsearch will be 0.X and hence the reason that we need to multiply
    # by factors of 10 to get reasonable values for ranking.
    recommendation_weight = 50.0
    MIN_ES_RATING = 3.5  # Minimum rating to have results meet before being recommended for ES Recommender Systems

    def initiate(self):
        """
        Initiate any variables needed for recommendation_logic function
        Make sure the Elasticsearch is up and running
        Steps:
        - Make sure that Elasticsearch is running
        - Ensure that variables are setup and working properly.
        - Import data into Elasticsearch
        """
        '''
        # Process Creating Documents (Importing) for searching:
        - Initially create a mapping for Elasticsearch using the above mapping data
        - Check to see if Elasticsearch table already exists
            - if so then remove the table
        - Create a new table to store data
        - Loop through all reviews:
            - Search for user (aka author_id) to get all reviewed listings by user
            - Add only items that are rated above the MIN_ES_RATING to the categories to be added to
                the user profile.  This makes items that are not ranked high to not play a role in which categories
                the user is associated with.
            - If new record, then create the contents just retrieved into a document
            - Else, append the information to the existing document
        '''

        check_elasticsearch()
        # TODO: Make sure the elasticsearch index is created here with the mappings

        '''
        Load data from Reviews Table into memory
        '''
        ###########
        # Loading Review Data:
        logger.debug('Elasticsearch User Base Recommendation Engine: Loading data from Review model')
        reviews_listings = models.Review.objects.all()
        reviews_listing_uname = reviews_listings.values_list('id', 'listing_id', 'rate', 'author')
        # End loading of Reviews Table data
        ###########

        number_of_shards = settings.ES_NUMBER_OF_SHARDS
        number_of_replicas = settings.ES_NUMBER_OF_REPLICAS

        '''
        Use Ratings table for data
        '''
        # Initialize ratings table for Elasticsearch to perform User Based Recommendations:
        rate_request_body = {
            "settings": {
                "number_of_shards": number_of_shards,
                "number_of_replicas": number_of_replicas  # ,
            },
            "mappings": {
                "recommend": {
                    "properties": {
                        "author_id": {
                            "type": "long"
                        },
                        "ratings": {
                            "type": "nested",
                            "properties": {
                                "listing_id": {
                                    "type": "long"
                                },
                                "rate": {
                                    "type": "long",
                                    "boost": 10
                                },
                                "listing_categories": {
                                    "type": "long"
                                }
                            }
                        },
                        "bookmark_ids": {
                            "type": "long"
                        },
                        "categories": {
                            "type": "long"
                        }
                    }
                }
            }
        }

        # Initialize Tables:
        # Initializing Recommended by Ratings ES Table by removing old Elasticsearch Table:
        if es_client.indices.exists(settings.ES_RECOMMEND_USER):
            resdel = es_client.indices.delete(index=settings.ES_RECOMMEND_USER)
            logger.info("Deleting Existing ES Index Result: '{}'".format(resdel))

        # Create ES Index since it has not been created or is deleted above:
        connect_es_record_exist = es_client.indices.create(index=settings.ES_RECOMMEND_USER, body=rate_request_body)
        logger.info("Creating ES Index after Deletion Result: '{}'".format(connect_es_record_exist))

        # Recommendation Listings loaded at start:
        # reviews_listings = models.Review.objects.all()
        # reviews_listing_uname = reviews_listings.values_list('id', 'listing_id', 'rate', 'author_id')

        for record in reviews_listing_uname:
            result_es = {}

            query_term = {
                "query": {
                    "term": {
                        "author_id": record[3]
                    }
                }
            }

            # Get current reviewed items for Person (author_id):
            es_search_result = es_client.search(
                index=settings.ES_RECOMMEND_USER,
                body=query_term
            )

            # For each reviewed listing_id in ratings_items get the categories associated with the listing:
            es_cat_query_term = {
                "_source": ["id", "categories"],
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"id": record[1]}}
                        ]
                    }
                }
            }

            category_items = []

            # Only take categories when the rating is above a 3, do not look at categories when the rating is 3 and below:
            if record[2] > self.MIN_ES_RATING:
                es_cat_search = es_client.search(
                    index=settings.ES_INDEX_NAME,
                    body=es_cat_query_term
                )

                # Set category_items array with category id's:
                if es_cat_search['hits']['total'] <= 1:
                    category_items = [cat['id'] for cat in es_cat_search['hits']['hits'][0]['_source']['categories']]
                else:
                    logger.debug("== MORE THAN ONE ID WAS FOUND ({}) ==".format(es_cat_search['hits']['total']))

            ratings_items = []
            ratings_items.append({"listing_id": record[1], "rate": record[2], "listing_categories": category_items})

            if es_search_result['hits']['total'] == 0:
                # If record does not exist in Recommendation List, then create it:
                result_es = es_client.create(
                    index=settings.ES_RECOMMEND_USER,
                    doc_type=settings.ES_RECOMMEND_TYPE,
                    id=record[0],
                    refresh=True,
                    body={
                        "author_id": record[3],
                        "ratings": ratings_items,
                        "categories": category_items
                    })
            else:
                # Update existing record:
                record_to_update = es_search_result['hits']['hits'][0]['_id']
                current_ratings = es_search_result['hits']['hits'][0]['_source']['ratings']
                new_ratings = current_ratings + ratings_items
                current_categories = es_search_result['hits']['hits'][0]['_source']['categories']

                # Since exisiting recommendation lists have been deleted, no need to worry about
                # adding duplicate data.

                result_es = es_client.update(
                   index=settings.ES_RECOMMEND_USER,
                   doc_type=settings.ES_RECOMMEND_TYPE,
                   id=record_to_update,
                   refresh=True,
                   body={"doc": {
                       "ratings": new_ratings,
                       "categories": list(set(current_categories + category_items))
                       }
                   })

            logger.info("Creating/Updating Record Result: '{}'".format(result_es))

    def recommendation_logic(self):
        """
        Recommendation logic
        - Create a search that will use the selected algorithm to create a recommendation list
        """
        '''
        # Process for creating recommendations:
        - Loop through all of the profiles and for each profile:
            - Get all of the bookmarked apps and store in user recommendation profile
            - Add category for all apps that were bookmarked to category field
            - if so then remove the table
        - Create a new table to store data
        - Loop through all reviews:
            - Search for user (aka author_id) to get all reviewed listings by user
            - Add only items that are rated above the MIN_ES_RATING to the categories to be added to
                the user profile.  This makes items that are not ranked high to not play a role in which categories
                the user is associated with.
            - If new record, then create the contents just retrieved into a document
            - Else, append the information to the existing document
            - Create query using bookmarked apps and categories and then search for reviewed listings
                that match the bookmarked apps based on search results
            - Form qurey for Elasticsearch that will take listings greater than MIN_ES_RATING and exclude bookmarked
                apps for user in reviewed listings and then remove bookmarked apps from searching the bookmarked app listings.
            - Run Query for each user and append recommended list to the user profile recommendations
        '''

        logger.debug('Elasticsearch User Base Recommendation Engine')
        logger.debug('Elasticsearch Health : {}'.format(es_client.cluster.health()))

        #########################
        # Information on Algorithms: (as per Elasticsearch: https://www.elastic.co/guide/en/elasticsearch/reference/2.4/search-aggregations-bucket-significantterms-aggregation.html)
        #       significant_terms (JLH) - Measures the statistical significance of the results of the search vs the entire set of results
        #                                 Calculated as follows: (ForegroundPercentage / BackgroundPercentage) * (ForegroundPercentage - BackgroundPercentage)
        #                                 =====> Results in a balance between the rare and the common items.
        #       chi_square              - Can add siginificant scoring by adding parameters such as include_negatives and background_is_superset.
        #       gnd (google normalized distance) - Used to determine similarity between words and phrases using the distance between them.
        #########################

        # Set Aggrelation List size for number of results to return:
        AGG_LIST_SIZE = 50  # Will return up to 30 results based on query.  Default is 10 if parameter is left out of query.

        # Retreive all of the profiles from database:
        all_profiles = models.Profile.objects.all()

        for profile in all_profiles:
            # ID to adivse on recommendation:
            profile_id = profile.id

            # Retrieve Bookmark App Listings for user:
            bookmarked_apps = models.ApplicationLibraryEntry.objects.for_user(profile.user.username)
            bookmarked_list = []
            for bkapp in bookmarked_apps:
                bookmarked_list.append(bkapp.listing.id)

            # print("Bookmarked Apps: ", bookmarked_list)

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

            # Only add/change documents if the user has any bookmarks, otherwise no need to update
            # documents with null information:
            category_items = []
            agg_query_term = {}
            if len(bookmarked_list) > 0:
                for bk_item in bookmarked_list:
                    # For each listing_id in ratings_items get the categories associated with the listing:
                    es_cat_query_term = {
                        "_source": ["id", "categories"],
                        "query": {
                            "bool": {
                                "must": [
                                    {"term": {"id": bk_item}}
                                ]
                            }
                        }
                    }
                    es_cat_search = es_client.search(
                        index=settings.ES_INDEX_NAME,
                        body=es_cat_query_term
                    )

                    if es_cat_search['hits']['total'] <= 1:
                        category_items = list(set(category_items + [cat['id'] for cat in es_cat_search['hits']['hits'][0]['_source']['categories']]))
                    else:
                        logger.debug("== CATEGORY ITEMS MORE THAN 1 ({}) ==".format(es_cat_search['hits']['total']))

                # Get Categories for bookmarked apps:
                categories = []
                if es_search_result['hits']['total'] > 0:
                    categories = es_search_result['hits']['hits'][0]['_source']['categories']

                # No Reviews were made, but user has bookmarked apps:
                if es_search_result['hits']['total'] == 0:
                    # print("PROFILE: ", profile_id)
                    result_es = es_client.create(
                        index=settings.ES_RECOMMEND_USER,
                        doc_type=settings.ES_RECOMMEND_TYPE,
                        id=profile_id,
                        refresh=True,
                        body={
                            "author_id": profile_id,
                            "bookmark_ids": bookmarked_list,
                            "categories": category_items
                        })
                    logger.info("Bookmarks Created for profile: {} with result: {}".format(profile_id, result_es))
                else:
                    record_to_update = es_search_result['hits']['hits'][0]['_id']
                    # Get current categories and then use to add to category_items:
                    current_categories = es_search_result['hits']['hits'][0]['_source']['categories']
                    result_es = es_client.update(
                       index=settings.ES_RECOMMEND_USER,
                       doc_type=settings.ES_RECOMMEND_TYPE,
                       id=record_to_update,
                       refresh=True,
                       body={"doc":
                            {
                                "bookmark_ids": bookmarked_list,
                                "categories": list(set(current_categories + category_items))
                            }
                       })
                    # print("Bookmarks Updated for profile: {} with result: {}".format(profile_id, result_es))

                if len(categories) > 0:
                    agg_query_term = {
                        "constant_score": {
                            "filter": {
                                "bool": {
                                    "should": [
                                        {"terms": {"bookmark_ids": bookmarked_list}},
                                        {"terms": {"categories": categories}},
                                        {
                                            "nested": {
                                                "path": "ratings",
                                                "query": {
                                                    "bool": {
                                                        "should": [
                                                            {"terms": {"ratings.listing_id": bookmarked_list}}
                                                        ]
                                                    }
                                                }
                                            }
                                        }]
                                }
                            }
                        }
                    }
                else:
                    agg_query_term = {
                        "constant_score": {
                            "filter": {
                                "bool": {
                                    "should": [
                                        {"terms": {"bookmark_ids": bookmarked_list}},
                                        {
                                            "nested": {
                                                "path": "ratings",
                                                "query": {
                                                    "bool": {
                                                        "should": [
                                                            {"terms": {"ratings.listing_id": bookmarked_list}}
                                                        ]
                                                    }
                                                }
                                            }
                                        }]
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
                                            "gte": self.MIN_ES_RATING
                                        }
                                    }
                                }
                            },
                            "aggs": {
                                "significant_terms": {
                                    "field": "ratings.listing_id",
                                    "exclude": bookmarked_list,
                                    "min_doc_count": 1,
                                    "size": AGG_LIST_SIZE
                                    # To change algorithm add the following after "size" parameter:
                                    # Add either: (No paraneters has JLH algorithm being used)
                                    #   "gnd": {} # optional parameters can be added if needed
                                    #   "chi_square": {} # optional parameters can be added if needed
                                },
                                "aggs": {
                                    "bookmarkedlistings": {
                                        "significant_terms": {
                                            "field": "bookmark_ids",
                                            "exclude": bookmarked_list,
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
                }
            }
            # print("+++++++++++++++++++++++++++++++++++++")
            # print("QUERY TERM: ", agg_search_query)
            # print("+++++++++++++++++++++++++++++++++++++")
            es_query_result = es_client.search(
                index=settings.ES_RECOMMEND_USER,
                body=agg_search_query
            )
            # print("RESULT FOR ONE SET: ", es_query_result)

            recommended_items = es_query_result['aggregations']['the_listing']['aggs']['buckets']
            # print("Length of Array: ", len(recommended_items))
            # Add items to recommended list for the profile:
            for indexitem in recommended_items:
                score = indexitem['score']
                # print("INDEX ITEM: ", indexitem)
                # print('Key {}, Score {}'.format(indexitem['key'], score))
                self.add_listing_to_user_profile(profile_id, indexitem['key'], score, False)

            logger.info("= ES USER RECOMMENDER Engine Completed Results for {} =".format(profile_id))
            logger.info("Creating/Updating Record Result: '{}'".format(es_query_result))
        logger.info("= ES USER RECOMMENDATION Results Completed =")
        ############################
        # END
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
