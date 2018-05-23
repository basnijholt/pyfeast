from collections import defaultdict
from jinja2 import Template


CTYPES = {'s': 'float', 'c': 'float', 'd': 'double', 'z': 'double'}

def _get_base_components(ctype):
    common = {
        'common1': [('int', 'feastparam', 'data'), (ctype, 'epsout'), ('int', 'loop')],
        'common2': [('int', 'M0'), (ctype, 'lambda_', 'data'), (ctype, 'q', 'data'),
                    ('int', 'mode'), (ctype, 'res', 'data'), ('int', 'info')],
        'list_I1': [(ctype, 'Emin'), (ctype, 'Emax')],
        'list_I2': [(ctype, 'Emid'), (ctype, 'r')],
        'X': {'x': [(ctype, 'Zne'), (ctype, 'Wne')], '': ''},
        'zc': {'double': 'z', 'float': 'c'}[ctype],
        'ds': {'double': 'd', 'float': 's'}[ctype]
    }
    sparse = {
        'list_A1': [('char', 'UPLO'), ('int', 'N'), (ctype, 'sa', 'data'), ('int', 'isa', 'data'), ('int', 'jsa', 'data')],
        'list_A2': [('int', 'N'), (ctype, 'sa', 'data'), ('int', 'isa', 'data'), ('int', 'jsa', 'data')],
        'list_B': {'g': [(ctype, 'sb'), ('int', 'isb'), ('int', 'jsb')], 'e': ''},
        }
    banded = {
        'list_A1': [('char', 'UPLO'), ('int', 'N'), ('int', 'kla'), (ctype, 'A', 'data'), ('int', 'LDA')],
        'list_A2': [('int', 'N'), ('int', 'kla'), ('int', 'kua'), (ctype, 'A', 'data'), ('int', 'LDA')],
        'list_A3': [('int', 'N'), ('int', 'kla'), ('int', 'kua'), (ctype, 'A', 'data'), ('int', 'LDA')],
        'list_B1': {'g': [('int', 'klb'), (ctype, 'B'), ('int', 'LDB')], 'e': ''},
        'list_B2': {'g': [('int', 'klb'), ('int', 'kub'), (ctype, 'B'), ('int', 'LDB')], 'e': ''},
    }
    dense = {
        'list_A1': [('char', 'UPLO'), ('int', 'N'), (ctype, 'A', 'data'), ('int', 'LDA')],
        'list_A2': [('int', 'N'), (ctype, 'A', 'data'), ('int', 'LDA')],
        'list_B': {'g': [(ctype, 'B'), ('int', 'LDB')], 'e': ''},
    }
    components = dict(sparse=sparse, banded=banded, dense=dense)
    components = {k: {**v, **common} for k, v in components.items()}
    return components


def get_base_components():
    return {k: _get_base_components(k) for k in ['float', 'double']}


def get_problems():
    from itertools import product
    # Table as defined on page 20 of the documentation
    dense = [('zc', 'sy', 'list_A1', 'list_B', 'list_I2'),
             ('zc', 'he', 'list_A1', 'list_B', 'list_I1'),
             ('ds', 'sy', 'list_A1', 'list_B', 'list_I1'),
             ('zc', 'ge', 'list_A2', 'list_B', 'list_I2'),
             ('ds', 'ge', 'list_A2', 'list_B', 'list_I2')]

    banded = [('zc', 'sb', 'list_A1', 'list_B1', 'list_I2'),
              ('zc', 'hb', 'list_A1', 'list_B1', 'list_I1'),
              ('zc', 'gb', 'list_A2', 'list_B2', 'list_I2'),
              ('ds', 'sb', 'list_A1', 'list_B1', 'list_I1'),
              ('ds', 'gb', 'list_A3', 'list_B2', 'list_I2')]

    sparse =[('zc', 'scsr', 'list_A1', 'list_B', 'list_I2'),
             ('zc', 'hcsr', 'list_A1', 'list_B', 'list_I1'),
             ('zc', 'gcsr', 'list_A2', 'list_B', 'list_I2'),
             ('ds', 'scsr', 'list_A1', 'list_B', 'list_I1'),
             ('ds', 'gcsr', 'list_A2', 'list_B', 'list_I2')]

    problems = dict(sparse=sparse, banded=banded, dense=dense)

    # Split the 'zc' and 'ds' into two problems
    all_problems = defaultdict(list)
    for k, v in problems.items():
        for types, *rest in v:
            for type_, eg, x in product(types, 'eg', ['x', '']):
                all_problems[k].append((type_, eg, x) + tuple(rest))

    return dict(all_problems)


