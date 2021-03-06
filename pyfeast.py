#!/usr/bin/env python3

import numpy as np
import feast

A = np.array([[2.0, -1.0], [-1.0, 2.0]])
Emin = -5.0
Emax = 5.0

x = feast.dfeast_syev_py(A, Emin, Emax)

print(x)


from scipy.sparse import csr_matrix
with open('system2') as f:
    mat = f.readlines()

data = []
rows = []
cols = []
for l in mat[1:]:
    row_i, col_j, data_real, data_imag = l.split()
    rows.append(int(row_i) - 1)
    cols.append(int(col_j) - 1)
    data.append(float(data_real) + 1j * float(data_imag))

csr_mat = csr_matrix((data, (rows, cols)))

x = feast.zfeast_hcsrev_py(csr_mat, fpm=[(0,1)], Emin=-0.35, Emax=0.23)

print(x)