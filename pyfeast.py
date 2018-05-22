import numpy as np
import feast

A = np.array([[2.0, -1.0], [-1.0, 2.0]])
Emin = -5.0
Emax = 5.0

x = feast.dfeast_syev(A, Emin, Emax)

print(x)



import scipy.sparse.linalg
with open('system2') as f:
    mat = f.readlines()

data = []
rows = []
cols = []
for l in mat[1:]:
    row_i, col_j, data_real, data_imag = l.split()
    rows.append(int(row_i)-1)
    cols.append(int(col_j)-1)
    data.append(float(data_real) + 1j * float(data_imag))

csr_mat = scipy.sparse.csr.csr_matrix((data, (rows, cols)))

x = feast.zfeast_hcsrev(csr_mat, Emin=-0.35, Emax=0.23)

print(x)