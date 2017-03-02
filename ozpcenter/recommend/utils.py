"""
Static Util File
Contains Math Functions for recommendations
Exception
"""
from enum import Enum


class FastNoSuchElementException(Exception):
    pass


class UnsupportedOperation(Exception):
    pass


class Direction(Enum):
    """
    Direction is used to denote the direction of an edge or location of a vertex on an edge.
    """
    IN = 1
    OUT = 2
    BOTH = 3


class GenericIterator(object):
    """

    """
    pass


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
        raise RuntimeError('Unsupported Operation')


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
        raise RuntimeError('Unsupported Operation')


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