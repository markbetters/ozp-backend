import logging

from ozpcenter.recommend import recommend_utils
from ozpcenter.recommend.recommend_utils import Direction
from ozpcenter.recommend.recommend_utils import FastNoSuchElementException
from plugins_util.plugin_manager import system_has_access_control

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


class Pipe(object):
    """
    <S, E>
    """

    def __init__(self):
        """
        Initialize Pipe

        Args:
            starts: Start of the Pipe
        """
        self.starts = None
        self.available = False
        self.current_end = None
        self.next_end = None

    def set_starts(self, starts):
        """
        Args:
            starts: iterable of s objects to the head (start) of pipe
        """
        self.starts = starts

    def next(self):
        """
        Return one E Object
        """
        if self.available:
            self.available = False
            self.current_end = self.next_end
            return self.current_end
        else:
            self.current_end = self.process_next_start()
            return self.current_end

    def has_next(self):
        """
        Return Boolean
        """
        if self.available:
            return True
        else:
            try:
                self.next_end = self.process_next_start()
                self.available = True
                return self.available
            except IndexError as err:  # TODO: Fix to RuntimeError
                self.available = False
                return self.available
            except Exception as err:  # NoSuchElementException
                raise err

    def process_next_start(self):
        """
        Returns E

        Raise:
            NoSuchElementException
        """
        raise NotImplementedError("Need to implement in subclasses")

    def reset(self):
        if isinstance(self.starts, self.__class__):
            self.starts.reset()

        self.next_end = None
        self.current_end = None
        self.available = False

    def __str__(self):
        default_keys = ['starts', 'available', 'current_end', 'next_end']
        instance_vars = {}
        variables = vars(self)
        for variable_key in variables:
            if variable_key not in default_keys:
                instance_vars[variable_key] = variables[variable_key]

        variables_string = ', '.join(['{}:{}'.format(key, instance_vars[key]) for key in instance_vars])
        output = '{}({})'.format(self.__class__.__name__, variables_string)
        return output


class MetaPipe(Pipe):

    def get_pipes(self):
        raise NotImplementedError("Need to implement in subclasses")

    def reset(self):
        for pipe in self.get_pipes():
            pipe.reset()
        super().reset()


class AsPipe(MetaPipe):

    def __init__(self, name, pipe):
        super().__init__()
        self.name = name
        self.pipe = pipe

    def set_starts(self, starts):
        """
        Args:
            starts: iterable of s objects to the head (start) of pipe
        """
        self.pipe.set_starts(starts)
        self.starts = starts

    def get_current_end(self):
        return self.current_end

    def get_name(self):
        return self.name

    def process_next_start(self):
        return self.pipe.next()

    def get_pipes(self):
        return [self.pipe]


class VerticesVerticesPipe(Pipe):

    def __init__(self, direction, *labels):
        super().__init__()
        # Super
        self.direction = direction
        self.labels = labels
        self.next_end = recommend_utils.EmptyIterator()

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
        self.next_end = recommend_utils.EmptyIterator()

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
        SideEffectPipe
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


class ListingDictPostSecurityMarkingCheckPipe(Pipe):

    def __init__(self, username, featured=False):
        super().__init__()
        self.username = username
        self.featured = featured

    def process_next_start(self):
        """
        execute security_marking check on each listing
        """
        while True:
            listing = self.starts.next()

            if not listing['security_marking']:
                logger.debug('Listing {0!s} has no security_marking'.format(listing['title']))
            else:
                if self.featured:
                    if listing['is_featured'] is True:
                        if system_has_access_control(self.username, listing['security_marking']):
                            return listing
                else:
                    if system_has_access_control(self.username, listing['security_marking']):
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
