
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


def sparse_components(ctype):
    components = {
        'list_A1': f'char *UPLO,int *N,{ctype} *sa,int *isa,int *jsa,',
        'list_A2': f'int *N,{ctype} *sa,int *isa,int *jsa,',
        'list_B': {'g': f'{ctype} *sb,int *isb,int *jsb,', 'e': ''},
        'common1': f'int *feastparam,{ctype} *epsout,int *loop,',
        'common2': f'int *M0,{ctype} *lambda,{ctype} *q,int *mode,{ctype} *res,int *info,',
        'list_I1': f'{ctype} *Emin,{ctype} *Emax,',
        'list_I2': f'{ctype} *Emid,{ctype} *r,',
        'X': {'x': f'{ctype} *Zne,{ctype} *Wne,', '': ''}
    }
    return components

t = """
cdef extern from "feast_sparse.h":
    {% for eg in 'eg' %} {% for x in ['x', ''] %}
    extern void {{ zc }}feast_hcsr{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ zc }}feast_gcsr{{ eg }}v{{ x }}_({{ d.list_A2 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ zc }}feast_scsr{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ ds }}feast_scsr{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ ds }}feast_gcsr{{ eg }}v{{ x }}_({{ d.list_A2 }}{{ d.list_B[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    {% endfor %} {% endfor %}
"""

print(Template(t).render(d=sparse_components('double'), zc='z', ds='d'))
print(Template(t).render(d=sparse_components('float'), zc='c', ds='s'))

def banded_components(ctype):
    components = {
        'list_A1': f'char *UPLO,int *N,int *kla,{ctype} *A,int *LDA,',
        'list_A2': f'int *N,int *kla,int *kua,{ctype} *A,int *LDA,',
        'list_A3': f'int *N,int *kla,int *kua,float *A,int *LDA,',
        'list_B1': {'g': f'int *klb,{ctype} *B,int *LDB,', 'e': ''},
        'list_B2': {'g': f'int *klb,int *kub,{ctype} *B,int *LDB,', 'e': ''},
        'common1': f'int *feastparam,{ctype} *epsout,int *loop,',
        'common2': f'int *M0,{ctype} *lambda,{ctype} *q,int *mode,{ctype} *res,int *info,',
        'list_I1': f'{ctype} *Emin,{ctype} *Emax,',
        'list_I2': f'{ctype} *Emid,{ctype} *r,',
        'X': {'x': f'{ctype} *Zne,{ctype} *Wne,', '': ''}
    }
    return components

t = """
cdef extern from "feast_banded.h":
    {% for eg in 'eg' %} {% for x in ['x', ''] %}
    extern void {{ zc }}feast_sb{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B1[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ zc }}feast_hb{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B1[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ zc }}feast_gb{{ eg }}v{{ x }}_({{ d.list_A2 }}{{ d.list_B2[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ ds }}feast_sb{{ eg }}v{{ x }}_({{ d.list_A1 }}{{ d.list_B1[eg] }}{{ d.common1 }}{{ d.list_I1 }}{{ d.common2 }}{{ d.X[x] }})
    extern void {{ ds }}feast_gb{{ eg }}v{{ x }}_({{ d.list_A3 }}{{ d.list_B2[eg] }}{{ d.common1 }}{{ d.list_I2 }}{{ d.common2 }}{{ d.X[x] }})
    {% endfor %} {% endfor %}
"""

print(Template(t).render(d=banded_components('double'), zc='z', ds='d').replace(',)', ')'))
print(Template(t).render(d=banded_components('float'), zc='c', ds='s').replace(',)', ')'))