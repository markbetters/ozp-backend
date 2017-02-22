"""
Recommender

https://github.com/aml-development/ozp-documentation/wiki/Recommender-%282017%29

Data Per User
- Listing Bookmarked

Keep track of folder apps

Recommendations are based on individual users

Steps:
    Load Data for each users
"""
from ozpcenter import models
from django.core.exceptions import ObjectDoesNotExist


class Recommender(object):
    """
    This class is to behave like a superclass for recommendation engine

    recommender_result_set: Dictionary with profile id, nested listing id with score pairs
        {
            profile_id#1: {
                listing_id#1: score#1,
                listing_id#2: score#2
            },
            profile_id#2: {
                listing_id#1: score#1,
                listing_id#2: score#2,
                listing_id#3: score#2,
            }
        }
    """
    def __init__(self):
        # Set up variables for processing data
        self.recommender_result_set = {}
        self.initiate()

    def initiate(self):
        raise NotImplementedError()

    def recommendation_logic(self):
        raise NotImplementedError()

    def merge(self):
        """
        This function is responsible for merging the results of the other Recommender RecommenderResultSet Object into self Object
        """
        pass

    def add_listing_to_user_profile(self, profile_id, listing_id, score):
        """
        Add listing and score to user profile
        """
        if profile_id in self.recommender_result_set:
            self.recommender_result_set[profile_id][listing_id] = score
        else:
            self.recommender_result_set[profile_id] = {}
            self.recommender_result_set[profile_id][listing_id] = score

    def recommend(self):
        """
        Execute recommendation logic
        """
        self.recommendation_logic()
        self.save_to_db()

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
                        current_listing = models.Listing.objects.get(pk=profile_id)
                    except ObjectDoesNotExist:
                        current_listing = None

                    if current_listing:
                        recommendations_entry = models.RecommendationsEntry(
                            target_profile=profile,
                            listing=current_listing,
                            score=score)
                        recommendations_entry.save()


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


class ElasticsearchContentBaseRecommender(Recommender):
    """
    Elasticsearch based recommendation engine
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


class ElasticsearchUserBaseRecommender(Recommender):
    """
    Elasticsearch based recommendation engine
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


class CrabUserBaseRecommender(Recommender):
    """
    Crab based recommendation engine
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
            'crab_user_base': CrabUserBaseRecommender,
            'elasticsearch_user_base': ElasticsearchUserBaseRecommender,
            'elasticsearch_content_base': ElasticsearchContentBaseRecommender,
            'sample_data': SampleDataRecommender
        }

    def recommend(self, recommender_string):
        """
        Creates Recommender Object, and excute the recommend
        """
        if recommender_string not in self.recommender_classes:
            raise Exception('Recommender Engine Not Found')

        recommender_obj = self.recommender_classes[recommender_string]()
        recommender_obj.recommend()
