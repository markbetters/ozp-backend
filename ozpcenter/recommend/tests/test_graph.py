"""
Make sure that Pipe and Pipeline classes work
"""
from django.test import TestCase

from ozpcenter.scripts import sample_data_generator as data_gen
from ozpcenter.recommend.graph import Graph


class GraphTest(TestCase):

    def setUp(self):
        """
        setUp is invoked before each test method
        """
        pass

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the whole TestCase (only run once for the TestCase)
        """
        data_gen.run()

    def test_graph_add_vertex(self):
        graph = Graph()
        self.assertEqual(str(graph), 'Graph(current_id: 0, vertices: 0, edges: 0)')

        added_vertex = graph.add_vertex('test_label', {'test_field': 1})

        self.assertEqual(str(graph), 'Graph(current_id: 1, vertices: 1, edges: 0)')
        self.assertEqual(added_vertex.label, 'test_label')
        self.assertEqual(added_vertex.get_property('test_field'), 1)

        added_vertex.set_property('test_field', 2)
        added_vertex = graph.get_vertex(1)
        self.assertEqual(added_vertex.get_property('test_field'), 2)
