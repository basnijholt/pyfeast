#!/usr/bin/env bash
CFLAGS="-I/opt/conda/include" LDFLAGS="-L/opt/conda/lib" python setup.py build_ext --inplace
