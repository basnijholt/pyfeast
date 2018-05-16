import numpy
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

ext_modules=[
    Extension("feast",
              sources=["feast.pyx"],
              libraries=["feast"]
    )
]

setup(
  name="pyfeast",
  ext_modules=cythonize(ext_modules),
  include_dirs = [numpy.get_include()]
)
