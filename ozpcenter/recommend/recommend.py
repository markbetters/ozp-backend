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
import ozpcenter.api.profile.model_access as model_access
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


class ElasticsearchContentBaseRecommender(Recommender):
    """
    Elasticsearch Content based recommendation engine
    - Initialize Recommendation list for content based
    - Import listings into main Elasticsearch table
        - Cycle through all reviews and add information to table (including text)
            - Add rating that the user given
        - Add all users that have bookmarked the app to the table
        - Go through User tables and add text to each record of a User Table
    - Perform calculations via query on data
    """
    '''
    # The Elasticsearch recommendation engine will find all listings that have a similar characteristics as the user
    # and then will rank them based on parameters that are specified in the boost after comparing them to the current listings.
    # Currently the weight will be based on the overall review ratings (only those that are 4 or 5 will be considered) for the applicaiton.
    # Then the frequency of the weights and bookmarks will then be used to calculate the foreground and background
    # occurrences to create a score that will then lead to the overall ranking of the apps.
    # In addition all of the text will be retrieved from each listing to add to the user profile.  Then content that matches items in the
    # user profile will be used against the listings table.  The highest ranked items will be returned upon a successful match.
    # The results will only be based on the profile text matches and should use all of the text in the code to make a successful match.
    '''
    friendly_name = 'Elasticsearch Content Filtering'
    # The weights that are returned by Elasticsearch will range between 0 and a any possible maximum because of query results.  Hence the reason
    # that we need to normalize the data.  Normailization is accomplished by moving the scale to be comprable with other engines using map_numbers function.
    # Reasoning: Results being possibly any range need to the results scaled up or down to be comporable with other engine results.
    # The weight being used is toning down the results so that they do not overwhelm other results solely based on content.
    recommendation_weight = 0.9  # Weighting is based on rebasing the results
    RESULT_SIZE = 50  # Get only the top 50 results
    min_new_score = 4  # Min value to set for rebasing of results
    max_new_score = 9  # Max value to rebase results to so that values
    content_norm_factor = 0.05  # Amount to increase the max value found so that saturation does not occur.

    def initiate(self):
        """
        Initiate any variables needed for recommendation_logic function
        Make sure the Elasticsearch is up and running
        """
        '''
        - Load all listings into Elasticsearch
        -
        '''
        check_elasticsearch()
        # Elasticsearch Content Based recommendation system uses the User Profiles and matches against the
        # applicaiton listings to create content matches.

        '''
        Initialize Tables:
        '''
        # Content Based is based on User Based profiles and gets an updated one by adding the content to the user profiles.
        # By adding the content to the user profiles, we can get content that matches what the user has bookmarked and
        # reviewed.

        # 10,000 is the max query size if there are more than 10,000 listings
        # then need to split the queries.  Currently this might be too much
        # overhead and hence the reason for not implementing in this implementation.
        # Since only 100 entries are max held in the table, reducing the size to RESULT_SIZE possiblities.
        # This will also improve performance on the index creation.
        query_size = {"size": self.RESULT_SIZE}

        # Get list of records from Listings table that fit the criteria needed to add information to the User
        # Profiles to create a match for content.
        listings_to_load_request = es_client.search(
            index=settings.ES_INDEX_NAME,
            body=query_size
        )

        listings_only = listings_to_load_request['hits']['hits']

        for listing in listings_only:
            bookmark_list = [listing['_source']['id']]

            # Get all of the listings that have been bookmarked from the User profiles so that the contents can
            # be updated wit text information.
            user_search_term = {
                "query": {
                    "bool": {
                        "should": [
                            {"terms": {"bookmark_ids": bookmark_list}},
                            {
                                "nested": {
                                    "path": "ratings",
                                    "query": {
                                        "bool": {
                                            "should": {
                                                "term": {
                                                    "ratings.listing_id": listing['_source']['id']
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            }

            user_search_results = es_client.search(
                index=settings.ES_RECOMMEND_USER,
                body=user_search_term
            )

            # Cycle through all of the users to update their user profiles with information that will have text for
            # the application to be added to the profile.
            for usertoupdate in user_search_results['hits']['hits']:
                current_titles = []
                current_descriptions = []
                current_descriptions_short = []
                current_tags = []
                current_categories = []
                # Check if there is a title in the profile so that it can be appended to and
                # all of the subsequent data will be added accordingly as well.
                # NOTE: Duplicate items will not be added since there is a check to see if the string exists
                # already and will not add if it does exist.
                if 'title' in usertoupdate['_source']:
                    current_titles = usertoupdate['_source']['title']
                    current_descriptions = usertoupdate['_source']['description']
                    current_descriptions_short = usertoupdate['_source']['description_short']
                    current_tags = usertoupdate['_source']['tags']
                    current_categories = usertoupdate['_source']['categories_text']
                    if listing['_source']['title'] not in current_titles:
                        current_titles.append(listing['_source']['title'])
                        if 'description' in listing['_source']:
                            if listing['_source']['description'] not in current_descriptions:
                                current_descriptions.append(listing['_source']['description'])
                        if 'description' in listing['_source']:
                            if listing['_source']['description'] not in current_descriptions:
                                current_descriptions_short.append(listing['_source']['description_short'])
                        if 'tags' in listing['_source']:
                            for taglist in listing['_source']['tags']:
                                if taglist['name'] not in current_tags:
                                    current_tags.append(taglist['name'])
                        if 'categories' in listing['_source']:
                            for catlist in listing['_source']['categories']:
                                if catlist['title'] not in current_categories:
                                    current_categories.append(catlist['title'])
                    # else: The else clause is not needed to do anything as it means the listing is already added.
                    #     logger.debug("= Listing already added title: {} =".format(listing['_source']['title']))
                else:
                    # If a title is not present in the record, then that means that no text information
                    # has been added to the record and we can start off fresh with the text to be added.
                    current_titles.append(listing['_source']['title'])
                    current_descriptions.append(listing['_source']['description'])
                    current_descriptions_short.append(listing['_source']['description_short'])
                    if 'tags' in listing['_source']:
                        for taglist in listing['_source']['tags']:
                            if taglist['name'] not in current_tags:
                                current_tags.append(taglist['name'])
                    if 'categories' in listing['_source']:
                        for catlist in listing['_source']['categories']:
                            if catlist['title'] not in current_categories:
                                current_categories.append(catlist['title'])

                # Based on the information from the checks above we can now submit the changes that we are proposing
                # to make to add the data to the User Profile so that it can be used in creating a content search.
                user_update_query = es_client.update(
                   index=settings.ES_RECOMMEND_USER,
                   doc_type=settings.ES_RECOMMEND_TYPE,
                   id=usertoupdate['_id'],
                   refresh=True,
                   body={"doc": {
                       "title": current_titles,
                       "description": current_descriptions,
                       "description_short": current_descriptions_short,
                       "tags": current_tags,
                       "categories_text": current_categories
                       }
                   })
                # Log a message when the update fails:
                if user_update_query['_shards']['failed'] > 0:
                    logger.info("= ES Content Based failed to update: {} =".format(user_update_query))

        # logger.info("= ES Content Based Recommendation - Initialization Complete =")

    def recommendation_logic(self):
        """
        Recommendation logic

        Template Code to make sure that Elasticsearch client is working
        This code should be replace by real algorthim
        """
        logger.info('Elasticsearch Content Base Recommendation Engine')
        logger.info('Elasticsearch Health : {}'.format(es_client.cluster.health()))

        # 10,000 is the max query size if there are more than 10,000 listings
        # then need to split the queries.  Currently this might be too much
        # overhead and hence the reason for not implementing in this implementation.
        query_size = {"size": self.RESULT_SIZE}

        # Get list of records from Listings table that fit the criteria needed to add information to the User
        # Profiles to create a match for content.
        es_profile_result = es_client.search(
            index=settings.ES_RECOMMEND_USER,
            body=query_size
        )

        # Filter the results to only the actual results:
        profiles_only = es_profile_result['hits']['hits']

        # For each profile in the return list we will cycle through the items necessary below to
        # add the necessary items to the search string to perform the comparison for matches:
        # First: What happens is that the categories filter items will match the items in the current categories that
        # the user has items bookmarked or reviewed.
        # Second: The title, descrition and description_short are added to respective multi_match queries and each items
        # in the list is added to a separate query.  The multi_match purpose is to search the same string across all of the fields
        # that we have listed.  This is needed since accurate results were not being obtained when all of the strings were combined
        # into one long string.  It also allows for an easier way to debug queries if there is ever a need.
        for each_profile in profiles_only:
            each_profile_source = each_profile['_source']
            query_object = []

            # Add categories to query to try and limit the results:
            categories_to_query = {}
            if 'categories' in each_profile_source:
                categories_to_query = {
                    "nested": {
                        "path": "categories",
                        "query": {
                            "bool": {
                                "should": [
                                    {"terms": {"categories.id": each_profile_source['categories']}}
                                ]
                            }
                        }
                    }
                }
                query_object.append(categories_to_query)

            # Add title to the query:
            if 'title' in each_profile_source:
                title_list = {}
                for items in each_profile_source['title']:
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
            if 'description' in each_profile_source:
                for items in each_profile_source['description']:
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
            if 'description_short' in each_profile_source:
                for items in each_profile_source['description_short']:
                    description_short_list = {
                        "multi_match": {
                            "query": items,
                            "type": "cross_fields",
                            "fields": ["title", "description", "description_short"],
                            "minimum_should_match": "20%"
                        }
                    }
                    query_object.append(description_short_list)

            query_compare = {}

            # Add a restriction to remove bookmarked apps from the query if they are present in
            # the profile.  This will eliminate unnecessary items to be queried:
            # The reason that the size is so large is because we do not want to limit the results to just a few
            # which then might be eleiminated when displayed to the user.  Hence the max result set is returned.
            if 'bookmark_ids' in each_profile_source:
                query_compare = {
                    "size": self.RESULT_SIZE,
                    "_source": ["id", "title", "description", "description_short", "agency_short_name", "categories"],
                    "query": {
                        "bool": {
                            "must_not": {
                                "terms": {"id": each_profile_source['bookmark_ids']}
                            },
                            "should": [
                                query_object
                            ]
                        }
                    }
                }
            else:
                # If no bookmarks then continue with getting the results:
                query_compare = {
                    "size": self.RESULT_SIZE,
                    "_source": ["id", "title", "description", "description_short", "agency_short_name", "categories"],
                    "query": {
                        "bool": {
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
            # Get only the results necessary from the returned JSON object:
            recommended_items = es_query_result['hits']['hits']

            # Skip if no results are returned as a precaution
            # Max score for Elasticsearch Content Based Recommendation to nomalize the data:
            if recommended_items:
                max_score_es_content = es_query_result['hits']['max_score'] + self.content_norm_factor * es_query_result['hits']['max_score']

            # Get the author so that it can be used in later items:
            profile_id = each_profile['_source']['author_id']
            # print("PROFITLE lookng up: ", profile_id)

            # Loop through all of the items and add them to the recommendation list for Content Based Filtering:
            for indexitem in recommended_items:
                score = recommend_utils.map_numbers(indexitem['_score'], 0, max_score_es_content, self.min_new_score, self.max_new_score)
                itemtoadd = indexitem['_source']['id']
                self.add_listing_to_user_profile(profile_id, itemtoadd, score, False)

        # New User problem and using search terms to recommend items should be done dynamically.  Since we do
        # not have dynamic support as of yet, the New User problem is being solved by going through and getting an aggregation of
        # the top terms in the titles of users that have recommendations and building a proposed list based on a search from
        # those results.  This is more of a hybrid approach for the new user problem, but should be corrected when on demand
        # searching is completed.  so the TODO: After implemention of dynamic searching based on user input for content, this code
        # might need to be modified or removed accordingly.  Hence the reason that it is separated out explicitly:

        # *START NEW USER TEMPORARY WORKAROUND* until dynamic engine is implemented:
        logger.info("= ES CONTENT RECOMMENDER NEW USER RECOMMENDATION CREATION =")
        # For users that do not have a recommendation profile need to create a new user recommendation:
        all_profiles = models.Profile.objects.all()

        # Setup parameters so that Elasticsearch results do not need to be performed multiple times when it is not needed:
        performed_search_request = False
        content_search_term = {}
        title_to_search_list = []
        new_user_return_list = []

        # The New User or Person that has no recommendation profile problem is solved by aggregating the results of all of the titles
        # that are present and then taking the top hits and searching for content based on those items.  This in turn creates content
        # based on the most popular titles that have been bookmarked and are in the recommendations tables already.
        for profile in all_profiles:
            # user_information = model_access.get_profile_by_id(profile.id)
            search_query = {
                "query": {
                    "term": {
                        "author_id": profile.id
                        }
                }
            }
            profile_id = profile.id
            # print("Profile ID: ", profile_id)

            # Create Search string to determine if profile exists in the Elasticsearch profile:
            search_result = es_client.search(
                index=settings.ES_RECOMMEND_USER,
                body=search_query
            )

            # Check to see if the user has a profile already that exists
            # in the Recommended Users.  If so then no need to perform another search
            # and can skip the rest of this for the current user:
            if search_result['hits']['total'] == 0:
                # If the user has not had any bookmarked items or rated items then need to perform a search
                # based on other user information, but only using aggregations of the titles in their profiles.
                # Perform this only once since it will be the same for all of the users without a profile:
                if not performed_search_request:
                    # Create a search query to get a list of aggregations for users:
                    content_search_term = {
                        "size": 0,
                        "aggs": {
                            "most_common_titles": {
                                "significant_terms": {
                                    "field": "title"
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
                    max_result_set_new_user = 25
                    query_compare = {
                        "size": max_result_set_new_user,
                        "_source": ["id", "title"],
                        "query": {
                            "bool": {
                                "should": [
                                    title_to_search_list
                                ]
                            }
                        }
                    }

                    # Get the results from the query:
                    es_query_result = es_client.search(
                        index=settings.ES_INDEX_NAME,
                        body=query_compare
                    )

                    # Max score for Elasticsearch Content Based Recommendation for new user to orient list against:
                    max_score_es_content = es_query_result['hits']['max_score'] + self.content_norm_factor * es_query_result['hits']['max_score']

                    # Store the results for the new users in the new_user_return_list:
                    new_user_return_list = es_query_result['hits']['hits']
                    # Set the search parameter to True so that subsequent searches will not be performed:
                    performed_search_request = True

                # Add recommended items based on content to user profile list:
                for indexitem in new_user_return_list:
                    score = recommend_utils.map_numbers(indexitem['_score'], 0, max_score_es_content, self.min_new_score, self.max_new_score)
                    itemtoadd = indexitem['_source']['id']
                    self.add_listing_to_user_profile(profile_id, itemtoadd, score, False)

                # logger.info("= ES CONTENT RECOMMENDER Engine Completed Results for New User {} =".format(profile_id))
        # *END NEW USER TEMPORARY WORKAROUND*:

        logger.info("= ES CONTENT RECOMMENDATION Results Completed =")
        ############################
        # END ES CONTENT BASED RECOMMENDATION
        ############################


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
    """

    friendly_name = 'Elasticsearch User Based Filtering'
    # The weights that are returned by Elasticsearch will be 0.X and hence the reason that we need to normalize the data.
    # Normailization is accomplished by moving the scale to be comprable with other engines using map_numbers function.
    # Reasoning: Results of scores are between 0 and 1 with results mainly around 0.0X, thus the normalization is necessary.
    recommendation_weight = 1.0  # Weight that the overall results are multiplied against.  The rating for user based is less than 1.
    # Results are between 0 and 1 and then converted to between min_new_score and max_new_score and then are multiplied by the weight
    # to be slightly better than the baseline recommendation systems if necessary.
    MIN_ES_RATING = 3.5  # Minimum rating to have results meet before being recommended for ES Recommender Systems
    min_new_score = 5  # Min value to set for rebasing of results
    max_new_score = 10  # Max value to rebase results to so that values

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
        # logger.info('Elasticsearch User Base Recommendation Engine: Loading data from Review model')
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
                        "author": {
                            "type": "string",
                            "analyzer": "english"
                        },
                        "title": {
                            "type": "string",
                            "analyzer": "english"
                        },
                        "description": {
                            "type": "string",
                            "analyzer": "english"
                        },
                        "description_short": {
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
        # Need to wait 1 second for index to get created according to search results.  This could be caused because of
        # time issues hitting a remote elasticsearch host:
        time.sleep(1)

        # Log a message if the update fails for creating a Elasticsearch index:
        if connect_es_record_exist['acknowledged'] is False:
            logger.info("Creating ES Index after Deletion Result: '{}'".format(connect_es_record_exist))

        ratings_items = []
        for record in reviews_listing_uname:
            # Get Username for profile:
            user_information = model_access.get_profile_by_id(record[3])
            username = user_information.user.username

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

            # Get Username for profile:
            user_information = model_access.get_profile_by_id(record[3])
            username = user_information.user.username

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

            ratings_items.append({"listing_id": record[1], "rate": record[2], "listing_categories": category_items})

            categories_to_look_up = category_items
            record_to_update = None
            if es_search_result['hits']['total'] == 0:
                # If record does not exist in Recommendation List, then create it:
                result_es = es_client.create(
                    index=settings.ES_RECOMMEND_USER,
                    doc_type=settings.ES_RECOMMEND_TYPE,
                    id=record[0],
                    refresh=True,
                    body={
                        "author_id": record[3],
                        "author": username,
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
                categories_to_look_up = list(set(current_categories + category_items))

                result_es = es_client.update(
                   index=settings.ES_RECOMMEND_USER,
                   doc_type=settings.ES_RECOMMEND_TYPE,
                   id=record_to_update,
                   refresh=True,
                   body={"doc": {
                       "ratings": new_ratings,
                       "categories": categories_to_look_up
                       }
                   })

            if result_es['_shards']['failed'] > 0:
                logger.info("Creating/Updating Record Failed: '{}'".format(result_es))

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

        logger.info('= Elasticsearch User Base Recommendation Engine =')
        # logger.info('Elasticsearch Health : {}'.format(es_client.cluster.health()))

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

        # Retreive all of the profiles from database:
        all_profiles = models.Profile.objects.all()

        for profile in all_profiles:
            # ID to adivse on recommendation:
            profile_id = profile.id

            # Retrieve Bookmark App Listings for user:
            bookmarked_apps = models.ApplicationLibraryEntry.objects.for_user(profile.user.username)
            bookmarked_list = []
            bookmarked_list_text = []
            for bkapp in bookmarked_apps:
                listing_id_query = {
                    "query": {
                        "term": {
                            "id": bkapp.listing.id
                        }
                    }
                }
                listings_to_load_request = es_client.search(
                    index=settings.ES_INDEX_NAME,
                    body=listing_id_query
                )
                # print("******************************************")
                # print("ITEM LISTING INFO: ", listings_to_load_request)
                # print("******************************************")
                # print("ITEM LISTING INFO: ", listings_to_load_request['hits']['hits'][0]['_source']['title'])
                bookmarked_list_text.append(listings_to_load_request['hits']['hits'][0]['_source']['title'])
                bookmarked_list.append(bkapp.listing.id)

            # print("Bookmarked Apps: ", bookmarked_list)

            # Get Username for profile:
            user_information = model_access.get_profile_by_id(profile_id)
            username = user_information.user.username

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
                            "author": username,
                            "bookmark_ids": bookmarked_list,
                            "categories": category_items
                        })
                    # logger.info("Bookmarks Created for profile: {} with result: {}".format(profile_id, result_es))
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
                    if result_es['_shards']['failed'] > 0:
                        logger.info("= ES User Based Bookmark and Category Update failed: {} =".format(result_es))

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

            recommended_items = es_query_result['aggregations']['the_listing']['aggs']['buckets']

            # Need to skip users that do not return any results as there will be no recommended_items to go through:
            if recommended_items:
                max_score_es_user = recommended_items[0]['score']

            # Add items to recommended list for the profile:
            for indexitem in recommended_items:
                score = recommend_utils.map_numbers(indexitem['score'], 0, max_score_es_user, self.min_new_score, self.max_new_score)
                # print("INDEX ITEM: ", indexitem)
                # print('Key {}, Score {}'.format(indexitem['key'], score))
                self.add_listing_to_user_profile(profile_id, indexitem['key'], score, False)

            # logger.info("= ES USER RECOMMENDER Engine Completed Results for {} =".format(profile_id))
            # logger.info("Creating/Updating Record Result: '{}'".format(es_query_result))
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
