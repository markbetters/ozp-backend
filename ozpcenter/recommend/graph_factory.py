"""
Graph Factory
Make different graphs
"""
from ozpcenter import models
from ozpcenter.recommend.graph import Graph


class GraphFactory(object):
    """
    Create different graph
    """
    @staticmethod
    def create_graph_template():
        graph = Graph()
        graph.add_vertex()
        return graph

    @staticmethod
    def create_graph_test_3v_2e():
        graph = Graph()
        vertex1 = graph.add_vertex('person', {'username': 'first last'})
        vertex2 = graph.add_vertex('listing', {'title': 'Skyzone1'})
        vertex3 = graph.add_vertex('listing', {'title': 'Skyzone2'})
        vertex1.add_edge('personListing', vertex2)
        vertex1.add_edge('personListing', vertex3)

        return graph

    @staticmethod
    def load_db_into_graph():
        """
        Load Django Database into graph

        Agency <--stewardedAgency--
        Agency <--agency--          Profile --bookmarked--> Listing --listingCategory--> Category
                                                                    --listingAgency--> Agency

        Steps:
            Load all Category
            Load all Agency
            Load all Listings
                Link to Agency
                Link to Category
            Load all Profiles
                Link to Agency
                Link bookmarked listings
        """
        graph = Graph()

        for category in models.Category.objects.all():
            data = {'title': category.title}
            added_vertex = graph.add_vertex('category', data, current_id='c-{}'.format(category.pk))

        for agency in models.Agency.objects.all():
            data = {'title': agency.title,
                    'short_name': agency.short_name}
            added_vertex = graph.add_vertex('agency', data, current_id='a-{}'.format(agency.pk))

        for listing in models.Listing.objects.all():
            data = {'title': listing.title,
                    'description': listing.description,
                    'is_private': listing.is_private,
                    'security_marking': listing.security_marking,
                    'is_enabled': listing.is_enabled,
                    'is_deleted': listing.is_deleted,
                    'is_featured': listing.is_featured,
                    'approval_status': listing.approval_status}

            added_vertex = graph.add_vertex('listing', data, current_id='l-{}'.format(listing.pk))

            # One Agency per listing
            current_agency = listing.agency
            added_vertex.add_edge('listingAgency', graph.get_vertex('a-{}'.format(current_agency.pk)))

            # Many Categories per listing
            for current_category in listing.categories.all():
                added_vertex.add_edge('listingCategory', graph.get_vertex('c-{}'.format(current_category.pk)))

        for profile in models.Profile.objects.all():
            data = {'username': profile.user.username,
                    'highest_role': profile.highest_role()}
            added_vertex = graph.add_vertex('profile', data, current_id='p-{}'.format(profile.pk))

            # Many Agencies per profile
            for current_agency in profile.organizations.all():
                added_vertex.add_edge('agency', graph.get_vertex('a-{}'.format(current_agency.pk)))

            # Many Agencies per profile
            for current_agency in profile.stewarded_organizations.all():
                added_vertex.add_edge('stewardedAgency', graph.get_vertex('a-{}'.format(current_agency.pk)))

        return graph
