try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

classifiers = ['Programming Language :: Python',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3.6',
               'License :: OSI Approved :: MIT License',
               'Operating System :: OS Independent',
               'Development Status :: 4 - Beta',
               'Intended Audience :: Developers',
               'Intended Audience :: System Administrators',
               'Intended Audience :: Science/Research',
               'Intended Audience :: Education',
               'Topic :: Scientific/Engineering',
               'Topic :: Software Development :: Libraries :: Python Modules',
               'Topic :: System :: Distributed Computing',
               'Topic :: System :: Logging',
               'Topic :: Utilities'
               ]

setup(
    name='sdaxen_python_utilities',
    packages=['python_utilities', 'python_utilities.plotting'],
    version='0.1.5',
    description='A collection of useful tools for common Python tasks',
    author='Seth Axen',
    author_email='seth.axen@gmail.com',
    license='MIT',
    url='https://github.com/sdaxen/python_utilities',
    download_url='https://github.com/sdaxen/python_utilities/tarball/0.1.4',
    keywords=['parallelization', 'scripting', 'logging', 'io', 'plotting'],
    classifiers=classifiers
)
