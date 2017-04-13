"""
Static Util File
Contains Math Functions for recommendations
Exception
"""
from collections import Iterable
from enum import Enum


class FastNoSuchElementException(Exception):
    pass


class UnsupportedOperationException(Exception):
    pass


class Direction(Enum):
    """
    Direction is used to denote the direction of an edge or location of a vertex on an edge.
    """
    IN = 1
    OUT = 2
    BOTH = 3


def list_to_group_count(input_list):
    """
    List to item occurrences count dictionary
    """
    group_count = {}
    for input_item in input_list:
        if input_item in group_count:
            group_count[input_item] = group_count[input_item] + 1
        else:
            group_count[input_item] = 1

    return group_count


def flatten_iterable(input_list, out=None):
    # print('flatten_iterable: {}, {}'.format(input_list, out))
    # check a
    if out is None:
        # initialize with empty list
        out = []

    for current_item in input_list:
        if isinstance(current_item, Iterable) and not isinstance(current_item, str):
            flatten_iterable(current_item, out)
        else:
            out.append(current_item)
    return out


class GenericIterator(object):
    """
    Generic Iterator
    """

    def next(self):
        raise NotImplementedError()

    def has_next(self):
        raise NotImplementedError()

    def remove(self):
        raise NotImplementedError()


class DictKeyValueIterator(GenericIterator):

    def __init__(self, input_dict):
        self.count = -1
        self.input_dict = input_dict
        self.keys = list(input_dict.keys())
        self.max_count = len(self.keys)

    def next(self):
        """
        Return:
            Vertex or Edge Object
        """
        self.count = self.count + 1
        if self.count >= self.max_count:
            raise FastNoSuchElementException()
        value = self.input_dict[self.keys[self.count]]
        return value

    def has_next(self):
        """
        TODO: Don't think it works as expected
        """
        return self.count <= self.max_count

    def remove(self):
        raise UnsupportedOperationException()


class ListIterator(GenericIterator):

    def __init__(self, input_list):
        self.count = -1
        self.input_list = input_list
        self.max_count = len(self.input_list)

    def next(self):
        """
        Return:
            Vertex or Edge Object
        """
        self.count = self.count + 1
        if self.count >= self.max_count:
            raise FastNoSuchElementException()
        value = self.input_list[self.count]
        return value

    def has_next(self):
        """
        TODO: Don't think it works as expected
        """
        return self.count <= self.max_count

    def remove(self):
        raise UnsupportedOperationException()


class EmptyIterator(GenericIterator):

    def next(self):
        """
        Return:
            Vertex or Edge Object
        """
        raise FastNoSuchElementException()

    def has_next(self):
        return False

    def remove(self):
        raise UnsupportedOperationException()


def map_numbers(input_num, old_min, old_max, new_min, new_max):
    """
    Linear Conversion between ranges used for normalization

    http://stackoverflow.com/questions/929103/convert-a-number-range-to-another-range-maintaining-ratio
    """
    old_value = float(input_num)
    old_min = float(old_min)
    old_max = float(old_max)
    new_min = float(new_min)
    new_max = float(new_max)

    old_range = (old_max - old_min)

    new_value = None

    if new_min == new_max:
        new_value = new_min
    elif old_range == 0:
        new_value = new_min
    else:
        new_range = (new_max - new_min)
        new_value = (((old_value - old_min) * new_range) / old_range) + new_min

    return new_value


def get_top_n_score(recommendations_results, size_n=30):
    """
    Getting the top scores and limiting number of records

    If N = 2, Get the top 2 listings based on the score
    {
        profile_id#1: {
            listing_id#1: score#1,
            listing_id#2: score#2
        },
        profile_id#2: {
            listing_id#1: score#1,
            listing_id#2: score#2,
            listing_id#3: score#3,
        }
    }
    TO
    {
        profile_id#1: [
            [listing_id#1, score#1],
            [listing_id#2, score#2]
        ],
        profile_id#2: [
            [listing_id#3, score#1],
            [listing_id#4, score#2]
        ]
    }
    """
    output = {}
    for profile_id in recommendations_results:
        listing_scores = recommendations_results[profile_id]
        sorted_listing_scores = [[key, listing_scores[key]] for key in sorted(listing_scores, key=listing_scores.get, reverse=True)][:size_n]
        output[profile_id] = sorted_listing_scores
    return output
