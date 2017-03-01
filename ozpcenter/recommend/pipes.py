from ozpcenter.recommend.pipeline import Pipe


class VerticesVerticesPipe(Pipe):

    def __init__(self, direction):
        super().__init__()
        # Super
        self.direction = direction

    def process_next_start(self):
        """
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


class LenPipe(Pipe):

    def __init__(self):
        super().__init__()

    def process_next_start(self):
        """
        Find length each object
        """
        start = len(self.starts.next())
        return start


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

    def __init__(self):
        super().__init__()

    def process_next_start(self):
        """
        CapitalizePipe each string object
        """
        current_vertex = self.starts.next()
        return current_vertex.get_properties()


class ElementHasPipe(Pipe):
    """
    Filter Pipe
    """
    def __init__(self, label, value=None):
        super().__init__()

    def process_next_start(self):
        """
        Element Has each string object
        """
        current_vertex = self.starts.next()
        return current_vertex
