"""Basic utilities for common scripting tasks.

Author: Seth Axen
E-mail: seth.axen@gmail.com
"""
import logging
import time

LOG_LEVELS = (logging.NOTSET, logging.INFO, logging.DEBUG, logging.WARNING,
              logging.ERROR, logging.CRITICAL)


def setup_logging(filename=None, verbose=False, level=-1,
                  timezone=time.localtime, with_level=True, with_time=True,
                  reset=True, writemode="a"):
    """Setup format string, file, and verbosity for logging.

    Parameters
    ----------
    filename : str, optional (default None)
        Log file. If None, logs are written to stdout.
    verbose : bool, optional (default False)
        Write debugging log messages in addition to info.
    level : int, optional (default -1)
        Force specific level for logging. If provided, ignore `verbose`.
    timezone : function, optional (default time.localtime)
        Function that returns a ``time.struct_time`` object. Recommended
        options are time.localtime for local machine time or time.gmtime for
        GMT.
    with_level : bool, optional (default False)
        Include log level in log messages.
    with_time : bool, optional (default True)
        Include system time in log messages.
    reset : bool, optional (default True)
        Description
    writemode : str, optional (default "a")
        Mode for writing to log file if `filename` is specified.
    """
    if reset:
        root = logging.getLogger()
        if root.handlers:
            for handler in root.handlers:
                root.removeHandler(handler)

    if level != -1 and level in LOG_LEVELS:
        log_level = level
    elif verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    msg_format = "%(message)s"
    if with_level:
        msg_format = "%(levelname)s|" + msg_format
    if with_time:
        logging.Formatter.converter = timezone
        msg_format = "%(asctime)s|" + msg_format

    if filename is not None:
        logging.basicConfig(filename=filename, filemode=writemode,
                            level=log_level, format=msg_format)
        logging.debug("Logging to %s" % filename)
    else:
        logging.basicConfig(level=log_level, format=msg_format)
        logging.debug("Logging to stdout")
