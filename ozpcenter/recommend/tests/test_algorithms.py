"""
Make sure that Pipe and Pipeline classes work
"""
from django.test import TestCase

from ozpcenter.scripts import sample_data_generator as data_gen
from ozpcenter.recommend.graph_factory import GraphFactory


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

        output = ['l-4', 'l-5', 'l-6', 'l-8', 'l-7']
        self.assertEqual(results, output)
