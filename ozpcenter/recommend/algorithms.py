"""
Algorithm using query
"""


class GraphAlgoritms(object):

    def __init__(self, graph):
        self.graph = graph

    def recommend_listings_for_profile(self, profile_id):
        profile_ids = self.graph.query().v(profile_id).id().to_list()  # Get target profile id
        profile_listing_ids = self.graph.query().v(profile_id).out('bookmarked').id().to_list()  # Get listings of target profile ids

        # Out to listings
        # In to the profiles
        other_profiles_query = self.graph.query().v(profile_id).out('bookmarked') \
                                                               .in_('bookmarked') \
                                                               .distinct().exclude_ids(profile_ids)

        # Out to the listings
        other_profiles_listings = other_profiles_query.out('bookmarked') \
            .distinct().exclude_ids(profile_listing_ids).id()

        return other_profiles_listings.to_list()
