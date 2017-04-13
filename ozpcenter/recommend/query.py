"""
Quering Graph
"""
from ozpcenter.pipe import pipes
from ozpcenter.pipe.pipeline import Pipeline
from ozpcenter.recommend import recommend_utils
from ozpcenter.recommend.recommend_utils import Direction


class Query(object):
    """
    Query Object Compiler/ Pipeline
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
            self.pipeline.set_starts(recommend_utils.DictKeyValueIterator(self.graph.vertices))

        return self

    def v(self, vertex_id, *vertex_ids):
        """
        Get Vertex by internal id
        """
        self.pipeline.add_pipe(pipes.GraphVertexPipe())

        if self.pipeline.starts is None:
            out_list = []

            if self.graph.vertices.get(vertex_id):
                out_list.append(self.graph.vertices.get(vertex_id))

            for current_vertex_id in vertex_ids:
                if self.graph.vertices.get(current_vertex_id):
                    out_list.append(self.graph.vertices.get(current_vertex_id))

            self.pipeline.set_starts(recommend_utils.ListIterator(out_list))

        return self

    def edge(self, edge_id):
        """
        get edge
        """
        pass

    def has(self, key, value):
        pass

    def out(self, *labels):
        """
        VerticesToVertices
        """
        current_pipe = pipes.VerticesVerticesPipe(Direction.OUT, labels)
        self.pipeline.add_pipe(current_pipe)
        return self

    def in_(self, *labels):
        """
        VerticesToVertices
        """
        current_pipe = pipes.VerticesVerticesPipe(Direction.IN, labels)
        self.pipeline.add_pipe(current_pipe)
        return self

    def outE(self, edge_label=None, value=None):
        """
        VerticesToEdges
        """
        return self

    def distinct(self):
        """
        distinct
        """
        current_pipe = pipes.DistinctPipe()
        self.pipeline.add_pipe(current_pipe)
        return self

    def id(self):
        """
        Get internal id of Elements
        """
        current_pipe = pipes.ElementIdPipe()
        self.pipeline.add_pipe(current_pipe)
        return self

    def exclude_ids(self, id_list):
        """
        Get internal id of Elements
        """
        current_pipe = pipes.ExcludeIdsPipe(id_list)
        self.pipeline.add_pipe(current_pipe)
        return self

    def limit(self, limit_number):
        """
        Limit number Elements
        """
        current_pipe = pipes.LimitPipe(limit_number)
        self.pipeline.add_pipe(current_pipe)
        return self

    def side_effect(self, function):
        """
        Limit number Elements
        """
        current_pipe = pipes.SideEffectPipe(function)
        self.pipeline.add_pipe(current_pipe)
        return self

    def to_dict(self, internal=False):
        """
        Convert Element into Dictionary
        """
        current_pipe = pipes.ElementPropertiesPipe(internal=internal)
        self.pipeline.add_pipe(current_pipe)
        return self

    def has_next(self):
        """
        Give results in a list of objects
        """
        return self.pipeline.has_next()

    def next(self):
        """
        Give results in a list of objects
        """
        return self.pipeline.next()

    def to_list(self):
        """
        Give results in a list of objects
        """
        return self.pipeline.to_list()

    def __str__(self):
        return str(self.pipeline)
