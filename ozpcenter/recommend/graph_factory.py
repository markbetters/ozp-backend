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
    def load_sample_profile_listing_graph():
        graph = Graph()
        profile1 = graph.add_vertex('profile', {'username': 'first1 last'}, current_id='p-1')
        profile2 = graph.add_vertex('profile', {'username': 'first2 last'}, current_id='p-2')
        profile3 = graph.add_vertex('profile', {'username': 'first3 last'}, current_id='p-3')
        profile4 = graph.add_vertex('profile', {'username': 'first4 last'}, current_id='p-4')
        profile5 = graph.add_vertex('profile', {'username': 'first5 last'}, current_id='p-5')

        listing1 = graph.add_vertex('listing', {'title': 'listing1'}, current_id='l-1')
        listing2 = graph.add_vertex('listing', {'title': 'listing2'}, current_id='l-2')
        listing3 = graph.add_vertex('listing', {'title': 'listing3'}, current_id='l-3')
        listing4 = graph.add_vertex('listing', {'title': 'listing4'}, current_id='l-4')
        listing5 = graph.add_vertex('listing', {'title': 'listing5'}, current_id='l-5')
        listing6 = graph.add_vertex('listing', {'title': 'listing6'}, current_id='l-6')
        listing7 = graph.add_vertex('listing', {'title': 'listing7'}, current_id='l-7')
        listing8 = graph.add_vertex('listing', {'title': 'listing8'}, current_id='l-8')

        category1 = graph.add_vertex('category', {'title': 'category1'}, current_id='c-1')
        category2 = graph.add_vertex('category', {'title': 'category2'}, current_id='c-2')

        listing1.add_edge('listingCategory', category1)
        listing2.add_edge('listingCategory', category2)
        listing3.add_edge('listingCategory', category1)
        listing4.add_edge('listingCategory', category2)

        listing5.add_edge('listingCategory', category1)
        listing6.add_edge('listingCategory', category2)
        listing7.add_edge('listingCategory', category1)
        listing8.add_edge('listingCategory', category2)

        profile1.add_edge('bookmarked', listing1)
        profile1.add_edge('bookmarked', listing2)
        profile1.add_edge('bookmarked', listing3)

        profile2.add_edge('bookmarked', listing1)
        profile2.add_edge('bookmarked', listing4)
        profile2.add_edge('bookmarked', listing5)

        profile3.add_edge('bookmarked', listing1)
        profile3.add_edge('bookmarked', listing2)
        profile3.add_edge('bookmarked', listing5)
        profile3.add_edge('bookmarked', listing6)
        profile3.add_edge('bookmarked', listing8)

        profile4.add_edge('bookmarked', listing2)
        profile4.add_edge('bookmarked', listing7)

        profile5.add_edge('bookmarked', listing2)
        profile5.add_edge('bookmarked', listing3)

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

            if listing.is_enabled and not listing.is_deleted and listing.approval_status == models.Listing.APPROVED:
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

            # Many stewardedAgency Agencies per profile
            for current_agency in profile.stewarded_organizations.all():
                added_vertex.add_edge('stewardedAgency', graph.get_vertex('a-{}'.format(current_agency.pk)))

            for current_entry in models.ApplicationLibraryEntry.objects.filter(owner=profile):
                current_listing = current_entry.listing
                data = {'folder_name': current_entry.folder}
                added_vertex.add_edge('bookmarked', graph.get_vertex('l-{}'.format(current_listing.pk)), data)

        return graph
