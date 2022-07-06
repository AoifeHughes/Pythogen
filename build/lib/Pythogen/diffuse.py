import numpy as np
from .nx import extract_graph_info, update_node_attribute
from .narrow_escape import multi_escp


def calc_cell_D_eff_NEP(cell, signal):
    return calc_D_eff(cell['radius'], signal.D,
                            cell['num_pd'],
                            cell['radius_ep'])

def calc_D_eff(r, D, N, ep):
    tau = multi_escp(r, D, N, ep)
    x2 = r**2
    Deff = x2 / (6*tau)
    return Deff

def calc_cell_D_eff_permeability(cell, signal):
    return calc_D_eff_permeability(signal.D, cell['q'],
                                   cell['radius']*2 )

def calc_D_eff_permeability(D,q,l):
    return (D*q*l)/(D+q*l)

def transport(dx, C,A):
    total_outs = np.zeros(C.shape)
    total_ins = np.zeros(C.shape)
    for c in range(len(C)):
        conns = np.where(A[c] == 1)[0]
        outs = dx[conns] # connections deff to us
        out_deff = np.ones(conns.shape) * dx[c]
        out_deff[out_deff > outs] = outs[outs < out_deff]
        tout = out_deff*4*C[c]
        total_ins[conns] += tout 
        total_outs[c] = np.sum(tout)
    return C+total_ins-total_outs

def diffuse(G, D, dt, dx, epochs, name, modifier_fs, signal):
    A, C = extract_graph_info(G, kind=name)
    for f in modifier_fs:
        f(G, A, signal)
    nn = np.sum(A, axis=1)
    dx = ((D*dt)/dx**2 )/nn
    for _ in range(epochs):
        C = transport(dx, C, A)

    update_node_attribute(G, name, C)
