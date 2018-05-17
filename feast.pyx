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
        int N,
        np.ndarray[double, ndim=1] A,
        int LDA,
        np.ndarray[int, ndim=1] feastparam,
        double Emin,
        double Emax,
        int M0):
    DTYPE = float
    cdef int loop, mode, info
    cdef double epsout
    cdef np.ndarray _lambda = np.zeros(M0, dtype=DTYPE)
    cdef np.ndarray q = np.zeros(N * M0, dtype=DTYPE)
    cdef np.ndarray res = np.zeros(M0, dtype=DTYPE)
    feastinit_(<int*> feastparam.data)
    dfeast_syev_(UPLO,
                <int*> &N,
                <double*> A.data,
                <int*> &LDA,
                <int*> feastparam.data,
                <double*> &epsout,
                <int*> &loop,
                <double*> &Emin,
                <double*> &Emax,
                <int*> &M0,
                <double*> _lambda.data,
                <double*> q.data,
                <int*> &mode,
                <double*> res.data,
                <int*> &info)
    return {'q': q, '_lambda': _lambda, 'res': res, 'info': info, 'mode': mode, 'loop': loop}
