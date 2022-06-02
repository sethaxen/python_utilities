"""Tools to aid in parallelizing a function call.

Default method is MPI, if available. Fallback is concurrent.futures. If all
else fails, final fallback is serial.

Author: Seth Axen
Email: seth.axen@gmail.com
"""
import os
import sys
import logging
from copy import copy
import multiprocessing
try:
    from itertools import izip as zip
except ImportError:  # python 3
    pass

# upon import, figure out if MPI is available, and decide parallel_mode
MPI_MODE = "mpi"
FUTURES_THREADS_MODE = "threads"
FUTURES_PROCESSES_MODE = "processes"
SERIAL_MODE = "serial"
ALL_PARALLEL_MODES = (MPI_MODE,
                      FUTURES_PROCESSES_MODE, FUTURES_THREADS_MODE,
                      SERIAL_MODE)

available_parallel_modes = []
try:
    from mpi4py import MPI
    available_parallel_modes.append(MPI_MODE)
except ImportError:
    pass

try:
    import concurrent.futures
    available_parallel_modes.append(FUTURES_PROCESSES_MODE)
    available_parallel_modes.append(FUTURES_THREADS_MODE)
except ImportError:
    pass

available_parallel_modes.append(SERIAL_MODE)


def make_data_iterator(data_entries, *iterables):
    """Make an iterator from an iterable of data entries and constant values.

    All iterables should have the same number of entries. Any passed values
    that are not iterators, lists, or tuples will have that same value
    repeated for the entire length of `data_entries`.

    Parameters
    ----------
    data_entries : iterable
        Iterable of data entries.
    *iterables
        One or more iterables or constant values to serve as additional
        data entries. These are zipped into an iterator with `data_entries`.

    Returns
    -------
    iterator : Iterator of tuples, each with an item in `data_entries`
               followed by corresponding items in `iterables`.
    """
    from itertools import repeat, cycle
    try:
        from collections.abc import Iterator
    except ImportError:  # python < 3.10
        from collections import Iterator

    new_iterables = [iter(data_entries), ]
    for iterable in iterables:
        if (isinstance(iterable, Iterator) or
                isinstance(iterable, list) or
                isinstance(iterable, tuple)):
            new_iterables.append(cycle(iterable))
        else:
            new_iterables.append(repeat(iterable))

    return zip(*new_iterables)


def read_bash_var(var, default=None):
    """Rad a bash variable for number of available processes/threads."""
    if var is None:
        return default
    try:
        val = int(os.environ[var])
        logging.debug("Variable %s indicates %d processors" % (var, val))
        return val
    except KeyError:
        logging.debug("Variable %s not set" % (var))
        return default
    except ValueError:
        logging.debug("Variable %s set to non-integer %s" % (var, str(val)))
        return default


def enum(*sequential, **named):
    """Fake an enumerated type.

    Reference:
    ----------
    - http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python

    Parameters
    ----------
    *sequential
        List of items.
    **named
        Dictionary of items.
    """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


