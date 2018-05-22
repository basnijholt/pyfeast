import numpy as np
from copy import copy
cimport numpy as np

int_dtype = np.int32

def dfeast_syev(
    np.ndarray[double, ndim=2] A,
    double Emin, double Emax,
    list _feastparam = None,char UPLO = 'F'
    ):
    if _feastparam is None:
        _feastparam = []
    
    if isinstance(UPLO, str):
        UPLO = UPLO.encode()
    
    DTYPE = np.float64
    cdef int loop, mode, info
    cdef double epsout
    cdef int N = A.shape[0]
    cdef int LDA = A.shape[1]
    cdef int M0 = A.shape[1]  # because M0 will change on exit
    
    cdef np.ndarray lambda_ = np.zeros(LDA, dtype=DTYPE)
    cdef np.ndarray q = np.zeros(N * LDA, dtype=DTYPE)
    cdef np.ndarray res = np.zeros(LDA, dtype=DTYPE)
    cdef np.ndarray feastparam = np.zeros(64, dtype=np.int32)
    feastinit_(<int*> feastparam.data)
    for k, v in _feastparam:
        feastparam[k] = v

    dfeast_syev_(<char*> &UPLO, <int*> &N, <double*> A.data, <int*> &LDA,<int*> feastparam.data, <double*> &epsout, <int*> &loop,<double*> &Emin, <double*> &Emax,<int*> &M0, <double*> lambda_.data, <double*> q.data, <int*> &mode, <double*> res.data, <int*> &info)
    q = q.reshape((N, LDA))
    return {'evecs': q, 'evals': lambda_, 'res': res, 'info': info, 'mode': mode, 'loop': loop}
