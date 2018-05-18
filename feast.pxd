cdef extern from "feast_tools.h":
    extern void feastinit_(int *feastparam)

def components(which, ctype):
    common = {
        'common1': f'int *feastparam,{ctype} *epsout,int *loop,',
        'common2': f'int *M0,{ctype} *lambda,{ctype} *q,int *mode,{ctype} *res,int *info,',
        'list_I1': f'{ctype} *Emin,{ctype} *Emax,',
        'list_I2': f'{ctype} *Emid,{ctype} *r,',
        'X': {'x': f'{ctype} *Zne,{ctype} *Wne,', '': ''}
    }
    sparse = {
        'list_A1': f'char *UPLO,int *N,{ctype} *sa,int *isa,int *jsa,',
        'list_A2': f'int *N,{ctype} *sa,int *isa,int *jsa,',
        'list_B': {'g': f'{ctype} *sb,int *isb,int *jsb,', 'e': ''}
        }
    banded = {
        'list_A1': f'char *UPLO,int *N,int *kla,{ctype} *A,int *LDA,',
        'list_A2': f'int *N,int *kla,int *kua,{ctype} *A,int *LDA,',
        'list_A3': f'int *N,int *kla,int *kua,{ctype} *A,int *LDA,',
        'list_B1': {'g': f'int *klb,{ctype} *B,int *LDB,', 'e': ''},
        'list_B2': {'g': f'int *klb,int *kub,{ctype} *B,int *LDB,', 'e': ''}
    }
    dense = {
        'list_A1': f'char *UPLO,int *N,{ctype} *A,int *LDA,',
        'list_A2': f'int *N,{ctype} *A,int *LDA,',
        'list_B': {'g': f'{ctype} *B,int *LDB,', 'e': ''}
    }
    components = dict(sparse=sparse, banded=banded, dense=dense)
    components = {k: {**v, **common} for k, v in components.items()}
    return components[which]

dense = """
cdef extern from "feast_dense.h":
    {% for eg in 'eg' %} {% for x in ['x', ''] %}
    extern void {{ zc }}feast_sy{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ zc }}feast_he{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ ds }}feast_sy{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ zc }}feast_ge{{ eg }}v{{ x }}_({{ d.list_A2 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ ds }}feast_ge{{ eg }}v{{ x }}_({{ d.list_A2 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    {% endfor %} {% endfor %}
"""

banded = """
cdef extern from "feast_banded.h":
    {% for eg in 'eg' %} {% for x in ['x', ''] %}
    extern void {{ zc }}feast_sb{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B1[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ zc }}feast_hb{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B1[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ zc }}feast_gb{{ eg }}v{{ x }}_({{ d.list_A2 }}{{ d.list_B2[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ ds }}feast_sb{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B1[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ ds }}feast_gb{{ eg }}v{{ x }}_({{ d.list_A3 }}{{ d.list_B2[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    {% endfor %} {% endfor %}
"""

sparse = """
cdef extern from "feast_sparse.h":
    {% for eg in 'eg' %} {% for x in ['x', ''] %}
    extern void {{ zc }}feast_scsr{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ zc }}feast_hcsr{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ zc }}feast_gcsr{{ eg }}v{{ x }}_({{ d.list_A2 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ ds }}feast_scsr{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ ds }}feast_gcsr{{ eg }}v{{ x }}_({{ d.list_A2 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    {% endfor %} {% endfor %}
"""

print(Template(sparse).render(d=components('sparse', 'double'), zc='z', ds='d').replace(',)', ')'))
print(Template(sparse).render(d=components('sparse', 'float'), zc='c', ds='s').replace(',)', ')'))
print(Template(banded).render(d=components('banded', 'double'), zc='z', ds='d').replace(',)', ')'))
print(Template(banded).render(d=components('banded', 'float'), zc='c', ds='s').replace(',)', ')'))
print(Template(dense).render(d=components('dense', 'double'), zc='z', ds='d').replace(',)', ')'))
print(Template(dense).render(d=components('dense', 'float'), zc='c', ds='s').replace(',)', ')'))