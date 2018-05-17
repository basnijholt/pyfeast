import numpy as np
import feast

UPLO = 'L'

LDA = np.int32(2)
UPLO = b'F' #; // 'L' and 'U' also fine
A = np.array([[2.0,-1.0], [-1.0,2.0]])
Emin = -5.0
Emax = 5.0;
feastparam = np.zeros(64, dtype=np.int32)
feastparam[0] = 1

x = feast.eig(UPLO, A, LDA, feastparam, Emin, Emax)

print(x)