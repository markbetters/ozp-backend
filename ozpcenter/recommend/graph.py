"""
# Memory Graph Implementation for Recommendation engine
Collaborative filtering based on graph database

TODO: Figure out of MEASURING MEANINGFUL PROFILE-LISTING CONNECTIONS
https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-significantterms-aggregation.html
aggregation that returns interesting or unusual occurrences of terms in a set
"measures the kind of statistically significant relationships we need to deliver meaningful recommendations"

Might be able to figure out how to implement JLHScore/ChiSquare Scoring to python
https://github.com/elastic/elasticsearch/blob/master/core/src/main/java/org/elasticsearch/search/aggregations/bucket/significant/heuristics/JLHScore.java

JLHScore:
Calculates the significance of a term in a sample against a background of
normal distributions by comparing the changes in frequency.

ChiSquare:
"Information Retrieval", Manning et al., Eq. 13.19

Google Normalized Distance:
Calculates Google Normalized Distance, as described in "The Google Similarity Distance", Cilibrasi and Vitanyi, 2007
link: http://arxiv.org/pdf/cs/0412098v3.pdf

## Structure
Vertex Types:
Agency
    short_name

Profile
    profile_id
    role: APPS_MALL_STEWARD > ORG_STEWARD > USER

Listing
    listing_id
    is_featured
    is_private
    total_reviews
    avg_rate

Category
    title

Include BookmarkedFolders ?
Include Review ?

Connections:
Agency <--profileAgency-- Profile --bookmarked--> Listing --listingCategory--> Category
                                                          --listingAgency--> Agency

## Algorithms
### Algorithm 1:  Getting Similar Listings via looking at other Profiles bookmarks

graph.v('profile', '1')  # Select 'profile 1' as start
    .out('bookmarked') # Go to all Listings that 'profile 1' has bookmarked
    .in('bookmarked')  # Go to all Profiles that bookmarked the same listings as 'profile 1'
    .filter(profile!=1)  # Filter out 'profile 1' from profile_username
    .out('bookmarked') # Go to all Listings that other people has bookmarked (recommendations)
    # Filter out all listings that 'profile 1' has bookmarked
    # Group by Listings with Count (recommendation weight) and sort by count DSC

Additions to improve relevance (usefull-ness to profile):
For the results, sort by Category, then Agency

### Algorithm 2:  Getting Most bookmarked listings across all profiles

graph.v('profile')  # Getting all Profiles
    .out('bookmarked') # Go to all Listings that all profiles has bookmarked
    # Group by Listings with Count (recommendation weight) and sort by count DSC

### Example Graph
                                                 +------------------+
                                                 |                  v
                                                 |
                                                 |              +----------+
                                                 |              |Listing 4 |
                                          +---------+           +----------+
                                         ++Profile 2+-------+
                                         +----------+       |
                      +----------+       |                  |
                      |Listing 1 |  <-^--+           +------->  +----------+
           +------->  +----------+    |              |          |Listing 5 |
           |                          |   +----------+          +----------+
           |                          +---+Profile 3+---+
           |                             +----------+   |
   +---------+        +----------+ <-----+              |
   |Profile 1+------> |Listing 2 |     |                |       +----------+
   +---------+        +----------+     |                +-----> |Listing 6 |
           |                           +------------+   |       +----------+
           |                           |  |Profile 4+-------+
           |                           |  +---------+   |   |
           |          +----------+     |                |   |
           +------->  |Listing 3 |     |                |   |   +----------+
                      +----------+     |                |   +-> |Listing 7 |
                             ^         |  +---------+   |       +----------+
                             |         +--+Profile 5|   |
                             +----------------------+   |
                                                        |
                                                        |       +----------+
                                                        +---->  |Listing 8 |
                                                                +----------+
Listing Categories:
Listing 1 - Category 1
Listing 2 - Category 1
Listing 3 - Category 2
Listing 4 - Category 2
Listing 5 - Category 2
Listing 6 - Category 3
Listing 7 - Category 3
Listing 8 - Category 1


### Usage
# TODO Convert into python
graph = Graph()

graph.create_vertex('person', {name: 'Rachael'})
graph.create_vertex('person', {name: 'Stephanie'})
graph.create_vertex('person', {name: 'Michael'})
graph.create_vertex('person', {name: 'Donovan'})

graph.query().V('person').filter({name__ilike: 'ae'}).to_list()


## Issues
### Non-useful listings
Solution - Also Use listing categories to make recommendation for relevant to user

### New User Problem
We might have the New User Problem,
The way to solve this to get the results of a different recommendation engine (CustomHybridRecommender - GlobalBaseline)
recommendations = CustomHybridRecommender + GraphCollaborativeRecommender


## Based on
https://en.wikipedia.org/wiki/Graph_theory
https://github.com/keithwhor/UnitGraph
https://medium.com/@keithwhor/using-graph-theory-to-build-a-simple-recommendation-engine-in-javascript-ec43394b35a3#.iocsamn74
http://tinkerpop.apache.org/javadocs/3.2.2/core/org/apache/tinkerpop/gremlin/structure/Element.html
http://www.objectivity.com/building-a-recommendation-engine-using-a-graph-database/
https://linkurio.us/using-neo4j-to-build-a-recommendation-engine-based-on-collaborative-filtering/
http://opensourceconnections.com/blog/2016/10/05/elastic-graph-recommendor/

## Lazy Loading Pipe Query System:
### VerticesVerticesPipe
Start with Vertices (1 or more) to get all the other Vertices connected to it.
"""
from ozpcenter.recommend.utils import Direction
from ozpcenter.recommend.utils import DictKeyValueIterator
from ozpcenter.recommend.pipeline import Pipeline


