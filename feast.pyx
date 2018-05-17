import numpy as np
cimport numpy as np

int_dtype = np.int32

cdef extern from "feast_dense.h":
    extern void dfeast_syev_(
        char *UPLO,
        int *N,
        double *A,
        int *LDA,
        int *feastparam,
        double *epsout,
        int *loop,
        double *Emin,
        double *Emax,
        int *M0,
        double *_lambda,
        double *q,
        int *mode,
        double *res,
        int *info)


cdef extern from "feast_tools.h":
    extern void feastinit_(int *feastparam)


def eig(UPLO,
        np.ndarray[double, ndim=2] A,
        int LDA,
        list feastparam,
        double Emin,
        double Emax):
    if isinstance(UPLO, str):
        UPLO = UPLO.encode()
    DTYPE = float
    cdef int loop, mode, info
    cdef double epsout
    cdef int N = A.shape[0]
    cdef int M = A.shape[1]
    cdef np.ndarray evals = np.zeros(M, dtype=DTYPE)
    cdef np.ndarray evecs = np.zeros(N * M, dtype=DTYPE)
    cdef np.ndarray res = np.zeros(M, dtype=DTYPE)
    cdef np.ndarray fpm = np.zeros(64, dtype=np.int32)

    feastinit_(<int*> fpm.data)
    for k, v in feastparam:
        fpm[k] = v

    dfeast_syev_(UPLO,
                <int*> &N,
                <double*> A.data,
                <int*> &LDA,
                <int*> fpm.data,
                <double*> &epsout,
                <int*> &loop,
                <double*> &Emin,
                <double*> &Emax,
                <int*> &M,
                <double*> evals.data,
                <double*> evecs.data,
                <int*> &mode,
                <double*> res.data,
                <int*> &info)
    evecs = evecs.reshape((N, M))
    return {'evecs': evecs, 'evals': evals, 'res': res, 'info': info, 'mode': mode, 'loop': loop}
