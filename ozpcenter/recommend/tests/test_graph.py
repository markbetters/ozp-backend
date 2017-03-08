"""
Make sure that Pipe and Pipeline classes work
"""
from django.test import TestCase

from ozpcenter.scripts import sample_data_generator as data_gen
from ozpcenter.recommend.graph import Graph
#from ozpcenter.recommend.graph_factory import GraphFactory


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

    def test_graph_add_edit_one_vertex(self):
        graph = Graph()
        self.assertEqual(str(graph), 'Graph(vertices: 0, edges: 0)')

        added_vertex = graph.add_vertex('test_label', {'test_field': 1})

        self.assertEqual(str(graph), 'Graph(vertices: 1, edges: 0)')
        self.assertEqual(added_vertex.label, 'test_label')
        self.assertEqual(added_vertex.get_property('test_field'), 1)

        added_vertex.set_property('test_field', 2)
        added_vertex = graph.get_vertex(1)
        self.assertEqual(added_vertex.get_property('test_field'), 2)

        self.assertEqual(str(graph), 'Graph(vertices: 1, edges: 0)')

    def test_graph_add_two_vertex(self):
        graph = Graph()
        self.assertEqual(str(graph), 'Graph(vertices: 0, edges: 0)')

        added_vertex = graph.add_vertex('test_label', {'test_field': 1})

        self.assertEqual(str(graph), 'Graph(vertices: 1, edges: 0)')
        self.assertEqual(added_vertex.label, 'test_label')
        self.assertEqual(added_vertex.get_property('test_field'), 1)

        added_vertex = graph.add_vertex('test_label1', {'test_field': 2})

        self.assertEqual(str(graph), 'Graph(vertices: 2, edges: 0)')
        self.assertEqual(added_vertex.label, 'test_label1')
        self.assertEqual(added_vertex.get_property('test_field'), 2)

    def test_graph_add_two_vertex_edges(self):
        graph = Graph()
        vertex1 = graph.add_vertex('person', {'username': 'first last'})
        vertex2 = graph.add_vertex('listing', {'title': 'Skyzone1'})
        vertex3 = graph.add_vertex('listing', {'title': 'Skyzone2'})
        vertex1.add_edge('personListing', vertex2)
        vertex1.add_edge('personListing', vertex3)

        self.assertEqual(str(graph), 'Graph(vertices: 3, edges: 2)')
        # Check Vertex 1
        self.assertEqual(len(vertex1.get_in_edges('personListing')), 0)
        self.assertEqual(len(vertex1.get_out_edges('personListing')), 2)

        # Check Vertex 2
        self.assertEqual(len(vertex2.get_in_edges('personListing')), 1)
        self.assertEqual(len(vertex2.get_out_edges('personListing')), 0)

        # Check Vertex 3
        self.assertEqual(len(vertex3.get_in_edges('personListing')), 1)
        self.assertEqual(len(vertex3.get_out_edges('personListing')), 0)
