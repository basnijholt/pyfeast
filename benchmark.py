import sympy
import numpy as np
from scipy.constants import physical_constants
import scipy.sparse as sp
import scipy.sparse.linalg as sla
from types import SimpleNamespace
import kwant
from kwant.continuum import discretize, sympify
import kwant.linalg.mumps as mumps
import time
import argparse

# ****************** general constants and globals *******************
c = physical_constants['speed of light in vacuum'][0]
val_hbar = physical_constants['Planck constant over 2 pi in eV s'][0]
val_m0 = physical_constants['electron mass energy equivalent in MeV'][0]
val_m0 = val_m0 / (c*10**9)**2 * 10**6
val_mu_B = physical_constants['Bohr magneton in eV/T'][0]
val_phi_0 = physical_constants['mag. flux quantum'][0] * (10**9)**2

constants = {
        'm_0': val_m0,
        'phi_0': val_phi_0,
        'mu_B': val_mu_B,
        'hbar': val_hbar
        }

def eigsh(matrix, k, sigma, **kwargs):
    """Call sla.eigsh with mumps support.
    Please see scipy.sparse.linalg.eigsh for documentation.
    """
    class LuInv(sla.LinearOperator):
        def __init__(self, A):
            inst = mumps.MUMPSContext()
            #inst.analyze(A, ordering='pord')
            inst.factor(A)
            self.solve = inst.solve
            sla.LinearOperator.__init__(self, A.dtype, A.shape)
        def _matvec(self, x):
            return self.solve(x.astype(self.dtype))
    opinv = LuInv(matrix - sigma * sp.identity(matrix.shape[0]))
    return sla.eigsh(matrix, k, sigma=sigma, OPinv=opinv, **kwargs)


def get_hexagon(width):
    def hexagon(pos):
        a0 = 0.25*width
        b0 = 0.5*np.sin(np.pi/3.0)*width
        (x, y) = pos
        return (y >- b0 and y < b0 and
                y > -(b0/a0) * (2*a0 - x) and
                y < -(b0/a0) * (x - 2*a0) and
                y < (b0/a0) * (x + 2*a0) and
                y > -(b0/a0) * (x + 2*a0))
    return hexagon


def make_syst(a, width):
    kx, ky, kz = kwant.continuum.momentum_operators

    ham_rashba = kwant.continuum.sympify('''                                                                                                                                         
        B*g*mu_B/2*sigma_z+(hbar**2/(2*m_0)*(k_x/m*k_x+k_y/m*k_y+k_z/m*k_z)-V(x, y))*eye(2)+                                                                 
        alpha_z*(k_x*sigma_y-k_y*sigma_x)+alpha_y*(k_z*sigma_x-k_x*sigma_z)+alpha_x*(k_y*sigma_z-k_z*sigma_y)                                                      
    ''')
    modified = ['V(x, y)']
    ham_rashba = ham_rashba.subs({ kx : kwant.continuum.sympify('k_x-pi/phi_0*B*y')})
    ham1 = ham_rashba
    ham2 = - ham_rashba.conjugate().subs({s: -s for s in [kx, ky, kz]})
    hamiltonian = sympy.Matrix(sympy.BlockDiagMatrix(ham1, ham2))
    hamiltonian[0, 3] = hamiltonian[3, 0] = + kwant.continuum.sympify('Delta_SC')
    hamiltonian[1, 2] = hamiltonian[2, 1] = - kwant.continuum.sympify('Delta_SC')
    subs = {s.conjugate(): s for s in hamiltonian.atoms(sympy.Symbol)}
    subs.update({kwant.continuum.sympify(m).conjugate() : kwant.continuum.sympify(m) for m in modified})
    hamiltonian = hamiltonian.subs(subs)

    template = discretize(hamiltonian, ('x', 'y'), grid_spacing=a)
    wire = kwant.Builder()
    shape = get_hexagon(width)
    wire.fill(template, lambda s: shape([s.pos[0], s.pos[1]]), (0, 0))
    return wire.finalized()


def Hk(syst, **kwargs):
    pars = dict(
        k_z=0.,
        B=0.5,
        m=0.026,
        alpha_z=0.03,
        alpha_x=-0.005,
        alpha_y=-0.01,
        g=-15.,
        V=lambda x, y: 0.05,
        Delta_SC=0.2e-3,
    )
    pars.update(constants)
    pars.update(kwargs)
    return sp.csc_matrix(syst.hamiltonian_submatrix(params=pars, sparse=True))


parser = argparse.ArgumentParser()
parser.add_argument("--latc", type=float, default=0.1)
args = parser.parse_args()


syst = make_syst(args.latc, width=100)

print('Construction time: ', end='')
t_start = time.time()
H = Hk(syst, k_z=0.1)
print(time.time() - t_start)

print('Hamiltonian size: ', H.shape[0])

print('Nonzero elements: ', H.nnz)

print('Diagonalization time with mumps: ', end='')
t_start = time.time()
E, V = eigsh(H, sigma=0, k=8, tol=1e-6)
print(time.time() - t_start)

print('Diagonalization time without mumps: ', end='')
t_start = time.time()
E, V = sla.eigsh(H, sigma=0, k=8, tol=1e-6)
print(time.time() - t_start)

E_max = np.max(E) + 1e-10

print('Diagonalization time with FEAST: ', end='')
import feast
t_start = time.time()
x = feast.zfeast_hcsrev(H, Emin=-E_max, Emax=E_max, k=10)
print(time.time() - t_start)
