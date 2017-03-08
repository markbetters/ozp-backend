"""
Lazy Loading Dataflow
"""
from ozpcenter.recommend import utils


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


class Pipeline(object):
    """
    A Pipeline is a linear composite of Pipes.
    """

    def __init__(self, starts=None, pipes=[]):
        """
        Initialize Pipeline
        """
        self.start_pipe = None
        self.end_pipe = None

        self.pipes = pipes or []
        if self.pipes:
            self.set_pipes()

        self.starts = None
        if starts:
            self.set_starts(starts)

    def set_starts(self, starts):
        """
        Set Start

        Args:
            Iterator of objects
        """
        self.starts = starts

        if self.start_pipe:
            self.start_pipe.set_starts(starts)

    def get_starts(self):
        """
        Get start iterable
        """
        return self.starts

    def set_pipes(self):
        """
        constructing the pipeline chain
        """
        pipeline_size = len(self.pipes)
        self.start_pipe = self.pipes[0]
        self.end_pipe = self.pipes[-1]

        for i in list(range(1, pipeline_size)):
            self.pipes[i].set_starts(self.pipes[i - 1])

    def add_pipe(self, iterable):
        """
        Add Pipe
        """
        self.pipes.append(iterable)
        self.set_pipes()

    def remove(self):
        """
        Remove Pipe
        """
        raise utils.UnsupportedOperation()

    def has_next(self):
        """
        Determines if there is another object that can be emitted
        """
        return self.end_pipe.has_next()

    def next(self):
        """
        Get the next objected emitted

        Return:
            Object
        """
        return self.end_pipe.next()

    def iterate(self):
        """
        This will iterate all the objects out of the pipeline.
        """
        if self.starts is None:
            raise Exception('No Start Iterator set')

        try:
            while True:
                self.next()
        except utils.FastNoSuchElementException:
            # Ignore FastNoSuchElementException
            pass

    def to_list(self):
        """
        Drains the pipeline into a list
        """
        if self.starts is None:
            raise Exception('No Start Iterator set')

        output = []
        try:
            while True:
                output.append(self.next())
        except utils.FastNoSuchElementException:
            # Ignore FastNoSuchElementException
            pass
        return output

    def count(self):
        """
        Count the number of objects in an pipeline
        """
        if self.starts is None:
            raise Exception('No Start Iterator set')

        count = 0
        try:
            while True:
                self.next()
                count = count + 1
        except utils.FastNoSuchElementException:
            # Ignore FastNoSuchElementException
            pass
        return count

    def size(self):
        """
        Number of pipes in the pipeline
        """
        return len(self.pipes)

    def __str__(self):
        """
        Pipeline String
        """
        return '[{}]'.format(', '.join([str(pipe) for pipe in self.pipes]))
