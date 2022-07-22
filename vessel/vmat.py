import numpy as np
from global_variables import gparam

gl = gparam()

# 真空容器内かの判定(真空容器内１，容器外0)
def is_inside_vac(r, z):
    v = 1
    # 現在
    if r<0.2035 or 1.374<r or z<-1.0 or 1.0<z or z<1.327*r-2.322 or -1.327*r+2.322<z:
        v = 0
    
    # 以前
    #if r<0.2035 or 1.374<r or z<-1.394 or 1.394<z or z<1.327*r-2.322 or -1.327*r+2.322<z:
    #    v = 0
    return v

# 真空容器のマトリックス
vac_vessel = np.array([
    [is_inside_vac(r, z) for r in gl.r_pos] for z in gl.z_pos]
    )

# 真空容器のマトリックスを取得
def get_vessel_mat(dmat):
    rmin, rmax, dr = dmat['rmin'], dmat['rmax'], dmat['dr']
    zmin, zmax, dz = dmat['zmin'], dmat['zmax'], dmat['dz']
    
    nr, nz = int((rmax-rmin)/dr+1), int((zmax-zmin)/dz+1)
    
    a = [[is_inside_vac(rmin+i*dr, zmin+j*dr) for i in range(nr)] for j in range(nz)]
    dmat['matrix'] = np.array(a)
    
    return dmat

def get_vessel(cond):
    dmat = cond['resolution'].copy()
    return get_vessel_mat(dmat)
