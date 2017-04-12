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

from ozpcenter import models
from ozpcenter.api.listing import model_access_es
from ozpcenter.api.listing.model_access_es import check_elasticsearch
from ozpcenter.recommend import recommend_utils
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


class CustomHybridRecommender(Recommender):
    """
    Custom Hybrid Recommender

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
        logger.debug('Elasticsearch User Base Recommendation Engine')
        logger.debug('Elasticsearch Health : {}'.format(es_client.cluster.health()))


class GraphCollaborativeFilteringBaseRecommender(Recommender):
    """
    Graph Collaborative Filtering based on Bookmarkes
    """
    friendly_name = 'Bookmark Collaborative Filtering'
    recommendation_weight = 2.0

    def initiate(self):
        """
        Initiate any variables needed for recommendation_logic function
        """
        pass

    def recommendation_logic(self):
        """
        Recommendation logic
        """
        pass


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
            'graph_cf': GraphCollaborativeFilteringBaseRecommender,
            'elasticsearch_user_base': ElasticsearchUserBaseRecommender,
            'elasticsearch_content_base': ElasticsearchContentBaseRecommender,
            'sample_data': SampleDataRecommender,
            'custom': CustomHybridRecommender
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

            self.merge(friendly_name, recommendation_weight, recommendations_results, recommendations_time)

        start_db_ms = time.time() * 1000.0
        self.save_to_db()
        end_db_ms = time.time() * 1000.0
        logger.info('Save to database took: {} ms'.format(end_db_ms - start_db_ms))
        logger.info('Whole Process: {} ms'.format(end_db_ms - start_ms))

    def save_to_db(self):
        """
        This function is responsible for storing the recommendations into the database
        """
        for profile_id in self.recommender_result_set:
            # print('*-*-*-*-'); import json; print(json.dumps(self.recommender_result_set[profile_id])); print('*-*-*-*-')

            profile = None
            try:
                profile = models.Profile.objects.get(pk=profile_id)
            except ObjectDoesNotExist:
                profile = None

            if profile:
                # Clear Recommendations Entries before putting new ones.
                models.RecommendationsEntry.objects.filter(target_profile=profile).delete()

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

                recommendations_entry = models.RecommendationsEntry(target_profile=profile,
                                                                    recommendation_data=msgpack.packb(self.recommender_result_set[profile_id]))
                recommendations_entry.save()