def convert_base_components(sub_components, make_str_func):
    from copy import deepcopy
    header_components = deepcopy(sub_components)
    for k, v in sub_components.items():
        if isinstance(v, list):
            header_components[k] = make_str_func(v)
        elif isinstance(v, dict):
            for _k, _v in v.items():
                if isinstance(_v, list):
                    header_components[k][_k] = make_str_func(_v)
    return header_components


def get_header_components():
    components = {}
    base_components = get_base_components()
    for ctype in ['float', 'double']:
        make_str = lambda v: ','.join([f'{ctype} *{name}' for ctype, name, *_ in v]) + ','
        components[ctype] = {k: convert_base_components(v, make_str)
                             for k, v in base_components[ctype].items()}
    return components


def _get_cython_components(ctype):
    def make_str(v):
        s = []
        for tup in v:
            if len(tup) == 2:
                ctype, name = tup
                s.append(f'<{ctype}*> &{name}')
            else:
                ctype, name, size = tup
                s.append(f'<{ctype}*> {name}.data')
        return ', '.join(s)
    components = get_base_components()
    return {k: convert_base_components(v, make_str)
            for k, v in components[ctype].items()}


def get_cython_components():
    return {k: _get_cython_components(k) for k in ['float', 'double']}


def parse_problem(problem):
    keys = 'T', 'eg', 'x', 'YF', 'list_A', 'list_B', 'list_I'
    return dict(zip(keys, problem))


def get_func_name(problem):
    T = problem['T']
    YF = problem['YF']
    eg = problem['eg']
    x = problem['x']
    return f'{T}feast_{YF}{eg}v{x}'


def get_call_sig(problem, matrix_type, components, sep):
    list_A = problem['list_A']
    list_B = problem['list_B']
    list_I = problem['list_I']
    x = problem['x']
    eg = problem['eg']
    ctype = CTYPES[problem['T']]
    c = components[ctype][matrix_type]
    args = [c[list_A], c[list_B][eg], c['common1'],
            c[list_I], c['common2'], c['X'][x]]
    return sep.join(x for x in args if x)


def get_header_info():
    all_problems = get_problems()
    headers = defaultdict(list)
    components = get_header_components()
    for matrix_type, problems in all_problems.items():
        for problem in problems:
            p = parse_problem(problem)
            funcname = get_func_name(p)
            call_sig = get_call_sig(p, matrix_type, components, '')
            call = "extern void {}({})".format(funcname, call_sig)
            headers[matrix_type].append(call)
    return headers


def get_cython_info():
    all_problems = get_problems()
    infos = defaultdict(list)
    components = get_cython_components()
    base_components = get_base_components()
    pytypes = {'s': 'np.float32', 'c': 'np.float64',
               'd': 'np.float64', 'z': 'np.float64'}
    for matrix_type, problems in all_problems.items():
        for problem in problems:
            p = parse_problem(problem)
            ctype = CTYPES[p['T']]
            (t, x1), (t, x2) = base_components[ctype][matrix_type][p['list_I']]
            infos[matrix_type].append(dict(
                ctype=ctype,
                funcname=get_func_name(p),
                pytype=pytypes[p['T']],
                list_I_args=f'{t} {x1}, {t} {x2}',
                call_sig=get_call_sig(p, matrix_type, components, ','),
            ))

    return dict(infos)


