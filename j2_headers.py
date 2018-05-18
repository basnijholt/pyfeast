from collections import defaultdict
from jinja2 import Template


def _get_base_components(ctype):
    common = {
        'common1': [('int', 'feastparam', 'data'), (ctype, 'epsout'), ('int', 'loop')],
        'common2': [('int', 'M0'), (ctype, 'lambda', 'data'), (ctype, 'q', 'data'),
                    ('int', 'mode'), (ctype, 'res', 'data'), ('int', 'info')],
        'list_I1': [(ctype, 'Emin'), (ctype, 'Emax')],
        'list_I2': [(ctype, 'Emid'), (ctype, 'r')],
        'X': {'x': [(ctype, 'Zne'), (ctype, 'Wne')], '': ''},
        'zc': {'double': 'z', 'float': 'c'}[ctype],
        'ds': {'double': 'd', 'float': 's'}[ctype]
    }
    sparse = {
        'list_A1': [('char', 'UPLO'), ('int', 'N'), (ctype, 'sa'), ('int', 'isa'), ('int', 'jsa')],
        'list_A2': [('int', 'N'), (ctype, 'sa'), ('int', 'isa'), ('int', 'jsa')],
        'list_B': {'g': [(ctype, 'sb'), ('int', 'isb'), ('int', 'jsb')], 'e': ''},
        }
    banded = {
        'list_A1': [('char', 'UPLO'), ('int', 'N'), ('int', 'kla'), (ctype, 'A'), ('int', 'LDA')],
        'list_A2': [('int', 'N'), ('int', 'kla'), ('int', 'kua'), (ctype, 'A'), ('int', 'LDA')],
        'list_A3': [('int', 'N'), ('int', 'kla'), ('int', 'kua'), (ctype, 'A'), ('int', 'LDA')],
        'list_B1': {'g': [('int', 'klb'), (ctype, 'B'), ('int', 'LDB')], 'e': ''},
        'list_B2': {'g': [('int', 'klb'), ('int', 'kub'), (ctype, 'B'), ('int', 'LDB')], 'e': ''},
    }
    dense = {
        'list_A1': [('char', 'UPLO'), ('int', 'N'), (ctype, 'A'), ('int', 'LDA')],
        'list_A2': [('int', 'N'), (ctype, 'A'), ('int', 'LDA')],
        'list_B': {'g': [(ctype, 'B'), ('int', 'LDB')], 'e': ''},
    }
    components = dict(sparse=sparse, banded=banded, dense=dense)
    components = {k: {**v, **common} for k, v in components.items()}
    return components


def get_base_components():
    return {k: _get_base_components(k) for k in ['float', 'double']}


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



def _get_call_signatures(ctype):
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


def get_call_signatures():
    return {k: _get_call_signatures(k) for k in ['float', 'double']}


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


def get_template_info(which):
    all_problems = get_problems()
    infos = defaultdict(list)
    headers = defaultdict(list)
    header_components = get_header_components()
    call_signatures = get_call_signatures()
    base_components = get_base_components()
    ctypes = {'s': 'float', 'c': 'float', 'd': 'double', 'z': 'double'}
    pytypes = {'s': 'np.float32', 'c': 'np.complex64',
               'd': 'np.float64', 'z': 'np.complex128'}
    for matrix_type, problems in all_problems.items():
        for T, eg, x, YF, list_A, list_B, list_I in problems:
            info = {}
            ctype = ctypes[T]
            info['ctype'] = ctype            
            info['funcname'] = f'{T}feast_{YF}{eg}v{x}_'
            if which == 'headers':
                c = header_components[ctype][matrix_type]
            else:
                c = call_signatures[ctype][matrix_type]
                info['pytype'] = pytypes[T]
                (t, x1), (t, x2) = base_components[ctype][matrix_type][list_I]
                info['list_I_args'] = f'{t} {x1}, {t} {x2}'
            info['call_sig'] = ''.join([c[list_A], c[list_B][eg],
                                        c['common1'], c[list_I],
                                        c['common2'], c['X'][x]])
            headers[matrix_type].append("extern void {}({})".format(
                info['funcname'], info['call_sig']))
            infos[matrix_type].append(info)

    if which == 'headers':
        return headers
    else:
        return dict(infos)


def create_feast_pxd():
    template = """
cdef extern from "feast_{}.h":
    {}
    """
    header_info = get_template_info('headers')
    headers = {k: '\n    '.join(v) for k, v in header_info.items()}
    headers = {k: template.format(k, v) for k, v in headers.items()}

    base = """
cdef extern from "feast_tools.h":
    extern void feastinit_(int *feastparam)
    """
    file = base + '\n\n'.join(headers.values()) + '\n'
    file = file.replace(',)', ')').replace('lambda', 'lambda_')
    with open('feast.pxd', 'w') as f:
        f.write(file)


if __name__ == '__main__':
    create_feast_pxd()
