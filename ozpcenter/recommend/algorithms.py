"""
# Algorithms using query

## Collaborative filtering based on graph database

### Structure
Vertex Types:
Agency
    short_name

Profile
    profile_id
    username
    role: APPS_MALL_STEWARD > ORG_STEWARD > USER

Listing
    listing_id
    is_featured
    is_private
    total_reviews
    avg_rate

Category
    title

Include BookmarkedFolders ?
Include Review ?

Connections:
    Agency <--stewardedAgency--
    Agency <--agency--          Profile --bookmarked--> Listing --listingCategory--> Category
                                                                --listingAgency--> Agency


# Algorithm: Getting Most bookmarked listings across all profiles

graph.v('profile')  # Getting all Profiles
    .out('bookmarked') # Go to all Listings that all profiles has bookmarked
    # Group by Listings with Count (recommendation weight) and sort by count DSC

# Example Graph
                                                 +------------------+
                                                 |                  v
                                                 |
                                                 |              +----------+
                                                 |              |Listing 4 |
                                          +---------+           +----------+
                                         ++Profile 2+-------+
                                         +----------+       |
                      +----------+       |                  |
                      |Listing 1 |  <-^--+           +------->  +----------+
           +------->  +----------+    |              |          |Listing 5 |
           |                          |   +----------+          +----------+
           |                          +---+Profile 3+---+
           |                             +----------+   |
   +---------+        +----------+ <-----+              |
   |Profile 1+------> |Listing 2 |     |                |       +----------+
   +---------+        +----------+     |                +-----> |Listing 6 |
           |                           +------------+   |       +----------+
           |                           |  |Profile 4+-------+
           |                           |  +---------+   |   |
           |          +----------+     |                |   |
           +------->  |Listing 3 |     |                |   |   +----------+
                      +----------+     |                |   +-> |Listing 7 |
                             ^         |  +---------+   |       +----------+
                             |         +--+Profile 5|   |
                             +----------------------+   |
                                                        |
                                                        |       +----------+
                                                        +---->  |Listing 8 |
                                                                +----------+
Listing Categories:
Listing 1 - Category 1
Listing 2 - Category 1
Listing 3 - Category 2
Listing 4 - Category 2
Listing 5 - Category 2
Listing 6 - Category 3
Listing 7 - Category 3
Listing 8 - Category 1

# Issues
## Non-useful listings
Solution - Also Use listing categories to make recommendation for relevant to user

# New User Problem
We might have the New User Problem,
The way to solve this to get the results of a different recommendation engine (BaselineRecommender - GlobalBaseline)
recommendations = BaselineRecommender + GraphCollaborativeRecommender

# Other Algorithms
TODO: Figure out of MEASURING MEANINGFUL PROFILE-LISTING CONNECTIONS
https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-significantterms-aggregation.html
aggregation that returns interesting or unusual occurrences of terms in a set
"measures the kind of statistically significant relationships we need to deliver meaningful recommendations"

Might be able to figure out how to implement JLHScore/ChiSquare Scoring to python
https://github.com/elastic/elasticsearch/blob/master/core/src/main/java/org/elasticsearch/search/aggregations/bucket/significant/heuristics/JLHScore.java

JLHScore:
Calculates the significance of a term in a sample against a background of
normal distributions by comparing the changes in frequency.

ChiSquare:
"Information Retrieval", Manning et al., Eq. 13.19

Google Normalized Distance:
Calculates Google Normalized Distance, as described in "The Google Similarity Distance", Cilibrasi and Vitanyi, 2007
link: http://arxiv.org/pdf/cs/0412098v3.pdf
"""
from ozpcenter.recommend import recommend_utils


class GraphAlgoritms(object):

    def __init__(self, graph):
        self.graph = graph

    def recommend_listings_for_profile(self, profile_id):
        """
        Collaborative filtering:
        Getting Similar Listings via looking at other Profiles bookmarks

        Algorithm Steps:
            - Select 'profile 1' as start
            - Go to all Listings that 'profile 1' has bookmarked
            - Go to all Profiles that bookmarked the same listings as 'profile 1'
            - Filter out 'profile 1' from profile_username
            - Go to all Listings that other people has bookmarked (recommendations)
            - Filter out all listings that 'profile 1' has bookmarked
            - Group by Listings with Count (recommendation weight) and sort by count DSC

        TODO: Additions to improve relevance (usefull-ness to profile):
        For the results, sort by Category, then Agency

        Returns:
            [(listing_id, recommendation weight),
             (listing_id, recommendation weight) ....]
        """
        profile_ids = self.graph.query().v(profile_id).id().to_list()  # Get target profile id

        profile_listing_categories_ids = []

        profile_listing_ids = (self.graph.query()
                                   .v(profile_id)
                                   .out('bookmarked')
                                   .id().to_list())  # Get listings of target profile ids

        other_profiles_query = (self.graph.query()
                                    .v(profile_id).as_('start_profile')  # Select Start Profile
                                    .out('bookmarked').as_('start_listings')  # Go to all Listings that 'Start Profile' has bookmarked
                                    .side_effect(lambda current_vertex:
                                                 [profile_listing_categories_ids.append(current) for current in
                                                  current_vertex.query().out('listingCategory').id().to_list()])
                                    .in_('bookmarked')  # Go to all Profiles that bookmarked the same listings as 'Start Profile'
                                    .distinct().exclude_ids(profile_ids)  # Exclude 'Start Profile'
                                    .except_('start_profile')  # Exclude 'Start Profile' TODO: Make this work
                                    .out('bookmarked')  # Go to all Listings that other people has bookmarked (recommendations)
                                    .exclude_ids(profile_listing_ids)  # Filter out all listings that 'Start Profile' has bookmarked
                                    .except_('start_listings')  # Filter out all listings that 'Start Profile' has bookmarked
                                    .id()
                                )

        other_profiles_query_list = other_profiles_query.to_list()
        group_by_id_count = recommend_utils.list_to_group_count(other_profiles_query_list)

        # Group by Listings with Count (recommendation weight) and sort by count DSC
        sorted_listing_ids = sorted(group_by_id_count.items(), key=lambda x: (x[1], x[0]), reverse=True)

        return sorted_listing_ids
