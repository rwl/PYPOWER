"""Make B Kron and compute power losses based on Kron Coefficient
Source: Arango Angarita, Dario & Urrego, Ricardo & Rivera, Sergio. (2018). Robust loss coefficients: application to power systems with solar and wind energy.
"""
import numpy as np
from numpy import array, zeros, pi
from numpy.linalg import inv
from pypower.api import ppoption, makeYbus, runpf
from pypower.idx_bus import PD, QD, VM, VA, BUS_TYPE, BUS_I
from pypower.idx_gen import PG, QG, GEN_BUS

def makeB_kron(ppc,pf_alg=1):
    """
    Make B Kron based on Arango Angarita,(2018).
    B Kron can be used to estimate power losses without redoing the power flow.
    """
    Sb = ppc['baseMVA']
    ppopt = ppoption(PF_ALG=pf_alg,VERBOSE=0,OUT_ALL=0,OUT_ALL_LIM=0,OUT_V_LIM=0)
    result,success = runpf(ppc,ppopt)
    if success != 1:
        B=[]
        B0=[]
        B00=[]
        PL=[]
        print("No Solution in Power Flow!")
        return B, B0, B00, PL, success
    Ybus, _, _ = makeYbus(Sb,ppc['bus'],ppc['branch'])
    Zb = inv(Ybus.toarray())
    Pgen = result['gen'][:,PG]/Sb
    Qgen = result['gen'][:,QG]/Sb
    Pdem = result['bus'][:,PD]/Sb
    Qdem = result['bus'][:,QD]/Sb
    v = result['bus'][:,VM]
    theta = result['bus'][:,VA]*(pi/180)
    V = v*(np.exp(1j*theta))
    m = np.size(Pgen)
    n = len(ppc['bus'][:,BUS_I])
    for sl,foo in zip(range(n),result['bus'][:,BUS_TYPE]):
        if foo==3:
            break
    cal = np.transpose([result['gen'][:,GEN_BUS],result['gen'][:,PG],result['gen'][:,QG]])
    Pgen[Pgen==0] = 0.000001/Sb
    nodGen = cal[:,GEN_BUS]
    VGEN = V[nodGen]
    ILK = np.array((Pdem-1j*Qdem)/np.conj(V))
    ID = np.sum(ILK)
    LK = ILK/ID
    T = np.matmul((Zb[sl,:]),LK.T)
    Zb1 = (np.array(Zb[sl,nodGen])).flatten()
    Zb2 = (np.array(Zb[sl,sl])).flatten()
    Zclave = np.hstack((Zb1,Zb2))
    C1a = -1*LK/T
    C1aa = np.transpose([C1a])
    C1 = C1aa*Zclave
    clave = np.arange(m)
    for i in range(m):
        C1[nodGen[i],clave[i]] = 1+C1[nodGen[i],clave[i]]
    C = C1
    PHI = np.zeros([m+1,m+1], dtype=complex)
    for k in range(m):
        F = 1j*(Qgen[k]/Pgen[k])
        PHI[k,k] = (1-F)/(np.conj(VGEN[k]))
    IO = -1*V[sl]/(Zb[sl,sl])
    PHI[m,m] = IO
    PHI = np.array(PHI)
    H = np.real(PHI.dot(C.T).dot(Zb.real).dot(np.conj(C)).dot(np.conj(PHI)))
    B = H[:m,:m]
    B0 = 2*H[m,:m]
    B00 = H[m,m]
    return B, B0, B00, success

def loss_kron_method(kronCoeffResult,baseMVA,Pgen):
    """
    Compute losses based on Kron Method.
    """
    [B,B0,B00]=kronCoeffResult
    Pgen=Pgen/baseMVA #convert to p.u.
    PL_Quadratic=Pgen.T.dot(B).dot(Pgen)*baseMVA
    PL_Linear=B0.dot(Pgen)*baseMVA
    PL_Constant=B00*baseMVA
    PL = (PL_Quadratic+PL_Linear+PL_Constant) #LOSSES_KroonsCoefficient
    return PL,PL_Quadratic,PL_Linear,PL_Constant