class Parallelizer(object):

    """A class to aid in parallelizing a function call.

    Ideal use case is when function calls are expected to have different
    runtimes and each call is completely independent of all others."""

    def __init__(self, parallel_mode=None, num_proc=None,
                 num_proc_bash_var=None, fail_value=False):
        """Choose mode and/or number of processors or use defaults.

        Parameters
        ----------
        parallel_mode : str, optional (default None)
            Mode to use for parallelization. Available modes are
            ('mpi', 'processes', 'threads', 'serial').
        num_proc : int, optional (default None)
            Maximum number of processors to use. Ignored in MPI mode.
        num_proc_bash_var : str, optional (default None)
            Number of available processors will be read from bash variable.
            Ignored if `num_proc` is specified.
        fail_value : any, optional (default False)
            Result to be yielded if specific function evaluation failed.
        """
        preferred_parallel_modes = copy(available_parallel_modes)
        logging.debug("Parallel modes %s are available." %
                      repr(preferred_parallel_modes))
        self.fail_value = fail_value
        self.rank = 0
        self.num_proc = None

        if parallel_mode is not None:
            if parallel_mode not in ALL_PARALLEL_MODES:
                raise KeyError("Parallel mode must be in %s." %
                               (repr(ALL_PARALLEL_MODES)))

            if parallel_mode not in preferred_parallel_modes:
                if self.is_master():
                    logging.warning(
                        "Parallel mode %s not available. Will auto-select a replacement." % (repr(parallel_mode)))
            else:
                preferred_parallel_modes.pop(
                    preferred_parallel_modes.index(parallel_mode))
                preferred_parallel_modes = ([parallel_mode, ] +
                                            preferred_parallel_modes)
                logging.debug("Available parallel modes reorganized to %s." % (
                    repr(preferred_parallel_modes)))

        if num_proc is None:
            num_proc = read_bash_var(num_proc_bash_var)

        for parallel_mode in preferred_parallel_modes:
            logging.debug("Checking if mode %s is valid." %
                          (repr(parallel_mode)))
            mode_num_proc = num_proc
            self.rank = 0

            if parallel_mode == MPI_MODE:
                comm = MPI.COMM_WORLD
                self.rank = comm.Get_rank()
                mpi_num_proc = comm.Get_size()
                mode_num_proc = mpi_num_proc

            if (mode_num_proc is not None and mode_num_proc < 2
                    and parallel_mode != SERIAL_MODE):
                if self.is_master():
                    logging.warning("Only %d processes available. %s mode not available." % (
                        mode_num_proc, repr(parallel_mode)))
                    continue
            elif (mode_num_proc is None
                  and parallel_mode in (FUTURES_PROCESSES_MODE,
                                        FUTURES_THREADS_MODE)):
                mode_num_proc = multiprocessing.cpu_count()
                logging.info("num_proc is not specified. %s mode will use all %d processes" % (
                    repr(parallel_mode), mode_num_proc))
            elif parallel_mode == SERIAL_MODE:
                mode_num_proc = 1

            self.parallel_mode = parallel_mode
            self.num_proc = mode_num_proc
            break

        if self.is_master():
            logging.info(
                "Parallelizer initialized with mode %s and %d processors." % (
                    repr(self.parallel_mode), self.num_proc))

    def is_mpi(self):
        return self.parallel_mode == MPI_MODE

    def is_concurrent(self):
        return self.is_threads() or self.is_processes()

    def is_threads(self):
        return self.parallel_mode == FUTURES_THREADS_MODE

    def is_processes(self):
        return self.parallel_mode == FUTURES_PROCESSES_MODE

    def is_serial(self):
        return self.parallel_mode == SERIAL_MODE

    def is_master(self):
        return self.rank == 0

    def run(self, *args, **kwargs):
        r"""Execute a function in parallel. Return list of results.

        Parameters
        ----------
        func : function
            Function to execute. Argument is single entry of `data_iterator`
            as well as named arguments in `kwargs`.
        data_iterator : iterator
            Iterator where each entry is an argument to `func`. These data
            are communicated between processors so should be as small as
            possible.
        kwargs : dict, optional (default {})
            Named arguments for `func`.
        out_file : str, optional (default None)
            File to write results of function to. If None, results are yielded
            instead of being written to file.
        out_str : str, optional (default "%s\n")
            Format string to be written to output file for each result.
        out_format : function, optional (default str)
            Function to apply to output of `func` to format results to match
            `out_str`.
        logging_str : str, optional (default None)
            Format string to be logged using `logging` for each successful
            result. If None, only errors are logged.
        logging_format : function, optional (default str)
            Function to apply to `data` entries of `data_iterator` to format
            results to match `logging_str`.
        num_proc : int (default None)
            Number of processors to use. If None, maximum number available
            is used. If `is_mpi`, this term is ignored.

        Returns
        -------
        list : List of results of `func`.
        """
        results = [x for x in self.run_gen(*args, **kwargs)]
        return results

    def run_gen(self, func, data_iterator, kwargs={}, out_file=None,
                out_str="%s\n", out_format=str, logging_str=None,
                logging_format=str):
        r"""Execute a function in parallel. Return result iterator.

        Parameters
        ----------
        func : function
            Function to execute. Argument is single entry of `data_iterator`
            as well as named arguments in `kwargs`.
        data_iterator : iterator
            Iterator where each entry is an argument to `func`. These data
            are communicated between processors so should be as small as
            possible.
        kwargs : dict, optional (default {})
            Named arguments for `func`.
        out_file : str, optional (default None)
            File to write results of function to. If None, results are yielded
            instead of being written to file.
        out_str : str, optional (default "%s\n")
            Format string to be written to output file for each result.
        out_format : function, optional (default str)
            Function to apply to output of `func` to format results to match
            `out_str`.
        logging_str : str, optional (default None)
            Format string to be logged using `logging` for each successful
            result. If None, only errors are logged.
        logging_format : function, optional (default str)
            Function to apply to `data` entries of `data_iterator` to format
            results to match `logging_str`.
        num_proc : int (default None)
            Number of processors to use. If None, maximum number available
            is used. If `is_mpi`, this term is ignored.

        Returns
        -------
        iterator : Iterator through results of `func`.
        """
        result_iterator = iter([])

        if self.is_mpi():
            result_iterator = (x for x in self.mpi_run(
                func, data_iterator, kwargs=kwargs, out_file=out_file,
                out_str=out_str, out_format=out_format,
                logging_str=logging_str, logging_format=logging_format))
        elif self.is_concurrent():
            result_iterator = (x for x in self.concurrent_run(
                func, data_iterator, kwargs=kwargs, out_file=out_file,
                out_str=out_str, out_format=out_format,
                logging_str=logging_str, logging_format=logging_format))
        else:
            result_iterator = (x for x in self.serial_run(
                func, data_iterator, kwargs=kwargs, out_file=out_file,
                out_str=out_str, out_format=out_format,
                logging_str=logging_str, logging_format=logging_format))

        return result_iterator

    def serial_run(self, func, data_iterator, kwargs={}, out_file=None,
                   out_str="%s\n", out_format=str, logging_str=None,
                   logging_format=str):
        """Run in serial on a single processor."""
        if out_file is not None:
            fh = open(out_file, "w")

        for data in data_iterator:
            try:
                result = func(*data, **kwargs)

                if out_file is None:
                    yield (result, data)
                else:
                    fh.write(out_str % out_format(result))
                    yield (True, data)

                if result != self.fail_value and logging_str is not None:
                    logging.info(logging_str % logging_format(data))
            except:
                logging.error("Error running: %s" % str(data),
                              exc_info=True)
                yield(self.fail_value, data)

    def concurrent_run(self, func, data_iterator, kwargs={}, out_file=None,
                       out_str="%s\n", out_format=str, logging_str=None,
                       logging_format=str):
        """Run in parallel with concurrent.futures."""
        if self.is_threads():
            executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=self.num_proc)
        else:
            executor = concurrent.futures.ProcessPoolExecutor(
                max_workers=self.num_proc)

        jobs = []
        jobs_dict = {}
        for data in data_iterator:
            job = executor.submit(func, *data, **kwargs)
            jobs.append(job)
            jobs_dict[job] = data

        jobs_iterator = concurrent.futures.as_completed(jobs)

        if out_file is not None:
            fh = open(out_file, "w")

        for job in jobs_iterator:
            data = jobs_dict[job]
            try:
                result = job.result()

                if out_file is None:
                    yield (result, data)
                else:
                    fh.write(out_str % out_format(result))
                    yield (True, data)

                if result != self.fail_value and logging_str is not None:
                    logging.info(logging_str % logging_format(data))

            except KeyboardInterrupt:
                logging.error("Error running: %s" % str(data),
                              exc_info=True)
                executor.shutdown()
                yield(self.fail_value, data)
            except:
                logging.error("Error running: %s" % str(data),
                              exc_info=True)
                yield(self.fail_value, data)

        if out_file is not None:
            fh.close()

        executor.shutdown()

    def mpi_run(self, func, data_iterator, kwargs={}, out_file=None,
                out_str="%s\n", out_format=str, logging_str=None,
                logging_format=str):
        """Run in parallel with MPI.

        Reference:
        ----------
        - https://github.com/jbornschein/mpi4py-examples/blob/master/09-task-pull.py
        """
        comm = MPI.COMM_WORLD
        status = MPI.Status()   # get MPI status object
        tags = enum('READY', 'DONE', 'EXIT', 'START')
        msg = "Proc:%d|" % self.rank

        comm.Barrier()
        mode = MPI.MODE_WRONLY | MPI.MODE_CREATE
        if out_file is not None:
            fh = MPI.File.Open(comm, out_file, mode)

        if self.is_master():
            task_index = 0
            num_workers = comm.Get_size() - 1
            closed_workers = 0
            logging.debug("%sMaster starting with %d workers" % (msg,
                                                                 num_workers))
            try:
                i = 0
                while closed_workers < num_workers:
                    received = comm.recv(source=MPI.ANY_SOURCE,
                                         tag=MPI.ANY_TAG,
                                         status=status)
                    source = status.Get_source()
                    tag = status.Get_tag()
                    if tag == tags.READY:
                        try:
                            data = next(data_iterator)
                        except StopIteration:
                            logging.debug(
                                "%sEnd of data iterator. Closing proc %d" % (
                                    msg, source))
                            comm.send(
                                None, dest=source, tag=tags.EXIT)
                        except:
                            logging.debug("%sCould not get data" % msg)

                        logging.debug(
                            "%sSending task %d to proc %d" % (msg,
                                                              task_index,
                                                              source))
                        comm.send(data, dest=source, tag=tags.START)
                        task_index += 1
                    elif tag == tags.DONE:
                        if received is not None:
                            result, data = received

                            logging.debug(
                                "%sReceived result %d from proc %d" % (
                                    msg, task_index, source))

                            if (result != self.fail_value and
                                    logging_str is not None):
                                logging.info(
                                    logging_str % logging_format(data))

                            if out_file is None or result == self.fail_value:
                                yield (result, data)
                            else:
                                yield (True, data)

                            i += 1

                    elif tag == tags.EXIT:
                        logging.debug("%sExiting proc %d" % (msg, source))
                        closed_workers += 1
            except (KeyboardInterrupt, SystemExit):
                logging.exception("%sError while processing" % msg,
                                  exc_info=True)
                sys.exit()
        else:
            # Worker processes execute code below
            while True:
                comm.send(None, dest=0, tag=tags.READY)
                data = comm.recv(
                    source=0, tag=MPI.ANY_TAG, status=status)
                tag = status.Get_tag()

                if tag == tags.START:
                    try:
                        result = func(*data, **kwargs)

                        if out_file is None:
                            comm.send(
                                (result, data), dest=0, tag=tags.DONE)
                        else:
                            fh.Write_shared(
                                (out_str % out_format(result)).encode("utf-8"))
                            comm.send(
                                (True, data), dest=0, tag=tags.DONE)
                    except:
                        logging.error(
                            "%sError running: %s" % (msg, str(data)),
                            exc_info=True)
                        comm.send(
                            (self.fail_value, data), dest=0, tag=tags.DONE)
                elif tag == tags.EXIT:
                    break

            comm.send(None, dest=0, tag=tags.EXIT)

        if out_file is not None:
            fh.Sync()
            fh.Close()

        comm.Barrier()


if __name__ == "__main__":
    def test_func(num, *args):
        return num * 100

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    data_list = range(100)
    data_iterator = make_data_iterator(data_list, "test")

    parallelizer = Parallelizer(parallel_mode=FUTURES_PROCESSES_MODE)

    run_kwargs = {"out_file": "test_out.txt", "out_str": "%d\n",
                  "out_format": lambda x: x,
                  "logging_str": "Logged %s %d",
                  "logging_format": lambda x: (x[1], x[0])}

    for result in parallelizer.run(test_func, data_iterator, **run_kwargs):
        print(result)
