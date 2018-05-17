import numpy
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

ext_modules=[
    Extension("feast",
              sources=["feast.pyx"],
              libraries=["feast_dense", "feast", "m", "gfortran", "openblas"],
              include_dirs=[numpy.get_include(), '/opt/conda/include'],
              library_dirs=['/opt/conda/lib'],
    )
]

setup(
  name="pyfeast",
  ext_modules=cythonize(ext_modules),
)
