import numpy as np
cimport numpy as np

int_dtype = np.int32


{% for ctype in ['single', 'double'] %} {% for eg in 'eg' %} {% for x in ['x', ''] %}
def {{ funcname }}(np.ndarray[{{ ctype }}, ndim=2] A,
    {{% if eg == 'g' %}}np.ndarray[{{ ctype }}, ndim=2] B,{{% endif %}}
    {{ list_I_args }},
    list feastparam = None,
    UPLO = 'F'):
    if feastparam is None:
        feastparam = []

    if isinstance(UPLO, str):
        UPLO = UPLO.encode()

    DTYPE = {{ pytype }}
    cdef int loop, mode, info
    cdef {{ ctype }} epsout
    cdef int N = A.shape[0]
    cdef int LDA = A.shape[1]
    cdef int M0 = A.shape[1]  # because M0 will change on exit

    {{% if eg == 'g' %}}
    cdef int LDB = A.shape[1]
    {{% endif %}}

    cdef np.ndarray evals = np.zeros(LDA, dtype=DTYPE)
    cdef np.ndarray evecs = np.zeros(N * LDA, dtype=DTYPE)
    cdef np.ndarray res = np.zeros(LDA, dtype=DTYPE)
    cdef np.ndarray fpm = np.zeros(64, dtype=np.int32)

    feastinit_(<int*> fpm.data)
    for k, v in feastparam:
        fpm[k] = v

    {{ funcname }}({{ call_sig }})
    evecs = evecs.reshape((N, LDA))
    return {'evecs': evecs, 'evals': evals, 'res': res, 'info': info, 'mode': mode, 'loop': loop}
{% endfor %} {% endfor %}