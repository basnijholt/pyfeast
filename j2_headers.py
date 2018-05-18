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


def convert_header_subcomponents(sub_components, ctype):
    from copy import deepcopy
    make_str = lambda v: ','.join([f'{ctype} *{name}' for ctype, name, *_ in v]) + ','
    header_components = deepcopy(sub_components)
    for k, v in sub_components.items():
        if isinstance(v, list):
            header_components[k] = make_str(v)
        elif isinstance(v, dict):
            for _k, _v in v.items():
                if isinstance(_v, list):
                    header_components[k][_k] = make_str(_v)
    return header_components


def get_header_components(ctype):
    components = base_components(ctype)
    return {k: convert_header_subcomponents(v, ctype) for k, v in components.items()}



dense = """
cdef extern from "feast_dense.h":
    {% for eg in 'eg' %} {% for x in ['x', ''] %}
    extern void {{ d.zc }}feast_sy{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.zc }}feast_he{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.ds }}feast_sy{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.zc }}feast_ge{{ eg }}v{{ x }}_({{ d.list_A2 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.ds }}feast_ge{{ eg }}v{{ x }}_({{ d.list_A2 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    {% endfor %} {% endfor %}
"""

banded = """
cdef extern from "feast_banded.h":
    {% for eg in 'eg' %} {% for x in ['x', ''] %}
    extern void {{ d.zc }}feast_sb{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B1[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.zc }}feast_hb{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B1[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.zc }}feast_gb{{ eg }}v{{ x }}_({{ d.list_A2 }}{{ d.list_B2[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.ds }}feast_sb{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B1[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ d.ds }}feast_gb{{ eg }}v{{ x }}_({{ d.list_A3 }}{{ d.list_B2[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    {% endfor %} {% endfor %}
"""

sparse = """
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
    file += Template(sparse).render(d=components['sparse'])
    file += Template(banded).render(d=components['banded'])
    file += Template(dense).render(d=components['dense'])

    # components = get_components('float')
    # file += Template(sparse).render(d=components['sparse'])
    # file += Template(banded).render(d=components['banded'])
    # file += Template(dense).render(d=components['dense'])

    file = file.replace(',)', ')').replace('lambda', 'lambda_')
    with open('feast.pxd', 'w') as f:
        f.write(file)

if __name__ == '__main__':
    create_feast_pxd()
