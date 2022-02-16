import os, sys
sys.path.append('..')
import sub as sb
import numpy as np
import electromagnetics as mag
from global_variables import gparam
gl = gparam()

# 粗い行列
# プラズマ電流マトリックスを作成するさいに用いる行列の計算
# 対称性から計算していくので、定義された範囲よりもz方向に広く計算している。
# [nr, 2*nz-1, nr]
mat = []
dir = os.path.join(gl.root_dir, 'plasma\plasma_kernel.npy')
try:
    mat = np.load(dir)
    
except Exception as e:    
    cz_pos = np.arange(gl.cz_min-(gl.cz_max-gl.cz_min), gl.cz_max+gl.cdel_z, gl.cdel_z)
    mat = np.array([[[mag.flux(r, z, rc, gl.cz_min, 1) 
                    for r in gl.cr_pos] 
                    for z in cz_pos] 
                    for rc in gl.cr_pos])
    np.save(dir, mat)

# 粗いマトリックスで(nr, nz)に単位電流が置かれた時の分布
def cget(nz, nr):
    m = mat[nr, gl.cnz-1-nz:2*gl.cnz-1-nz, :]
    return m

# プラズマ電流分布が作るフラックスのマトリックス
def cflux(pl_mat):
    mat = np.zeros((gl.cnz, gl.cnr))
    for nz in range(gl.cnz):
        for nr in range(gl.cnr):
            mat += pl_mat[nz, nr]*cget(nz, nr)
    return mat

# プラズマ電流分布が作るフラックスのマトリックス
def cal_plasma_flux(dmat):
    # 粗いメッシュにする。
    dm = {
        'rmin':gl.cr_min, 'rmax':gl.cr_max, 'dr':gl.cdel_r, 
        'zmin':gl.cz_min, 'zmax':gl.cz_max, 'dz':gl.cdel_z,
        }
    dm = sb.resampling(dm, dmat)
    dm['matrix'] = cflux(dm['matrix'])
    r = sb.get_dmat_dim(dmat)
    r = sb.resampling(r, dm)
    return r 

# パラボリックな電流分布
def d_plasma_cur_parabolic(dmat, r0, z0, ip, radius):
    rmin, rmax, dr = dmat['rmin'], dmat['rmax'], dmat['dr']
    zmin, zmax, dz = dmat['zmin'], dmat['zmax'], dmat['dz']
    rpos = np.arange(rmin, rmax+0.9*dr, dr)
    zpos = np.arange(zmin, zmax+0.9*dz, dz)
    
    m1 = plasma_cur_parabolic(r0, z0, ip, radius, rpos, zpos)
    dmat['matrix'] = m1
    return dmat
 
# パラボリックな電流分布: 合計i [A], r=r0の範囲でパラボリックに分布
def plasma_cur_parabolic(r0, z0, ip, radius, r_pos, z_pos):
    # (r0, z0): プラズマ電流の位置
    # ip: プラズマ電流
    # r_pos, z_pos: メッシュ位置
    # このとき分布は(2*i/pi/r0**4) (r0**2-r**2)に従う。
    # (2*i/pi/r0**4) (r0**2-r**2) はr=r0でゼロになる。また２次元で面積積分したときiになる。
    # だけど、ここではとりあえずパラボリックに分布させて、最後に総和を調整する。    
    def v(r, z, r0, z0, radius):
        d = ((r-r0)**2+(z-z0)**2)**0.5
        if d < radius:
            return (r0**2-d**2)
        else:
            return 0.0
        
    mat = np.array([[v(r, z, r0, z0, radius) for r in r_pos] for z in z_pos]
                )
    mat = mat/np.sum(mat)*ip
    
    return mat