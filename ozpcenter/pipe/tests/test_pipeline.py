"""
Make sure that Pipe and Pipeline classes work

TODO: Make below code work
if not len_pipe.has_next():
    break
"""
from django.test import TestCase

from ozpcenter.scripts import sample_data_generator as data_gen
from ozpcenter.recommend import recommend_utils
from ozpcenter.pipe import pipes
from ozpcenter.pipe import pipeline
from ozpcenter.recommend.graph import Graph


class PipelineTest(TestCase):

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

    def test_pipe_cap(self):
        caps_pipe = pipes.CapitalizePipe()
        caps_pipe.set_starts(recommend_utils.ListIterator(['this', 'is', 'the', 'test']))

        list_out = []

        try:
            while caps_pipe.has_next():
                current_object = caps_pipe.next()
                list_out.append(current_object)
        except recommend_utils.FastNoSuchElementException:
            # Ignore FastNoSuchElementException
            pass

        self.assertEqual(list_out, ['THIS', 'IS', 'THE', 'TEST'])

    def test_pipeline_limit(self):
        pipeline_test = pipeline.Pipeline(recommend_utils.ListIterator([1, 2, 3, 4, 5, 6, 7]),
                                          [pipes.LimitPipe(5)])

        self.assertEqual(pipeline_test.to_list(), [1, 2, 3, 4, 5])

        pipeline_test = pipeline.Pipeline(recommend_utils.ListIterator([1, 2, 3, 4, 5, 6, 7]),
                                          [pipes.LimitPipe(2)])

        self.assertEqual(pipeline_test.to_list(), [1, 2])

        pipeline_test = pipeline.Pipeline(recommend_utils.ListIterator([1, 2, 3]),
                                          [pipes.LimitPipe(5)])

        self.assertEqual(pipeline_test.to_list(), [1, 2, 3])

    def test_pipe_cap_len_chain(self):
        caps_pipe = pipes.CapitalizePipe()
        len_pipe = pipes.LenPipe()

        caps_pipe.set_starts(recommend_utils.ListIterator(['this', 'is', 'the', 'test']))
        len_pipe.set_starts(caps_pipe)

        list_out = []

        try:
            while len_pipe.has_next():  # Make this refresh has loop
                current_object = len_pipe.next()
                list_out.append(current_object)
        except recommend_utils.FastNoSuchElementException:
            # Ignore FastNoSuchElementException
            pass

        self.assertEqual(list_out, [4, 2, 3, 4])

    def test_pipeline_1(self):
        caps_pipe = pipes.CapitalizePipe()

        pipeline_test = pipeline.Pipeline()
        pipeline_test.add_pipe(caps_pipe)

        pipeline_test.set_starts(recommend_utils.ListIterator(['this', 'is', 'the', 'test']))

        list_out = []
        try:
            while pipeline_test.has_next():
                current_object = pipeline_test.next()
                list_out.append(current_object)
        except recommend_utils.FastNoSuchElementException:
            # Ignore FastNoSuchElementException
            pass
        self.assertEqual(list_out, ['THIS', 'IS', 'THE', 'TEST'])

    def test_pipeline_chain_2(self):
        pipeline_test = pipeline.Pipeline(recommend_utils.ListIterator(['this', 'is', 'the', 'test']),
                                          [pipes.CapitalizePipe(),
                                           pipes.LenPipe()])
        list_out = []
        try:
            while pipeline_test.has_next():
                current_object = pipeline_test.next()
                list_out.append(current_object)
        except recommend_utils.FastNoSuchElementException:
            # Ignore FastNoSuchElementException
            pass
        self.assertEqual(list_out, [4, 2, 3, 4])

    def test_pipeline_chain_to_list(self):
        pipeline_test = pipeline.Pipeline(recommend_utils.ListIterator(['this', 'is', 'the', 'test']),
                                          [pipes.CapitalizePipe(),
                                           pipes.LenPipe()])

        self.assertEqual(pipeline_test.to_list(), [4, 2, 3, 4])

    def test_pipeline_graph_vertex_while(self):
        graph = Graph()
        graph.add_vertex('test_label', {'test_field': 1})
        graph.add_vertex('test_label', {'test_field': 2})

        pipeline_test = pipeline.Pipeline(graph.get_vertices_iterator(),
                                          [pipes.GraphVertexPipe()])

        try:
            list_out = []
            while pipeline_test.has_next():
                current_object = pipeline_test.next()
                list_out.append(current_object.id)
        except recommend_utils.FastNoSuchElementException:
            # Ignore FastNoSuchElementException
            pass
        self.assertEqual(list_out, [1, 2])

    def test_pipeline_graph_vertex_chain_to_list(self):
        graph = Graph()
        graph.add_vertex('test_label', {'test_field': 1})
        graph.add_vertex('test_label', {'test_field': 2})

        pipeline_test = pipeline.Pipeline(graph.get_vertices_iterator(),
                                          [pipes.GraphVertexPipe(),
                                           pipes.ElementIdPipe()])

        self.assertEqual(pipeline_test.to_list(), [1, 2])

    def test_pipeline_graph_vertex_chain_dict_to_list(self):
        graph = Graph()
        graph.add_vertex('test_label', {'test_field': 8})
        graph.add_vertex('test_label', {'test_field': 10})
        graph.add_vertex('test_label', {'test_field': 12, 'time': 'now'})

        pipeline_test = pipeline.Pipeline(graph.get_vertices_iterator(),
                                          [pipes.GraphVertexPipe(),
                                           pipes.ElementPropertiesPipe()])
        output = [
            {'test_field': 8},
            {'test_field': 10},
            {'test_field': 12, 'time': 'now'}
        ]
        self.assertEqual(pipeline_test.to_list(), output)
