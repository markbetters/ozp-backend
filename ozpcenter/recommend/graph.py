"""
# Memory Graph Implementation for Recommendation engine

# Usage
graph = Graph()

graph.create_vertex('person', {name: 'Rachael'})
graph.create_vertex('person', {name: 'Stephanie'})
graph.create_vertex('person', {name: 'Michael'})
graph.create_vertex('person', {name: 'Donovan'})

graph.query().V('person').filter({name__ilike: 'ae'}).to_list()

# Based on
https://github.com/keithwhor/UnitGraph
https://en.wikipedia.org/wiki/Graph_theory
http://opensourceconnections.com/blog/2016/10/05/elastic-graph-recommendor/
http://www.objectivity.com/building-a-recommendation-engine-using-a-graph-database/
https://linkurio.us/using-neo4j-to-build-a-recommendation-engine-based-on-collaborative-filtering/
http://tinkerpop.apache.org/javadocs/3.2.2/core/org/apache/tinkerpop/gremlin/structure/Element.html
https://medium.com/@keithwhor/using-graph-theory-to-build-a-simple-recommendation-engine-in-javascript-ec43394b35a3#.iocsamn74
"""
from ozpcenter.recommend import utils
from ozpcenter.recommend.algorithms import GraphAlgoritms
from ozpcenter.recommend.query import Query


class Element(object):
    """
    An Element is the base class for both Vertex and Edge.
    An Element has an identifier that must be unique to its inheriting classes (Vertex or Edge)
    An Element can maintain a collection of Property objects.
    """

    def __init__(self, graph_instance, input_id, label=None, properties=None):
        self.graph = graph_instance
        self.label = label
        self.id = input_id  # Internal Id
        self.properties = properties or {}

    def _get_id(self):
        """
        An identifier that is unique. All Vertices and edges ids must be unique
        """
        return self.id

    def _set_id(self, input_id):
        self.id = input_id
        return self.id

    def _get_label(self):
        """
        The type of element for different classifications
        """
        return self.label

    def _set_label(self, input_label):
        """
        The type of element for different classifications
        Example: person, game, road
        """
        self.label = input_label
        return self.label

    def get_properties(self):
        """
        Get properties

        Args:
            Filter by properties
        """
        return self.properties

    def set_properties(self, properties):
        """
        Get properties

        Args:
            Filter by properties
        """
        for key in properties:
            current_value = properties[key]
            self.properties[key] = current_value
        return self.properties

    def get_property(self, key):
        """
        Return the object value associated with the provided string key.
        If no value exists for that key, return null.
        """
        return self.properties.get(key)

    def set_property(self, key, value):
        """
        Assign a key/value property to the element.
        If a value already exists for this key, then the previous key/value is overwritten
        """
        self.properties[key] = value
        return self.properties[key]

    # def _del_property(self, key):
    #     """
    #     Return the object value associated with the provided string key.
    #     If no value exists for that key, return null.
    #     """
    #     del self.properties[key]

    def remove_property(self, key):
        """
        Un-assigns a key/value property from the element.
        The key value of the removed property is returned.
        """
        value = self.properties.get(key)
        if key in self.properties:
            del self.properties[key]
        return value

    def remove(self):
        """
        Remove the element from the graph.
        """
        if isinstance(self, Vertex):
            self.graph.remove_vertex(self)
        else:
            self.graph.remove_edge(self)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        else:
            return False


