import logging

from ozpcenter.pipe.pipeline import Pipe
from ozpcenter.recommend import utils
from ozpcenter.recommend.utils import Direction
from ozpcenter.recommend.utils import FastNoSuchElementException
from plugins_util.plugin_manager import system_has_access_control

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class VerticesVerticesPipe(Pipe):

    def __init__(self, direction, *labels):
        super().__init__()
        # Super
        self.direction = direction
        self.labels = labels
        self.next_end = utils.EmptyIterator()

    def process_next_start(self):
        """
        Start at Vertex, return Vertex
        """
        while True:
            if self.next_end.has_next():
                try:
                    current_edge = self.next_end.next()

                    if self.direction == Direction.OUT:
                        return current_edge.out_vertex  # Edge
                    elif self.direction == Direction.IN:
                        return current_edge.in_vertex
                    else:
                        raise Exception('Need to implement')
                except FastNoSuchElementException:
                    pass
            else:
                current_vertex = self.starts.next()
                edges_iterator = current_vertex.get_edges_iterator(self.direction, self.labels)
                self.next_end = edges_iterator


class VerticesEdgesPipe(Pipe):

    def __init__(self, direction, *labels):
        super().__init__()
        # Super
        self.direction = direction
        self.labels = labels
        self.next_end = utils.EmptyIterator()

    def process_next_start(self):
        """
        Start at Vertex, return Vertex
        """
        while True:
            if self.next_end.has_next():
                try:
                    current_edge = self.next_end.next()

                    if self.direction == Direction.OUT:
                        return current_edge  # Edge
                    elif self.direction == Direction.IN:
                        return current_edge
                    else:
                        raise Exception('Need to implement')
                except FastNoSuchElementException:
                    pass
            else:
                current_vertex = self.starts.next()
                edges_iterator = current_vertex.get_edges_iterator(self.direction, self.labels)
                self.next_end = edges_iterator


class EdgesVerticesPipe(Pipe):

    def __init__(self, direction):
        super().__init__()
        # Super
        self.direction = direction

    def process_next_start(self):
        """
        Start at Edge, return Vertex
        """
        pass


class CapitalizePipe(Pipe):

    def __init__(self):
        super().__init__()

    def process_next_start(self):
        """
        CapitalizePipe each string object
        """
        start = self.starts.next().upper()
        return start


class SideEffectPipe(Pipe):

    def __init__(self, function):
        super().__init__()
        self.function = function

    def process_next_start(self):
        """
        CapitalizePipe each string object
        """
        start = self.starts.next()
        self.function(start)
        return start


class LenPipe(Pipe):

    def __init__(self):
        super().__init__()

    def process_next_start(self):
        """
        Find length each object
        """
        start = len(self.starts.next())
        return start


class ListingPostSecurityMarkingCheckPipe(Pipe):

    def __init__(self, username):
        super().__init__()
        self.username = username

    def process_next_start(self):
        """
        execute security_marking check on each listing
        """
        while True:
            listing = self.starts.next()
            if not listing.security_marking:
                logger.debug('Listing {0!s} has no security_marking'.format(listing.title))
            if system_has_access_control(self.username, listing.security_marking):
                return listing


class LimitPipe(Pipe):

    def __init__(self, limit_number):
        super().__init__()
        self.count = 1
        self.limit_number = limit_number

    def process_next_start(self):
        """
        Limit number of items
        """
        while True:
            if self.count > self.limit_number:
                raise FastNoSuchElementException()
            else:
                current_item = self.starts.next()
                self.count = self.count + 1
                return current_item


class DistinctPipe(Pipe):

    def __init__(self):
        super().__init__()
        self.items = set()

    def process_next_start(self):
        """
        Limit number of items
        """
        while True:
            current_item = self.starts.next()

            if current_item not in self.items:
                self.items.add(current_item)
                return current_item


class ExcludePipe(Pipe):

    def __init__(self, object_list):
        super().__init__()
        self.items = set()

        for current_object in object_list:
            self.items.add(current_object)

    def process_next_start(self):
        """
        Limit number of items
        """
        while True:
            current_item = self.starts.next()

            if current_item not in self.items:
                return current_item


class ExcludeIdsPipe(Pipe):

    def __init__(self, object_list):
        super().__init__()
        self.items = set()

        for current_object in object_list:
            self.items.add(current_object)

    def process_next_start(self):
        """
        Limit number of items
        """
        while True:
            current_element = self.starts.next()
            current_element_id = current_element.id

            if current_element_id not in self.items:
                return current_element


class GraphVertexPipe(Pipe):
    """
    Start of Graph to vertex flow
    """

    def __init__(self):
        super().__init__()

    def process_next_start(self):
        """
        CapitalizePipe each string object
        """
        current_vertex = self.starts.next()
        return current_vertex


class ElementIdPipe(Pipe):
    """
    Start of Graph to vertex flow
    """

    def __init__(self):
        super().__init__()

    def process_next_start(self):
        """
        CapitalizePipe each string object
        """
        current_vertex = self.starts.next()
        return current_vertex.id


class ElementPropertiesPipe(Pipe):
    """
    Start of Graph to vertex flow
    """

    def __init__(self, internal=False):
        super().__init__()
        self.internal = internal

    def process_next_start(self):
        """
        CapitalizePipe each string object
        """
        current_vertex = self.starts.next()
        vertex_properties = current_vertex.properties

        if self.internal:
            vertex_properties['_id'] = current_vertex.id
            vertex_properties['_label'] = current_vertex.label

        return vertex_properties


class ElementHasPipe(Pipe):
    """
    Filter Pipe
    """

    def __init__(self, label, key=None, predicate='EQUALS', value=None):
        super().__init__()

    def process_next_start(self):
        """
        Element Has each string object
        """
        current_vertex = self.starts.next()
        return current_vertex
