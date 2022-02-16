import numpy as np
import sub as sb
from global_variables import gparam
gl = gparam()

# PFコイルによるフラックス
def coil_flux(data):
    #data: {'coilname': float_current, 'coilname2': float_current2,}
    
    mat = np.zeros((gl.nz, gl.nr))
    for k in data.keys():
        mat += data[k]*np.load('./coils/data_npy/'+k+'.npy')
        
    return mat

def get_coil_flux(dmat, coil_currents):
    fl = coil_flux(coil_currents)
    dm_f = gl.get_dmat_fine()
    dm_f['matrix'] = np.array(fl)
    return sb.resampling(dmat, dm_f)
