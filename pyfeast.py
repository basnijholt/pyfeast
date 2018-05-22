import numpy as np
import feast

A = np.array([[2.0, -1.0], [-1.0, 2.0]])
Emin = -5.0
Emax = 5.0

x = feast.dfeast_syev(A, Emin, Emax)

print(x)