class Vertex(Element):
    """
    An Element is the base class for both Vertex and Edge.
    An Element has an identifier that must be unique to its inheriting classes (Vertex or Edge)
    """

    def __init__(self, graph_instance, input_id, label=None, properties=None):
        super().__init__(graph_instance, input_id, label, properties)
        self.in_edges = {}
        self.out_edges = {}

    def __repr__(self):
        return 'Vertex({})'.format(self.label)

    def query(self):
        return Query(self.graph).v(self.id)

    def get_edges_iterator(self, direction, *labels):
        return utils.ListIterator(self.get_edges(direction, labels))

    def get_edges(self, direction, *labels):
        """

        """
        labels = utils.flatten_iterable(labels)

        if direction == utils.Direction.OUT:
            return self.get_out_edges(labels)
        elif direction == utils.Direction.IN:
            return self.get_in_edges(labels)
        else:
            out_list = []

            for current_edge in self.get_out_edges(labels):
                out_list.append(current_edge)

            for current_edge in self.get_in_edges(labels):
                out_list.append(current_edge)

            return out_list

    def get_in_edges(self, *labels):
        """
        Get in edges
        """
        labels = utils.flatten_iterable(labels)
        output_list = []
        labels_list = []

        if not labels:
            for label in self.in_edges:
                labels_list.append(label)
        else:
            for label in labels:
                labels_list.append(label)

        for label in labels_list:
            if self.in_edges.get(label):
                in_edge_dict = self.in_edges.get(label)
                for current_edge_key in in_edge_dict:
                    output_list.append(in_edge_dict[current_edge_key])
        return output_list

    def get_out_edges(self, *labels):
        """
        Get out edges
        """
        labels = utils.flatten_iterable(labels)
        output_list = []
        labels_list = []

        if not labels:
            for label in self.out_edges:
                labels_list.append(label)
        else:
            for label in labels:
                labels_list.append(label)

        for label in labels_list:
            if self.out_edges.get(label):
                out_edge_dict = self.out_edges.get(label)
                for current_edge_key in out_edge_dict:
                    output_list.append(out_edge_dict[current_edge_key])
        return output_list

    def add_edge(self, label, vertex_instance, properties=None):
        current_edge = self.graph.add_edge(current_id=None,
                                           in_vertex_id=self.id,
                                           out_vertex_id=vertex_instance.id,
                                           label=label,
                                           properties=properties)
        return current_edge

    def add_in_edge(self, label, edge_instance):
        """
        """
        if label in self.in_edges:
            self.in_edges[label][edge_instance.id] = edge_instance
        else:
            self.in_edges[label] = {}
            self.in_edges[label][edge_instance.id] = edge_instance
        return self.in_edges[label][edge_instance.id]

    def add_out_edge(self, label, edge_instance):
        """
        Add out edges
        """
        if label in self.out_edges:
            self.out_edges[label][edge_instance.id] = edge_instance
        else:
            self.out_edges[label] = {}
            self.out_edges[label][edge_instance.id] = edge_instance
        return self.out_edges[label][edge_instance.id]


class Edge(Element):
    """
    An Element is the base class for both Vertex and Edge.
    An Element has an identifier that must be unique to its inheriting classes (Vertex or Edge)
    """

    def __init__(self, graph_instance, input_id, label=None, out_vertex=None, in_vertex=None, properties=None):
        super().__init__(graph_instance, input_id, label, properties)
        self._in_vertex = in_vertex or None
        self._out_vertex = out_vertex or None

    def __repr__(self):
        return '{}--{}-->{}'.format(self._in_vertex, self.label, self._out_vertex)

    def link(self, in_vertex, out_vertex):
        self._in_vertex = in_vertex
        self._out_vertex = out_vertex

    @property
    def in_vertex(self):
        return self._in_vertex

    @property
    def out_vertex(self):
        return self._out_vertex

    def get_vertex(self, direction):
        """
        Get Vertex

        Arg:
            direction: Enum Direction
        """
        if direction == utils.Direction.IN:
            return self._in_vertex
        elif direction == utils.Direction.OUT:
            return self._out_vertex
        else:
            raise Exception('Invalid Direction')


