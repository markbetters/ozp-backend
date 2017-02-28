from ozpcenter.recommend.pipeline import Pipe


class VerticesVerticesPipe(Pipe):

    def __init__(self, direction):
        # Super
        self.direction = direction


class CapitalizePipe(Pipe):

    def process_next_start(self):
        """
        CapitalizePipe each string object
        """
        start = self.starts.next().upper()
        return start


class LenPipe(Pipe):

    def process_next_start(self):
        """
        Find length each object
        """
        start = len(self.starts.next())
        return start
