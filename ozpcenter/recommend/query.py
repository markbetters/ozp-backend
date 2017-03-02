"""
Quering Graph
"""
from ozpcenter.recommend.utils import Direction
from ozpcenter.recommend.utils import DictKeyValueIterator
from ozpcenter.recommend.pipeline import Pipeline
from ozpcenter.recommend import pipes


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
        self.pipeline.add_pipe(pipes.GraphVertexPipe())

        if self.pipeline.starts is None:
            self.pipeline.set_starts(DictKeyValueIterator(self.graph.vertices))

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
        current_pipe = pipes.VerticesVerticesPipe(Direction.OUT)
        self.pipeline.add_pipe(current_pipe)
        return self

    def outE(self, edge_label=None, value=None):
        """
        VerticesToEdges

        """
        self.steps.append('outE({},{}'.format(edge_label, value))
        return self

    def id(self):
        """
        Get internal id of Elements
        """
        current_pipe = pipes.ElementIdPipe()
        self.pipeline.add_pipe(current_pipe)
        return self

    def limit(self, limit_number):
        """
        Limit number Elements
        """
        current_pipe = pipes.LimitPipe(limit_number)
        self.pipeline.add_pipe(current_pipe)
        return self

    def to_dict(self):
        """
        Convert objects (Elements into )
        """
        current_pipe = pipes.ElementPropertiesPipe()
        self.pipeline.add_pipe(current_pipe)
        return self

    def to_list(self):
        """
        Give results in a list of objects
        """
        return self.pipeline.to_list()

    def __str__(self):
        return str(self.pipeline)
