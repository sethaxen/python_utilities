"""Utilities for I/O and buffering.

Author: Seth Axen
E-mail: seth.axen@gmail.com
"""
import os
import gzip
import bz2
import logging

HDF5_BUFFER_SIZE = 100


class HDF5Buffer(object):

    """Buffer for periodically writing to HDF5 file.

    A kill signal can result in an unclosed and therefore unusable
    HDF5 file. This buffer stores up values, periodically opens the HDF5
    file, flushes values to the file, and then closes it so that the odds
    of the file being left open are low if a kill signal is sent."""

    def __init__(self, filename, write_mode="w", max_size=HDF5_BUFFER_SIZE):
        """Create the buffer.

        Parameters
        ----------
        filename : str
            HDF5 filename
        write_mode : str, optional
            Mode to use for writing ("w" for write, "a" for append)
        max_size : int, optional
            Maximum number of objects to store in buffer before flushing.
        """
        self.filename = filename
        self.buffer = {}
        self.max_size = max_size
        self.size = 0
        self.filehandle = None
        self.open(write_mode=write_mode)
        self.close()

    def add_group(self, name, group_dict):
        """Add a group dict to buffer.

        Parameters
        ----------
        name : str
            Name of group.
        group_dict : dict
            Dict where keys are dataset names and values are kwargs for
            h5py `Group.create_dataset` method.
        """
        logging.debug("Adding group to HDF5 buffer.")
        self.buffer.update({name: group_dict})
        self.size += 1
        if self.size == HDF5_BUFFER_SIZE:
            self.flush()

    def open(self, write_mode="a"):
        """Open HDF5 file."""
        import h5py
        self.filehandle = h5py.File(self.filename, write_mode)

    def close(self):
        """Close HDF5 file if it is open."""
        if self.filehandle is not None:
            self.filehandle.close()
            self.filehandle = None

    def flush(self):
        """Write buffered items to HDF5 file and clear."""
        logging.debug("Flushing HDF5 buffer to %s" % self.filename)
        if self.filehandle is None:
            self.open(write_mode="a")
        for group_name, group_dict in self.buffer.iteritems():
            conf_grp = self.filehandle.create_group(group_name)
            for data_name, data_kwargs in group_dict.iteritems():
                conf_grp.create_dataset(data_name, **data_kwargs)
        self.close()
        self.buffer = {}
        self.size = 0

    def __del__(self):
        """Flush buffer to file upon destruction."""
        self.flush()


def touch_dir(dirname):
    """Create directory if it doesn't exist.

    Parameters
    ----------
    dirname : str
        Directory name.
    """
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except OSError:
            if not os.path.exists(dirname):
                logging.exception("Failed to create %s." % dirname,
                                  exc_info=True)


def smart_open(filename, mode="r", *args, **kwargs):
    """Open file. Assume method of opening by extension.

    Parameters
    ----------
    filename, str
        Name of file
    mode, str
        Mode to open file in
    *args
        Input arguments
    **kwargs
        Keyword arguments

    Returns
    -------
    File-like object : Opened file-like object.
    """
    if os.path.splitext(filename)[-1] == ".gz":
        if len(mode) < 2:
            mode += "b"
        file_class = gzip.GzipFile
    elif os.path.splitext(filename)[-1] == ".bz2":
        if len(mode) < 2:
            mode += "b"
        file_class = bz2.BZ2File
    else:
        return open(filename, mode, *args, **kwargs)

    class SmartOpen(file_class):
        def write(self, text, *args, **kwargs):
            if "b" in mode and not isinstance(text, bytes):
                super(SmartOpen, self).write(text.encode("utf-8"), *args,
                                             **kwargs)
            else:
                super(SmartOpen, self).write(text, *args, **kwargs)

    return SmartOpen(filename, mode, *args, **kwargs)