class Graph(object):
    """
    A Graph is a container object for a collection of Vertex, Edge
    """

    def __init__(self):
        """
        Current_id:
            Current ID counter
        Vertices:
            Dictionary with Key: ID, value: Vertex obj
        Edges:
            Dictionary with Key: ID, value: Vertex obj
        """
        self.current_id = 0
        self.vertices = {}
        self.edges = {}

    def __str__(self):
        output = 'Graph(vertices: {}, edges: {})'.format(self.node_count(),
                                                         self.edge_count())
        return output

    def reset(self):
        """
        Reset Graph
        """
        self.current_id = 0
        self.vertices = {}
        self.edges = {}

    def node_count(self):
        return len(self.vertices)

    def edge_count(self):
        return len(self.edges)

    def get_next_id(self):
        """
        Get next id
        """
        while True:
            self.current_id = self.current_id + 1
            if self.current_id not in self.vertices:
                break
            if self.current_id not in self.edges:
                break
        return self.current_id

    def get_vertex(self, current_id):
        """
        Get Vertex from graph

        Return:
            Vertex
        """
        if current_id is None:
            raise Exception('Vertex ID can not be None')
        return self.vertices.get(current_id)

    def get_vertices(self, key=None, value=None):
        """
        Get Vertices

        key: the label to filter
        value: the value to filter
        """
        return [self.vertices[internal_id] for internal_id in self.vertices]

    def get_vertices_iterator(self, key=None, value=None):
        """
        Get Vertices iterator

        key: the label to filter
        value: the value to filter
        """
        return utils.DictKeyValueIterator(self.vertices)

    def add_vertex(self, label=None, properties=None, current_id=None):
        """
        Add Vertex to graph

        Return:
            Vertex
        """
        if current_id is None:
            done = False
            while not done:
                next_id = self.get_next_id()

                if next_id not in self.vertices:
                    current_id = next_id
                    done = True
        else:
            if current_id in self.vertices:
                raise Exception('Vertex with ID Already Exist')

        current_vertex = Vertex(self, current_id, label=label, properties=properties)
        self.vertices[current_vertex.id] = current_vertex
        return current_vertex

    def remove_vertex(self, current_id):
        if current_id is None:
            raise Exception('Vertex ID can not be None')
        if current_id not in self.vertices:
            raise Exception('Vertex ID does not exist')

        current_vertex = self.vertices[current_id]
        # Remove all edges from vertex
        for current_edge in current_vertex.get_edges():
            current_vertex.remove_edge(current_edge.id)
        # Delete Vertex from graph
        self.vertices.pop(current_id, None)

    def get_edge(self, current_id):
        """
        Return the edge referenced by the provided object current_id.
        If no edge is referenced by that current_id, then return null.
        """
        if current_id is None:
            raise Exception('Edge ID can not be None')
        return self.edges.get(current_id)

    def get_edges(self):
        """
        Get all edges
        """
        return [self.edges[internal_id] for internal_id in self.edges]

    def add_edge(self, current_id=None, in_vertex_id=None, out_vertex_id=None, label=None, properties=None):
        """
        Add edge to graph
        """
        if current_id is None:
            done = False
            while not done:
                next_id = self.get_next_id()

                if next_id not in self.edges:
                    current_id = next_id
                    done = True
        else:
            if current_id in self.edges:
                raise Exception('Edge with ID Already Exist')

        in_vertex = self.vertices.get(in_vertex_id)
        out_vertex = self.vertices.get(out_vertex_id)

        if out_vertex is None or in_vertex is None:
            raise Exception('In_vertex or out_vertex not found')

        current_edge = Edge(self, current_id,
                            label=label,
                            in_vertex=in_vertex,
                            out_vertex=out_vertex,
                            properties=properties)

        self.edges[current_id] = current_edge
        in_vertex.add_out_edge(label, current_edge)
        out_vertex.add_in_edge(label, current_edge)
        return current_edge

    def remove_edge(self, current_id):
        """
        Remove Edge from graph
        """
        if current_id is None:
            raise Exception('Edge ID can not be None')
        if current_id not in self.edges:
            raise Exception('Edge ID does not exist')

        # current_edge = self.edges[current_id]
        # out_vertex=current_edge.get_vertex(Direction.OUT)
        # in_vertex=current_edge.get_vertex(Direction.IN)
        # if out_vertex and out_vertex.out_edges:
        #     for edge in out_vertex.out_edge:
        self.edges.pop(current_id, None)

    def query(self):
        """
        Make a Query object to query graph
        """
        return Query(self)

    def algo(self):
        return GraphAlgoritms(self)
