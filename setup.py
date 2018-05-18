#!/usr/bin/env python3

import configparser
import sys
import os.path
import numpy
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

import jinja2 as j2

from j2_headers import create_feast_pxd

def guess_libraries():
    """Return the configuration for FEAST if it is available in a known way.

    This is known to work with the FEAST binaries in the conda-forge channel."""
    import ctypes.util
    common_libs = ["feast_dense", "feast_sparse", "feast_banded", "feast", 'mkl_rt', "gfortran", 'iomp5']
    for lib in ['blas', 'openblas']:
        if ctypes.util.find_library(lib):
            return common_libs + [lib]
    else:
        print('Cannot find MKL or openBLAS!')
        sys.exit(1)


def guess_libraries_dirs():
    return [os.path.join(sys.exec_prefix, 'lib')]


def guess_include_dirs():
    return [os.path.join(sys.exec_prefix, 'include')]


def guess(key):
    if key == 'library_dirs':
        return guess_libraries_dirs()
    elif key == 'include_dirs':
        return guess_include_dirs()
    elif key == 'libraries':
        return guess_libraries()


def get_config(config_file='build.conf'):
    # Read build configuration file.
    configs = configparser.ConfigParser()
    try:
        with open(config_file) as f:
            configs.read_file(f)
        config = dict(configs['feast'])
    except IOError:
        print('User-configured build config.')
        config = {}
    except KeyError:
        print('User-configured build config, '
              'but no `feast` section.')
        config = {}

    keys = ['include_dirs', 'library_dirs', 'libraries']
    for k in keys:
        if k in config:
            config[k] = config[k].split()
        else:
            print('Auto configuring `{}` (best guess)'.format(k))
            config[k] = guess(k)    
    
    config['include_dirs'].append(numpy.get_include())
    return config


if __name__ == '__main__':
    ext_params = get_config()
    create_feast_pxd()

    ext_modules=[
        Extension("feast",
                  sources=["feast.pyx"],
                  **ext_params,
        )
    ]

    setup(
      name="pyfeast",
      ext_modules=cythonize(ext_modules),
    )
