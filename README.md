# Python Utilities
Useful tools for common Python tasks.

## Introduction
This package arose from a desire to standardize useful methods and classes I found myself reusing in many projects. These fall into several sub-packages:
- [`scripting`](python_utilities/scripting.py): method with useful defaults and settings for log format, verbosity, and destination
- [`io_tools`](python_utilities/io_tools.py): methods for intelligently guessing file compression from extension and safely buffering numerical data before writing to an HDF5 file
- [`parallel`](python_utilities/parallel.py): determine which options for parallelization are available in the current environment, and run a method on a dataset using a master-slave paradigm. The `Parallelizer` class arose from a common use case of writing/testing/running scripts on a local machine using multiprocessing or multithreading for parallelization but then needing to modify the scripts to use MPI on a large cluster. The `Parallelizer` allows the same script to be run in both contexts without any need for changing code.
- [`plotting`](python_utilities/plotting): useful color schemes for maximum contrast and methods for conversion between color spaces

## Installation
`python_utilities` may be installed in three ways, in order of preference:
1. Using conda: `conda install -c conda-forge sdaxen_python_utilities`
2. Using pip: `pip install sdaxen_python_utilities`
3. From GitHub:
   1. Download the source from this repository
   1. Download this repository to your machine
      - Clone this repository to your machine with `git clone https://github.com/sdaxen/python_utilities.git`
      - OR download an archive by navigating to [https://github.com/sdaxen/python_utilities](https://github.com/sdaxen/python_utilities) and clicking "Clone or download > Download ZIP". Extract the archive.
   2. Add the path to the repository to your `$PYTHONPATH`. On Unix, this can be done with `export PYTHONPATH=[PATH/TO/REPO]:$PYTHONPATH` where `[PATH/TO/REPO]` is replaced with the path on your machine.

## Usage
An example usage of the most common methods/classes is given below.
In this example, we read in a file that contains a range of numbers.
We then compute the product between each of those numbers and a single
number. We do this in parallel, so that as each slave node is ready,
the master sends it a number from the file. All results are logged
to `log.txt`, and the results are saved to a file `products.txt`.
```python
from python_utilities.scripting import setup_logging
from python_utilities.io_tools import smart_open
from python_utilities.parallel import Parallelizer, make_data_iterator


# Methods written for parallel have non-keyword (num1) and keyword (num2)
# arguments. All keyword arguments must be constant across all parallel
# runs, while non-keyword arguments may vary. Here, we will vary num1, but
# num2 will be constant.
def product(num1, num2=100):
    return num1 * num2


# log everything, including logging.debug messages, to log.txt
setup_logging("log.txt", verbose=True)

data_list = []
# smart_open recognizes the .gz extension
with smart_open("numbers.txt.gz", "r") as f:
    for line in f:
        data_list.append(float(line.strip()))

# items in iterator must be lists or tuples (non-keyword args)
data_iterator = make_data_iterator(data_list)
# use multiprocessing if available
parallelizer = Parallelizer(parallel_mode="processes")
run_kwargs = {"out_file": "products.txt",  # save one result per line
              "out_str": "%d\n",  # formatting of output line
              "out_format": lambda x: x,  # modify result before saving
              "logging_str": "Multiplied by %d",  # format log line
              "logging_format": lambda x: (x),  # modify result before logging
              "kwargs": {"num2": 100}}  # pass constant keyword argument

# run the method on every item in the iterator. If out_file specified,
# boolean success is returned. Otherwise, result is returned. Use
# parallelizer.run to run method on all data before returning and return
# in order.
for success, data in parallelizer.run_gen(product, data_iterator,
                                          **run_kwargs):
    print(success)
```
