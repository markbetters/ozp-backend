"""
Memory Graph Implementation for Recommendation engine

Algorthim 1:
    Collaborative filtering based on graph database

Usage:
graph = Graph();

graph.createNode('person', {name: 'Rachael'});
graph.createNode('person', {name: 'Stephanie'});
graph.createNode('person', {name: 'Michael'});
graph.createNode('person', {name: 'Donovan'});

graph.nodes('person').query().filter({name__ilike: 'ae'}).units();

Based on:
https://en.wikipedia.org/wiki/Graph_theory
https://github.com/keithwhor/UnitGraph
https://medium.com/@keithwhor/using-graph-theory-to-build-a-simple-recommendation-engine-in-javascript-ec43394b35a3#.iocsamn74
http://tinkerpop.apache.org/javadocs/3.2.2/core/org/apache/tinkerpop/gremlin/structure/Element.html
http://www.objectivity.com/building-a-recommendation-engine-using-a-graph-database/
https://linkurio.us/using-neo4j-to-build-a-recommendation-engine-based-on-collaborative-filtering/

"""


class Element(object):
    """
    An Element is the base class for both Vertex and Edge.
    An Element has an identifier that must be unique to its inheriting classes (Vertex or Edge)
    An Element can maintain a collection of Property objects.
    """
    def __init__(self):
        self.label = None
        self.properties = {}

    def label(self):
        """
        The type of element for different classifications
        Example: person, game, road

        """
        pass

    def load(self, properties_dictionary):
        pass

    def set(self, property_name, value):
        pass

    def unset(self, property_name):
        pass

    def get(self, property_name):
        pass


class Vertex(Element):
    """
    An Element is the base class for both Vertex and Edge.
    An Element has an identifier that must be unique to its inheriting classes (Vertex or Edge)
    """
    def __init__(self, label, properties_dictionary=None):
        self.in_edges = []
        self.out_edges = []


class Edge(Element):
    """
    An Element is the base class for both Vertex and Edge.
    An Element has an identifier that must be unique to its inheriting classes (Vertex or Edge)
    """
    def __init__(self, label, properties_dictionary=None):
        pass

    def link(self, input_vertex, out_vertex):
        pass


class Graph(object):
    """
    A Graph is a container object for a collection of Vertex, Edge
    """
    def __init__(self):
        self.vertices = []
        self.edges = []

    def node_count(self):
        pass

    def edge_count(self):
        pass
