import os
import numpy as np
import sub.magnetics as mag
import sub.emat as emat
from tqdm import tqdm
from global_variables import gparam

gl = gparam()

path = os.path.join(gl.root_dir, 'device', gl.device_name, 'plasma')
# ディレクトリ有無の確認
if not os.path.exists(path):
    os.makedirs(path)
file = f'plasma_kernel_br_{gl.cname}.npy'

# 粗い行列
# プラズマ電流マトリックスを作成するさいに用いる行列の計算
# 対称性から計算していくので、定義された範囲よりもz方向に広く計算している。
# [nr, 2*nz-1, nr]
mat = []
absfile = os.path.join(path, file)
try:
    mat = np.load(absfile)

except Exception as e:
    print(f'Making plama matrix: {file}.')
    print('Please wait to finish.')
    cz_pos = np.arange(
        gl.cz_min - (gl.cz_max - gl.cz_min), gl.cz_max + gl.cdel_z, gl.cdel_z
    )
    mat = np.array(
        [
            [[mag.br(r, z, rc, gl.cz_min, 1) for r in gl.cr_pos] for z in cz_pos]
            for rc in tqdm(gl.cr_pos)
        ]
    )
    np.save(absfile, mat)

# 粗いマトリックスで(nr, nz)に単位電流が置かれた時の分布
def cget(nz, nr):
    m = mat[nr, gl.cnz - 1 - nz : 2 * gl.cnz - 1 - nz, :]
    return m


# プラズマ電流分布が作るマトリックス
def cbr(pl_mat):
    mat = np.zeros((gl.cnz, gl.cnr))
    for nz in range(gl.cnz):
        for nr in range(gl.cnr):
            mat += pl_mat[nz, nr] * cget(nz, nr)
    return mat


# プラズマ電流分布が作るマトリックス
def cal_plasma_br(dmat):
    """プラズマ電流密度によるフラックス

    Args:
        dmat (dmat): 電流密度のdmat(メッシュ内の総電流ではない)

    Returns:
        _type_: _description_
    """
    # 粗いメッシュにする。
    dm = gl.get_dmat_coarse()
    dm = emat.resampling(dm, dmat)
    dm["matrix"] = cbr(dm["matrix"])
    r = emat.get_dmat_dim(dmat)
    r = emat.resampling(r, dm)
    
    r['matrix'] *= r['dr']*r['dz'] # jtを電流密度とする場合
    
    return r
