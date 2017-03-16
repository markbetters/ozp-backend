"""
Make sure that Pipe and Pipeline classes work
"""
from django.test import TestCase

from ozpcenter.recommend.graph_factory import GraphFactory
from ozpcenter.scripts import sample_data_generator as data_gen


class GraphTest(TestCase):

    def setUp(self):
        """
        setUp is invoked before each test method
        """
        pass

    @classmethod
    def setUpTestData(cls):
        """
        Set up test database for the whole TestCase (only run once for the TestCase)
        """
        data_gen.run()

    def test_graph_recommendation(self):
        graph = GraphFactory.load_sample_profile_listing_graph()
        results = graph.algo().recommend_listings_for_profile('p-1')

        output = [('l-5', 2), ('l-8', 1), ('l-7', 1), ('l-6', 1), ('l-4', 1)]

        self.assertEqual(results, output)

    def test_graph_recommendation_db(self):
        graph = GraphFactory.load_db_into_graph()
        results = graph.algo().recommend_listings_for_profile('p-1')  # bigbrother

        output = [('l-114', 1), ('l-113', 1), ('l-112', 1), ('l-1', 1)]

        self.assertEqual(results, output)
