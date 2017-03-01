"""
Make sure that Pipe and Pipeline classes work
"""
from django.test import TestCase

from ozpcenter.scripts import sample_data_generator as data_gen
from ozpcenter.recommend.graph import Graph


class GraphQueryTest(TestCase):

    def setUp(self):
        """
        setUp is invoked before each test method
        """
        self.graph = Graph()
        self.graph.add_vertex('test_label', {'test_field': 1})
        self.graph.add_vertex('test_label', {'test_field': 2})
        self.graph.add_vertex('test_label', {'test_field': 12, 'time': 'now'})

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the whole TestCase (only run once for the TestCase)
        """
        data_gen.run()

    def test_graph_query_builder(self):
        query = self.graph.query().V()
        self.assertEqual(str(query), "['GraphVertexPipe({})']")

        query = self.graph.query().V().to_dict()
        self.assertEqual(str(query), "['GraphVertexPipe({})', 'ElementPropertiesPipe({})']")

    def test_graph_query_V_dict(self):
        query = self.graph.query().V().to_dict()
        all_vertices = query.to_list()

        output = [
            {'test_field': 1},
            {'test_field': 2},
            {'test_field': 12, 'time': 'now'}
        ]

        self.assertEqual(all_vertices, output)

    def test_graph_query_V_id(self):
        query = self.graph.query().V().id()
        all_vertices = query.to_list()

        output = [1, 2, 3]

        self.assertEqual(all_vertices, output)
