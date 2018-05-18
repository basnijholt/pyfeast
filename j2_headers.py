from jinja2 import Template

def base_components(ctype):
    common = {
        'common1': [('int', 'feastparam', 'data'), (ctype, 'epsout'), ('int', 'loop')],
        'common2': [('int', 'M0'), (ctype, 'lambda', 'data'), (ctype, 'q', 'data'), ('int', 'mode'), (ctype, 'res', 'data'), ('int', 'info')],
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


def convert_header_subcomponents(sub_components, ctype, make_str_func):
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


def get_header_components(ctype):
    make_str = lambda v: ','.join([f'{ctype} *{name}' for ctype, name, *_ in v]) + ','
    components = base_components(ctype)
    return {k: convert_header_subcomponents(v, ctype, make_str) for k, v in components.items()}


def get_cython_components(ctype):
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
    components = base_components(ctype)
    return {k: convert_header_subcomponents(v, ctype, make_str) for k, v in components.items()}


def get_problems():
    from collections import defaultdict
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
            for type_ in types:
                all_problems[k].append((type_,) + tuple(rest))

    return dict(all_problems)


dense_headers = """
cdef extern from "feast_dense.h":
    {% for eg in 'eg' %} {% for x in ['x', ''] %}
    extern void {{ d.zc }}feast_sy{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.zc }}feast_he{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.ds }}feast_sy{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.zc }}feast_ge{{ eg }}v{{ x }}_({{ d.list_A2 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.ds }}feast_ge{{ eg }}v{{ x }}_({{ d.list_A2 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    {% endfor %} {% endfor %}
"""

banded_headers = """
cdef extern from "feast_banded.h":
    {% for eg in 'eg' %} {% for x in ['x', ''] %}
    extern void {{ d.zc }}feast_sb{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B1[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.zc }}feast_hb{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B1[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.zc }}feast_gb{{ eg }}v{{ x }}_({{ d.list_A2 }}{{ d.list_B2[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.ds }}feast_sb{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B1[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.ds }}feast_gb{{ eg }}v{{ x }}_({{ d.list_A3 }}{{ d.list_B2[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    {% endfor %} {% endfor %}
"""

sparse_headers = """
cdef extern from "feast_sparse.h":
    {% for eg in 'eg' %} {% for x in ['x', ''] %}
    extern void {{ d.zc }}feast_scsr{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.zc }}feast_hcsr{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.zc }}feast_gcsr{{ eg }}v{{ x }}_({{ d.list_A2 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.ds }}feast_scsr{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.ds }}feast_gcsr{{ eg }}v{{ x }}_({{ d.list_A2 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    {% endfor %} {% endfor %}
"""


base = """
cdef extern from "feast_tools.h":
    extern void feastinit_(int *feastparam)
"""


def create_feast_pxd():
    components = get_header_components('double')
    file = base
    file += Template(sparse_headers).render(d=components['sparse'])
    file += Template(banded_headers).render(d=components['banded'])
    file += Template(dense_headers).render(d=components['dense'])

    components = get_components('float')
    file += Template(sparse_headers).render(d=components['sparse'])
    file += Template(banded_headers).render(d=components['banded'])
    file += Template(dense_headers).render(d=components['dense'])

    file = file.replace(',)', ')').replace('lambda', 'lambda_')
    with open('feast.pxd', 'w') as f:
        f.write(file)

if __name__ == '__main__':
    create_feast_pxd()