class Query(object):
    """
    Query Object Compiler/ Pipeline

    graph.query().V('profile_id', 4).out()
    """
    def __init__(self, graph):
        self.graph = graph
        self.pipeline = Pipeline()

    def V(self, vertex_label=None, value=None):
        """
        Vertices
        """

        self.steps.append('V({},{}'.format(vertex_label, value))
        return self

    def v(self, vertex_id=None):
        """
        Get Vertex by internal id
        """
        self.steps.append('v({}'.format(vertex_id))
        return self

    def edge(self, edge_id):
        """
        get edge
        """
        pass

    def has(self, key, value):
        pass

    def out(self, edge_label=None, value=None):
        """
        VerticesToVertices

        """
        # current_pipe = VerticesVerticesPipe(Direction.OUT)

        self.steps.append('out({},{}'.format(edge_label, value))
        return self

    def outE(self, edge_label=None, value=None):
        """
        VerticesToEdges

        """
        self.steps.append('outE({},{}'.format(edge_label, value))
        return self

    def to_list():
        """
        Give results in a list of objects
        """
        pass

    def __str__(self):
        return self.steps


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

    def id(self, input_id=None):
        """
        An identifier that is unique. All Vertices and edges ids must be unique
        """
        if input_id:
            self.id = input_id
        return self.id

    def label(self, input_label):
        """
        The type of element for different classifications
        Example: person, game, road

        """
        if input_label:
            self.label = input_label
        return self.label

    def load(self, properties):
        """
        properties: Dictionary
        """
        for key in properties:
            current_value = properties[key]
            self.properties[key] = current_value

    def set_property(self, key, value):
        """
        Assign a key/value property to the element.
        If a value already exists for this key, then the previous key/value is overwritten
        """
        self.properties[key] = value

    def remove_property(self, key):
        """
        Un-assigns a key/value property from the element.
        The key value of the removed property is returned.
        """
        value = self.properties.get(key)
        if key in self.properties:
            del self.properties[key]
        return value

    def get(self, key):
        """
        Return the object value associated with the provided string key.
        If no value exists for that key, return null.
        """
        return self.properties.get(key)

    def remove(self):
        """
        Remove the element from the graph.
        """
        if isinstance(self, Vertex):
            self.graph.remove_vertex(self)
        else:
            self.graph.remove_edge(self)


class Vertex(Element):
    """
    An Element is the base class for both Vertex and Edge.
    An Element has an identifier that must be unique to its inheriting classes (Vertex or Edge)
    """
    def __init__(self, graph, id, label=None, properties=None):
        self.in_edges = []
        self.out_edges = []

    def get_edges(self, direction, labels):
        pass

    def add_edge(self, label, edge_instance):
        # return self.graph.addEdge(null, this, vertex, label)
        pass


class Edge(Element):
    """
    An Element is the base class for both Vertex and Edge.
    An Element has an identifier that must be unique to its inheriting classes (Vertex or Edge)
    """
    def __init__(self, label=None, id=None, properties=None):
        self.in_vertex = None
        self.out_vertex = None

    def link(self, in_vertex, out_vertex):
        pass

    def get_vertex(self, direction):
        """
        Get Vertex

        Arg:
            direction: Enum Direction

        """
        if direction == Direction.IN:
            pass
        elif direction == Direction.OUT:
            pass
        else:
            pass


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

    def reset(self):
        """
        Reset Graph
        """
        self.current_id = 0
        self.vertices = {}
        self.edges = {}

    def node_count(self):
        pass

    def edge_count(self):
        pass

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

    def get_vertices(self, key=None, value=None):
        """
        Get Vertices

        key: the label to filter
        value: the value to filter
        """
        pass

    def get_vertices_iterator(self, key=None, value=None):
        """
        Get Vertices iterator

        key: the label to filter
        value: the value to filter
        """
        return DictKeyValueIterator(self.vertices)

    def add_vertex(self, current_id=None, properties=None):
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

        current_vertex = Vertex(self, current_id, properties=properties)
        self.vertices[current_vertex.id] = current_vertex
        return current_vertex

    def get_vertex(self, current_id):
        """
        Get Vertex from graph

        Return:
            Vertex
        """
        if current_id is None:
            raise Exception('Vertex ID can not be None')
        return self.vertices.get(current_id)

    def remove_vertex(self, current_id):
        if current_id is None:
            raise Exception('Vertex ID can not be None')

    def get_edge(self, current_id):
        """
        Return the edge referenced by the provided object current_id.
        If no edge is referenced by that current_id, then return null.
        """
        if current_id is None:
            raise Exception('Edge ID can not be None')
        return self.edges.get(current_id)

    def remove_edge(self, current_id):
        pass


class GraphFactory(object):
    """
    Create different graph
    """
    @staticmethod
    def create_graph_template():
        graph = Graph()
        graph.add_vertex()
