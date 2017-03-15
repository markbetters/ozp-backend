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
    30,000 Users
    300 Listings

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

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count

from ozpcenter import models
from ozpcenter.api.listing import model_access_es
from ozpcenter.api.listing.model_access_es import check_elasticsearch
from ozpcenter.recommend import utils
# from ozpcenter.recommend.graph_factory import GraphFactory


# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))

# Create ES client
es_client = model_access_es.es_client


class Recommender(object):
    """
    This class is to behave like a superclass for recommendation engine
    """

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
        print('--------')
        print(self.recommender_result_set)
        print('--------')
        print('Recommendation Logic took: {} ms'.format(recommendation_ms - start_ms))
        return self.recommender_result_set


class SampleDataRecommender(Recommender):
    """
    Sample Data Recommender
    """

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
            print('Calculating Profile {}/{}'.format(current_profile_count, all_profiles_count))

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
            # library_entries = library_entries.filter(owner__user__username=username)
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

                calculation = utils.map_numbers(count, old_min, old_max, new_min, new_max)
                self.add_listing_to_user_profile(profile_id, listing_id, calculation, True)


class ElasticsearchContentBaseRecommender(Recommender):
    """
    Elasticsearch Content based recommendation engine
    """

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
        print('Elasticsearch Content Base Recommendation Engine')
        print('Elasticsearch Health : {}'.format(es_client.cluster.health()))


class ElasticsearchUserBaseRecommender(Recommender):
    """
    Elasticsearch User based recommendation engine
    """

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
        print('Elasticsearch User Base Recommendation Engine')
        print('Elasticsearch Health : {}'.format(es_client.cluster.health()))


class GraphCollaborativeFilteringBaseRecommender(Recommender):
    """
    Graph Collaborative Filtering based on Bookmarkes
    """

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

    def _merge_add_entry(self, profile_id, listing_id, score):
        """
        Merge the results together
        When there is a conflict in the profile/listing/score, average the two scores together
        """
        if profile_id in self.recommender_result_set:
            if self.recommender_result_set[profile_id].get(listing_id):
                self.recommender_result_set[profile_id][listing_id] = (self.recommender_result_set[profile_id][listing_id] + float(score)) / 2
            else:
                self.recommender_result_set[profile_id][listing_id] = float(score)
        else:
            self.recommender_result_set[profile_id] = {}
            self.recommender_result_set[profile_id][listing_id] = float(score)

    def merge(self, recommender_result_set):
        """
        Purpose is to merge all of the different Recommender's algorthim recommender result together.
        This function is responsible for merging the results of the other Recommender recommender_result_set diction into self recommender_result_set

        Self recommender_result_set
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

        Other recommender_result_set:
        {
            profile_id#3: {
                listing_id#1: score#1,
                listing_id#2: score#2
            },
            profile_id#1: {
                listing_id#5: score#1,
            }
        }

        Merged recommender_result_set
        {
            profile_id#1: {
                listing_id#1: score#1,
                listing_id#2: score#2,
                listing_id#5: score#3,
            },
            profile_id#2: {
                listing_id#1: score#1,
                listing_id#2: score#2,
                listing_id#3: score#3,
            },
            profile_id#3: {
                listing_id#1: score#1,
                listing_id#2: score#2
            },
        }
        """
        if recommender_result_set is None:
            return False
        for profile_id in recommender_result_set:
            for listing_id in recommender_result_set[profile_id]:
                score = recommender_result_set[profile_id][listing_id]
                self._merge_add_entry(profile_id, listing_id, score)
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
            print('======{}======='.format(current_recommender_obj.__class__.__name__))
            recommender_obj = current_recommender_obj
            self.merge(recommender_obj.recommend())
            print('=============')

        start_db_ms = time.time() * 1000.0
        self.save_to_db()
        end_db_ms = time.time() * 1000.0
        print('Save to database took: {} ms'.format(end_db_ms - start_db_ms))
        print('Whole Process: {} ms'.format(end_db_ms - start_ms))

    def save_to_db(self):
        """
        This function is responsible for storing the recommendations into the database
        """
        for profile_id in self.recommender_result_set:

            profile = None
            try:
                profile = models.Profile.objects.get(pk=profile_id)
            except ObjectDoesNotExist:
                profile = None

            if profile:
                # Clear Recommendations Entries before putting new ones.
                models.RecommendationsEntry.objects.filter(target_profile=profile).delete()

                listing_ids = self.recommender_result_set[profile_id]

                for current_listing_id in listing_ids:
                    score = listing_ids[current_listing_id]
                    current_listing = None
                    try:
                        current_listing = models.Listing.objects.get(pk=current_listing_id)
                    except ObjectDoesNotExist:
                        current_listing = None

                    if current_listing:
                        recommendations_entry = models.RecommendationsEntry(
                            target_profile=profile,
                            listing=current_listing,
                            score=score)
                        recommendations_entry.save()
