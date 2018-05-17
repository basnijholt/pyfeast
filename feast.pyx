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
        np.ndarray[np.double_t, ndim=1] A,
        int LDA,
        np.ndarray[np.int32_t, ndim=1] feastparam,
        double epsout,
        int loop,
        double Emin,
        double Emax,
        int M0,
        np.ndarray[np.double_t, ndim=1] _lambda,
        np.ndarray[np.double_t, ndim=1] q,
        int mode,
        np.ndarray[np.double_t, ndim=1] res,
        int info):
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
    return q, _lambda
