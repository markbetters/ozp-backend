"""
Tests for (most) of the Utils mechanism
"""
from django.test import TestCase

from ozpcenter.recommend import recommend_utils
from ozpcenter.scripts import sample_data_generator as data_gen


class UtilsTest(TestCase):

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

    def test_get_top_n_score(self):
        input_data = {
            1: {
                4: 8,
                5: 2,
                2: 3
            },
            2: {
                1: 10,
                2: 20,
                3: 30
            }
        }
        expected_results = {
            1: [
                [4, 8],
                [2, 3]
            ],
            2: [
                [3, 30],
                [2, 20]
            ]
        }

        results = recommend_utils.get_top_n_score(input_data, 2)
        self.assertEqual(results, expected_results)

    def test_map_numbers(self):
        input_num = 500
        in_min = 1
        in_max = 500
        out_min = 10
        out_max = 20

        results = recommend_utils.map_numbers(input_num, in_min, in_max, out_min, out_max)
        self.assertEqual(results, 20)

    def test_map_numbers_1(self):
        input_num = 2
        in_min = 1
        in_max = 500
        out_min = 10
        out_max = 20

        results = recommend_utils.map_numbers(input_num, in_min, in_max, out_min, out_max)
        self.assertEqual(results, 10.02004008016032)

    def test_list_iterator(self):
        list_iterator = recommend_utils.ListIterator([1, 2, 3])

        list_out = []
        try:
            while list_iterator.has_next():
                list_out.append(list_iterator.next())
        except recommend_utils.FastNoSuchElementException:
            # Ignore FastNoSuchElementException
            pass

        self.assertEqual(list_out, [1, 2, 3])

    def test_dict_key_value_iterator(self):
        input_dict = {
            5: 8,
            2: 100,
            9: 5,
            -1: 9
        }
        list_iterator = recommend_utils.DictKeyValueIterator(input_dict)

        list_out = []
        try:
            while list_iterator.has_next():
                list_out.append(list_iterator.next())
        except recommend_utils.FastNoSuchElementException:
            # Ignore FastNoSuchElementException
            pass
        self.assertEqual(list_out, [5, 100, 8, 9])

    # def test_combine(self):
    #     data = {"Sample Data Gen":
    #             {"recommendations": [[1, 1.0], [2, 1.0], [3, 1.0], [4, 1.0],
    #                                  [5, 1.0], [6, 1.0], [7, 1.0], [8, 1.0],
    #                                  [9, 1.0], [10, 1.0]],
    #              "weight": 0.5,
    #              "ms_took": 2546.332763671875},
    #             "Baseline":
    #                 {"recommendations": [[11, 8.5], [112, 8.0], [85, 7.0], [86, 7.0],
    #                                      [87, 7.0], [88, 7.0], [89, 7.0], [90, 7.0],
    #                                      [62, 6.0], [81, 6.0], [21, 5.5], [1, 5.0], [111, 5.0],
    #                                     [113, 5.0], [114, 5.0], [64, 4.0], [66, 4.0],
    #                                     [68, 4.0], [70, 4.0], [72, 4.0]],
    #                 "weight": 1.0,
    #                 "ms_took": 1143.02734375}}
