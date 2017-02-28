"""
Make sure that Pipe and Pipeline classes work
"""
from django.test import TestCase

from ozpcenter.scripts import sample_data_generator as data_gen
from ozpcenter.recommend import utils
from ozpcenter.recommend import pipes
from ozpcenter.recommend import pipeline


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
        caps_pipe.set_starts(utils.ListIterator(['this', 'is', 'the', 'test']))

        list_out = []

        while caps_pipe.has_next():
            current_object = caps_pipe.next()
            list_out.append(current_object)

        self.assertEqual(list_out, ['THIS', 'IS', 'THE', 'TEST'])

    def test_pipe_cap_len_chain(self):
        caps_pipe = pipes.CapitalizePipe()
        len_pipe = pipes.LenPipe()

        caps_pipe.set_starts(utils.ListIterator(['this', 'is', 'the', 'test']))
        len_pipe.set_starts(caps_pipe)

        list_out = []

        while len_pipe.has_next():
            current_object = len_pipe.next()
            list_out.append(current_object)

        self.assertEqual(list_out, [4, 2, 3, 4])

    def test_pipeline_1(self):
        caps_pipe = pipes.CapitalizePipe()

        pipeline_test = pipeline.Pipeline()
        pipeline_test.add_pipe(caps_pipe)

        pipeline_test.set_starts(utils.ListIterator(['this', 'is', 'the', 'test']))

        list_out = []
        while pipeline_test.has_next():
            current_object = pipeline_test.next()
            list_out.append(current_object)

        self.assertEqual(list_out, ['THIS', 'IS', 'THE', 'TEST'])

    def test_pipeline_chain_2(self):
        pipeline_test = pipeline.Pipeline(utils.ListIterator(['this', 'is', 'the', 'test']),
                                          [pipes.CapitalizePipe(),
                                           pipes.LenPipe()])
        list_out = []
        while pipeline_test.has_next():
            current_object = pipeline_test.next()
            list_out.append(current_object)

        self.assertEqual(list_out, [4, 2, 3, 4])

    def test_pipeline_chain_to_list(self):
        pipeline_test = pipeline.Pipeline(utils.ListIterator(['this', 'is', 'the', 'test']),
                                          [pipes.CapitalizePipe(),
                                           pipes.LenPipe()])

        self.assertEqual(pipeline_test.to_list(), [4, 2, 3, 4])
