import numpy as np
import feast

LDA = 2
UPLO = 'F'  # 'L' and 'U' also fine
A = np.array([[2.0, -1.0], [-1.0, 2.0]])
Emin = -5.0
Emax = 5.0;
feastparam = []

x = feast.eig(UPLO, A, LDA, feastparam, Emin, Emax)

print(x)