def create_feast_pyx():
    t = """import numpy as np
from copy import copy
cimport numpy as np
from scipy.sparse import csr_matrix

int_dtype = np.int32

# Dense matrices
{% for p in problems.dense %}
def {{ p.funcname }}_py(
    np.ndarray[{{ p.ctype }}, ndim=2] A,
    {%- if p.eg == 'g' -%}np.ndarray[{{ p.ctype }}, ndim=2] B,{% endif %}
    {{ p.list_I_args }},
    list fpm = None,
    {%- if "UPLO" in p.call_sig -%}char UPLO = 'F'{% endif %}
    ):
    if fpm is None:
        fpm = []
    {% if "UPLO" in p.call_sig %}
    if isinstance(UPLO, str):
        UPLO = UPLO.encode()
    {% endif %}
    DTYPE = {{ p.pytype }}
    cdef int loop, mode, info
    cdef {{ p.ctype }} epsout
    cdef int N = A.shape[0]
    cdef int LDA = A.shape[1]
    cdef int M0 = A.shape[1]  # because M0 will change on exit
    {% if p.eg == 'g' %}
    cdef int LDB = B.shape[1]
    {% endif %}
    cdef np.ndarray lambda_ = np.zeros(LDA, dtype=DTYPE)
    cdef np.ndarray q = np.zeros(N * LDA, dtype=DTYPE)
    cdef np.ndarray res = np.zeros(LDA, dtype=DTYPE)
    cdef np.ndarray feastparam = np.zeros(64, dtype=np.int32)
    feastinit(<int*> feastparam.data)
    for k, v in fpm:
        feastparam[k] = v

    {{ p.funcname }}({{ p.call_sig }})
    q = q.reshape((N, LDA))
    return {'evecs': q, 'evals': lambda_, 'res': res, 'info': info, 'mode': mode, 'loop': loop}
{% endfor %}


# Sparse matrices
{% for p in problems.sparse %}
def {{ p.funcname }}_py(
    A,
    {%- if p.eg == 'g' -%}np.ndarray[{{ p.ctype }}, ndim=2] B,{% endif %}
    {{ p.list_I_args }},
    int k=40,
    list fpm = None,
{%- if "UPLO" in p.call_sig -%}char UPLO = 'F'{% endif %}
    ):
    if fpm is None:
        fpm = []
{% if "UPLO" in p.call_sig %}
    if isinstance(UPLO, str):
        UPLO = UPLO.encode()
{% endif %}
    if not isinstance(A, csr_matrix):
        A = csr_matrix(A)

    DTYPE = {{ p.pytype }}
    cdef int loop, mode, info
    cdef {{ p.ctype }} epsout
    cdef int N = A.shape[0]
    cdef int M0 = k
{% if p.eg == 'g' %}
    cdef int LDB = B.shape[1]
{% endif %}
    cdef np.ndarray sa = np.zeros(2 * A.data.shape[0], dtype=DTYPE)
    cdef np.ndarray[int, ndim=1] isa
    cdef np.ndarray[int, ndim=1] jsa
    sa[::2] = A.data.real
    sa[1::2] = A.data.imag
    jsa = A.indices.astype(np.int32) + 1  # +1 bc FORTRAN
    isa = A.indptr.astype(np.int32) + 1

    cdef np.ndarray lambda_ = np.zeros(M0, dtype=DTYPE)
    cdef np.ndarray q = np.zeros(2 * N * M0, dtype=DTYPE)
    cdef np.ndarray res = np.zeros(M0, dtype=DTYPE)
    cdef np.ndarray feastparam = np.zeros(64, dtype=np.int32)
    feastinit(<int*> feastparam.data)
    for key, val in fpm:
        feastparam[key] = val

    {{ p.funcname }}({{ p.call_sig }})
    q_real = q[:N*k]
    q_imag = q[N*k:]
    q = (q_real + 1j * q_imag).reshape((N, -1))
    return {'evecs': q, 'evals': lambda_, 'res': res, 'info': info, 'mode': mode, 'loop': loop}
{% endfor %}
"""
    infos = get_cython_info()

    # XXX: temporarily only write the following to the file!
    selected = ['dfeast_syev']
    infos = {k: [x for x in v if x['funcname'] in selected]
             for k, v in infos.items()}

    file = Template(t).render(problems=infos)
    with open('feast.pyx', 'w') as f:
        f.write(file)


def create_feast_pxd():
    template = """
cdef extern from "mkl.h":
    {}
    """
    header_info = get_header_info()
    headers = {k: '\n    '.join(v) for k, v in header_info.items()}
    headers = {k: template.format(v) for k, v in headers.items()}

    base = """
cdef extern from "mkl.h":
    extern void feastinit(int *feastparam)
    """
    file = base + '\n\n'.join(headers.values()) + '\n'
    file = file.replace(',)', ')')
    with open('feast.pxd', 'w') as f:
        f.write(file)


if __name__ == '__main__':
    create_feast_pxd()
    create_feast_pyx()
