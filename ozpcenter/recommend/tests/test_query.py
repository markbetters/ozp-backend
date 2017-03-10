"""
Make sure that Pipe and Pipeline classes work
"""
from django.test import TestCase

from ozpcenter.scripts import sample_data_generator as data_gen
from ozpcenter.recommend.graph import Graph
from ozpcenter.recommend.graph_factory import GraphFactory


class GraphQueryTest(TestCase):

    def setUp(self):
        """
        setUp is invoked before each test method
        """
        self.graph = Graph()
        self.graph.add_vertex('test_label', {'test_field': 1})
        self.graph.add_vertex('test_label', {'test_field': 2})
        self.graph.add_vertex('test_label', {'test_field': 12, 'time': 'now'})

        self.graph2 = Graph()
        self.vertex1 = self.graph2.add_vertex('person', {'username': 'first last'}, current_id=10)
        self.vertex2 = self.graph2.add_vertex('listing', {'title': 'Skyzone1'}, current_id=20)
        self.vertex3 = self.graph2.add_vertex('listing', {'title': 'Skyzone2'}, current_id=30)
        self.vertex1.add_edge('personListing', self.vertex2)
        self.vertex1.add_edge('personListing', self.vertex3)

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the whole TestCase (only run once for the TestCase)
        """
        data_gen.run()

    def test_graph_query_builder(self):
        query = self.graph.query().V()
        self.assertEqual(str(query), "[GraphVertexPipe()]")

    def test_graph_query_builder_chain(self):
        query = self.graph.query().V().to_dict()
        self.assertEqual(str(query), "[GraphVertexPipe(), ElementPropertiesPipe(internal:False)]")

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

    def test_graph_query_v_to_list(self):
        query = self.graph2.query().v(10).id()
        all_vertices = query.to_list()
        output = [10]
        self.assertEqual(all_vertices, output)

        query = self.graph2.query().v(10, 20).id()
        all_vertices = query.to_list()
        output = [10, 20]
        self.assertEqual(all_vertices, output)

    def test_graph_query_v_out_to_list(self):
        query = self.graph2.query().v(10).out().id()
        all_vertices = query.to_list()
        output = [20, 30]
        self.assertEqual(all_vertices, output)

        query = self.graph2.query().v(20).out().id()
        all_vertices = query.to_list()
        output = []
        self.assertEqual(all_vertices, output)

    def test_graph_sample_profile_listing_in(self):
        graph = GraphFactory.load_sample_profile_listing_graph()
        self.assertEqual(str(graph), 'Graph(vertices: 13, edges: 15)')

        query_results = graph.query().v('l-1').id().to_list()
        output = ['l-1']
        self.assertEqual(query_results, output)

        query_results = graph.query().v('l-1').in_('bookmarked').id().to_list()
        output = ['p-1', 'p-2', 'p-3']
        self.assertEqual(query_results, output)

        query_results = graph.query().v('l-1', 'l-2', 'l-3').id().to_list()
        output = ['l-1', 'l-2', 'l-3']
        self.assertEqual(query_results, output)

    def test_graph_sample_profile_listing(self):
        graph = GraphFactory.load_sample_profile_listing_graph()
        self.assertEqual(str(graph), 'Graph(vertices: 13, edges: 15)')

        query_results = graph.query().v('p-1').id().to_list()
        output = ['p-1']
        self.assertEqual(query_results, output)

        query_results = graph.query().v('p-1').out('bookmarked').id().to_list()
        output = ['l-1', 'l-2', 'l-3']
        self.assertEqual(query_results, output)

        query_results = graph.query().v('p-1').out('bookmarked').in_('bookmarked').id().to_list()
        output = ['p-1', 'p-2', 'p-3', 'p-3', 'p-1', 'p-4', 'p-5', 'p-1', 'p-5']
        self.assertEqual(query_results, output)

        query_results = graph.query().v('p-1').out('bookmarked').in_('bookmarked').id().distinct().to_list()
        output = ['p-1', 'p-2', 'p-3', 'p-4', 'p-5']
        self.assertEqual(query_results, output)

        query_results = graph.query().v('p-1').out('bookmarked').in_('bookmarked').distinct().id().to_list()
        output = ['p-1', 'p-2', 'p-3', 'p-4', 'p-5']
        self.assertEqual(query_results, output)

        query_results = graph.query().v('p-1').out('bookmarked').in_('bookmarked').distinct().exclude_ids(['p-1']).id().to_list()
        output = ['p-2', 'p-3', 'p-4', 'p-5']
        self.assertEqual(query_results, output)
