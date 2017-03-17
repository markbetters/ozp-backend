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

    def test_load_db_into_graph(self):
        graph = GraphFactory.load_db_into_graph()
        self.assertEqual(str(graph), 'Graph(vertices: 158, edges: 402)')

        bigbrother_dict = graph.query().v('p-1').to_dict().next()
        expected_dict = {'highest_role': 'APPS_MALL_STEWARD', 'username': 'bigbrother'}
        self.assertEqual(bigbrother_dict, expected_dict)

        bigbrother_bookmarks = graph.query().v('p-1').out('bookmarked').id().to_list()
        expected_bookmarks = ['l-11']
        self.assertEqual(bigbrother_bookmarks, expected_bookmarks)
