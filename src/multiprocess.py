import logging
import sys

from . import modules


# START HACKERY #####
# The builtin multiprocessing library is a bit weird, in that it offers multiple modes that it can be used in - the
# correct way to use the library is to import it, and then use it with the correct mode specified, e.g:
#
# >>> import multiprocessing as mp
# >>> mp = mp.get_context('forkserver')
#
# In particular, we shouldn't go around just blindly importing and using the multiprocessing library without specifying
# it like this, as else it will set the default mode globally, and anyone else trying to use the multiprocessing library
# might be in for an unexpected surprise; our library code shouldn't restrict how they wise to use the module.
#
# So we need to avoid importing multiprocessing ourselves unless we really have to! So we provide a __call__ function
# on the module to allow people to tell it what kind of multiprocessing they're using, so that we can define our objects
# in the appropriate space.

mp_ = None  # Will later be set to the multiprocessing library


def _call(cls, old_cls):
    def __call__(self, mp=None):
        """Call the module to tell it what to use as the multiprocessing library; it will default to importing the normal
        multiprocessing library. This is necessary so that multiprocessing can be replaced with the result of
        multiprocessing.get_context, if necessary.
        """

        global mp_
        if mp_ is not None:
            raise RuntimeError("Module already has a multiprocessing library; cannot specify it again.")

        # Import or set multiprocessing
        if mp is None:
            import multiprocessing as mp_
        else:
            mp_ = mp
        _mp_already_imported = True
        # Define all the things in this module
        _define()
        # Get rid of the special stuff we don't need any more.
        self.__class__ = old_cls
    return __call__


# Keep this updated when adding this inside _define! No real better way of handling this, as Python simply cannot be
# allowed to know what's inside _define until multiprocessing is specified.
def _dir(cls, old_cls):
    def __dir__(self):
        existing = super(cls, self).__dir__()
        new = ['RedirectedOutputProcess', 'StreamToLogger', 'LogOutputProcess', 'StreamToQueue', 'QueueOutputProcess']
        return existing + new
    return __dir__


# If someone tries to get an attribute on this module then our hand is forced; go ahead and import multiprocessing.
def _getattr(cls, old_cls):
    def __getattr__(self, name):
        if name in dir(self):
            self()
            return globals()[name]
        else:
            raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    return __getattr__


modules.endow_attrs(__name__, {'__call__': _call, '__dir__': _dir, '__getattr__': _getattr})


# END HACKERY #####


def _define():
    class RedirectedOutputProcess(mp_.Process):
        """Redirects the stdout and stderr streams of a Process to the specified :stdout: and :stderr:."""

        def __init__(self, *args, stdout=None, stderr=None, **kwargs):
            """Arguments:
                stdout: Where to redirect stdout. Defaults to no redirection.
                stderr: Where redirect stderr. Defaults to no redirection.

            Otherwise the same as multiprocessing.Process.
            """
            self.stdout = stdout
            self.stderr = stderr
            super(RedirectedOutputProcess, self).__init__(*args, **kwargs)

        def run(self):
            if self.stdout is not None:
                sys.stdout = self.stdout
            if self.stderr is not None:
                sys.stderr = self.stderr
            super(RedirectedOutputProcess, self).run()

    # Courtesy of # https://github.com/jdloft/multiprocess-logging/blob/master/main.py
    class StreamToLogger:
        """Converts streams (stdout or stderr for example) to logs."""

        def __init__(self, logger, log_level=logging.INFO, **kwargs):
            """Arguments:
                logger: A logger to log the stream to.
                log_level: The level to log at.
            """

            self.logger = logger
            self.log_level = log_level
            self.linebuf = ''
            super(StreamToLogger).__init__(**kwargs)

        def write(self, buf):
            for line in buf.rstrip().splitlines():
                self.logger.log(self.log_level, line.rstrip())

        def flush(self):
            pass

    class LogOutputProcess(RedirectedOutputProcess):
        """Logs the stdout and stderr of a process to a log."""

        def __init__(self, *args, logger=None,
                     stdout_logger=None, stderr_logger=None,
                     stdout_log_level=logging.INFO, stderr_log_level=logging.ERROR,
                     stdout=None, stderr=None, **kwargs):
            """Arguments:
                logger: The logger to redirect both stdout and stderr to.
                stdout_logger: The logger to redirect just stdout; defaults to the value of the logger argument.
                stderr_logger: The logger to redirect just stderr; defaults to the value of the logger argument.
                stdout_log_level: The level to log stdout at. Defaults to INFO.
                stderr_log_level: The level to log stderr at. Defaults to ERROR.
                stdout: Where to redirect stdout; defaults to logging to the logger specified by the stdout_logger argument.
                stderr: Where to redirect stderr; defaults to logging to the logger specified by the stderr_logger argument.

            Otherwise the same as multiprocessing.Process.
            """

            if stdout_logger is None:
                stdout_logger = logger
            if stderr_logger is None:
                stderr_logger = logger

            if stdout_logger is not None and stdout is None:
                stdout = StreamToLogger(logger=stdout_logger, log_level=stdout_log_level)
            if stderr_logger is not None and stderr is None:
                stderr = StreamToLogger(logger=stderr_logger, log_level=stderr_log_level)
            super(LogOutputProcess, self).__init__(*args, stdout=stdout, stderr=stderr, **kwargs)

    class StreamToQueue:
        """Puts the results of streams (stdout or stderr for example) on a queue."""

        def __init__(self, queue, block=False, **kwargs):
            """Arguments:
                queue: The queue to put the stream on to.
                block: Whether to block if the queue is full. Defaults to False. (In which case the data from the stream
                    will be lost.)
            """

            self.queue = queue
            self.block = block
            super(StreamToQueue).__init__(**kwargs)

        def write(self, buf):
            for line in buf.rstrip().splitlines():
                self.queue.put(line.rstrip(), block=self.block)

        def flush(self):
            pass

    class QueueOutputProcess(RedirectedOutputProcess):
        """Puts the stdout and sterr of a process on a queue."""

        def __init__(self, *args, queue=None, block=False,
                     stdout_queue=None, stderr_queue=None,
                     stdout_block=False, stderr_block=False,
                     stdout=None, stderr=None,
                     **kwargs):
            """Arguments:
                queue: The queue to put both stdout and stderr on.
                block: Whether to block if the queue is full.
                stdout_queue: The queue to put just stdout on; defaults to the value of the queue argument.
                stderr_queue: The queue to put just stderr on; defaults to the value of the queue argument.
                stdout_block: Whether to block when the stdout_queue is full; defaults to the value of the block argument.
                stderr_block: Whether to block when the stderr_queue is full; defaults to the value of the block argument.
                stdout: Where to redirect stdout; defaults to putting on the queue specified by the stdout_queue argument.
                stderr: Where to redirect stderr; defaults to putting on the queue specified by the stderr_queue argument.

            Otherwise the same as multiprocessing.Process.
            """

            if stdout_queue is None and queue is not None:
                stdout_queue = queue
            if stderr_queue is None and queue is not None:
                stderr_queue = queue

            if stdout_block is None and block is not None:
                stdout_block = block
            if stderr_queue is None and block is not None:
                stderr_block = block

            if stdout_queue is not None and stdout is None:
                    stdout = StreamToQueue(queue=stdout_queue, block=stdout_block)
            if stderr_queue is not None and stderr is None:
                    stderr = StreamToQueue(queue=stderr_queue, block=stderr_block)
            super(QueueOutputProcess, self).__init__(*args, stdout=stdout, stderr=stderr, **kwargs)

    globals().update(locals())
