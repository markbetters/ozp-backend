"""
Make sure that Pipe and Pipeline classes work
"""
from django.test import override_settings
from django.test import TestCase

from ozpcenter.recommend.graph import Graph
from ozpcenter.scripts import sample_data_generator as data_gen


@override_settings(ES_ENABLED=False)
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

    def test_graph_three_vertices_simple(self):
        graph = Graph()
        vertex1 = graph.add_vertex('person', {'username': 'first last'}, current_id=10)
        vertex2 = graph.add_vertex('listing', {'title': 'Skyzone1'}, current_id=20)
        vertex3 = graph.add_vertex('listing', {'title': 'Skyzone2'}, current_id=30)
        vertex1.add_edge('personListing', vertex2)
        vertex1.add_edge('personListing', vertex3)
        vertex1.add_edge('testListing', vertex3)

        self.assertEqual(str(graph), 'Graph(vertices: 3, edges: 3)')
        # Check Vertex 1
        self.assertEqual(len(vertex1.get_in_edges('personListing')), 0)
        self.assertEqual([edge.label for edge in vertex1.get_in_edges('personListing')], [])
        self.assertEqual([edge.in_vertex.id for edge in vertex1.get_in_edges('personListing')], [])

        self.assertEqual(len(vertex1.get_out_edges('personListing')), 2)
        self.assertEqual(len(vertex1.get_out_edges()), 3)
        self.assertEqual([edge.label for edge in vertex1.get_out_edges('personListing')], ['personListing', 'personListing'])
        self.assertEqual([edge.out_vertex.id for edge in vertex1.get_out_edges('personListing')], [20, 30])

        # Check Vertex 2
        self.assertEqual(len(vertex2.get_in_edges('personListing')), 1)
        self.assertEqual([edge.label for edge in vertex2.get_in_edges('personListing')], ['personListing'])
        self.assertEqual([edge.in_vertex.id for edge in vertex2.get_in_edges('personListing')], [10])

        self.assertEqual(len(vertex2.get_out_edges('personListing')), 0)
        self.assertEqual([edge.label for edge in vertex2.get_out_edges('personListing')], [])
        self.assertEqual([edge.out_vertex.id for edge in vertex2.get_out_edges('personListing')], [])

        # Check Vertex 3
        self.assertEqual(len(vertex3.get_in_edges('personListing')), 1)
        self.assertEqual([edge.label for edge in vertex3.get_in_edges('personListing')], ['personListing'])
        self.assertEqual([edge.in_vertex.id for edge in vertex3.get_in_edges('personListing')], [10])

        self.assertEqual(len(vertex3.get_out_edges('personListing')), 0)
        self.assertEqual([edge.label for edge in vertex3.get_out_edges('personListing')], [])
        self.assertEqual([edge.out_vertex.id for edge in vertex3.get_out_edges('personListing')], [])
