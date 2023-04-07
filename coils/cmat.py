import os

import numpy as np
import copy
import sub.emat as emat
from global_variables import gparam

gl = gparam()

# PFコイルによるフラックス
def coil_flux(data):
    # data: {'coilname': float_current, 'coilname2': float_current2,}

    mat = np.zeros((gl.nz, gl.nr))
    for k in data.keys():
        dir = os.path.join(gl.root_dir, f"coils/data_npy/{k}.npy")
        mat += data[k] * np.load(dir)

    return mat


def get_coil_flux(dmat, coil_currents):
    fl = coil_flux(coil_currents)
    dm_f = gl.get_dmat_fine()
    dm_f["matrix"] = np.array(fl)
    return emat.resampling(dmat, dm_f)


def get_flux_of_coil(cond):
    dmat = copy.deepcopy(gl.get_dmat_coarse())
    coil_currents = cond["cur_pf"]
    return get_coil_flux(dmat, coil_currents)
