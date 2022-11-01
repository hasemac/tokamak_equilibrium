import os
import sys

sys.path.append("..")
import copy
import numpy as np
import sub.magnetics as mag
import sub.emat as emat
import sub.sub_func as ssf
from global_variables import gparam

gl = gparam()

# 粗い行列
# プラズマ電流マトリックスを作成するさいに用いる行列の計算
# 対称性から計算していくので、定義された範囲よりもz方向に広く計算している。
# [nr, 2*nz-1, nr]
mat = []
dir = os.path.join(gl.root_dir, "plasma/plasma_kernel_bz_" + gl.cname + ".npy")
try:
    mat = np.load(dir)

except Exception as e:
    print('Making plama matrix. Please wait to finish.')
    cz_pos = np.arange(
        gl.cz_min - (gl.cz_max - gl.cz_min), gl.cz_max + gl.cdel_z, gl.cdel_z
    )
    mat = np.array(
        [
            [[mag.bz(r, z, rc, gl.cz_min, 1) for r in gl.cr_pos] for z in cz_pos]
            for rc in gl.cr_pos
        ]
    )
    np.save(dir, mat)

# 粗いマトリックスで(nr, nz)に単位電流が置かれた時の分布
def cget(nz, nr):
    m = mat[nr, gl.cnz - 1 - nz : 2 * gl.cnz - 1 - nz, :]
    return m


# プラズマ電流分布が作るフラックスのマトリックス
def cbz(pl_mat):
    mat = np.zeros((gl.cnz, gl.cnr))
    for nz in range(gl.cnz):
        for nr in range(gl.cnr):
            mat += pl_mat[nz, nr] * cget(nz, nr)
    return mat


# プラズマ電流分布が作るフラックスのマトリックス
def cal_plasma_bz(dmat):
    """プラズマ電流密度によるフラックス

    Args:
        dmat (dmat): 電流密度のdmat(メッシュ内の総電流ではない)

    Returns:
        _type_: _description_
    """
    # 粗いメッシュにする。
    dm = gl.get_dmat_coarse()
    dm = emat.resampling(dm, dmat)
    dm["matrix"] = cbz(dm["matrix"])
    r = emat.get_dmat_dim(dmat)
    r = emat.resampling(r, dm)
    
    r['matrix'] *= r['dr']*r['dz'] # jtを電流密度とする場合
    
    return r
