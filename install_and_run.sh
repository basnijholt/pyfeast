#!/usr/bin/env bash
rm -fr *.c build *.so *pxd __pycache__
python setup.py build_ext --inplace
python pyfeast.py
