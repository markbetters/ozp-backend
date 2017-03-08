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

    def test_load_db_into_graph(self):
        graph = GraphFactory.load_db_into_graph()
        # import pprint
        # print(pprint.pprint(graph.query().V().to_dict(internal=True).to_list()))
        self.assertEqual(str(graph), 'Graph(vertices: 149, edges: 363)')
