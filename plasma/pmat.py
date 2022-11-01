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
dir = os.path.join(gl.root_dir, "plasma/plasma_kernel_" + gl.cname + ".npy")
try:
    mat = np.load(dir)

except Exception as e:
    print('Making plama matrix. Please wait to finish.')
    cz_pos = np.arange(
        gl.cz_min - (gl.cz_max - gl.cz_min), gl.cz_max + gl.cdel_z, gl.cdel_z
    )
    mat = np.array(
        [
            [[mag.flux(r, z, rc, gl.cz_min, 1) for r in gl.cr_pos] for z in cz_pos]
            for rc in gl.cr_pos
        ]
    )
    np.save(dir, mat)

# 粗いマトリックスで(nr, nz)に単位電流が置かれた時の分布
def cget(nz, nr):
    m = mat[nr, gl.cnz - 1 - nz : 2 * gl.cnz - 1 - nz, :]
    return m


# プラズマ電流分布が作るフラックスのマトリックス
def cflux(pl_mat):
    mat = np.zeros((gl.cnz, gl.cnr))
    for nz in range(gl.cnz):
        for nr in range(gl.cnr):
            mat += pl_mat[nz, nr] * cget(nz, nr)
    return mat


# プラズマ電流分布が作るフラックスのマトリックス
def cal_plasma_flux(dmat):
    """プラズマ電流密度によるフラックス

    Args:
        dmat (dmat): 電流密度のdmat(メッシュ内の総電流ではない)

    Returns:
        _type_: _description_
    """
    # 粗いメッシュにする。
    dm = gl.get_dmat_coarse()
    dm = emat.resampling(dm, dmat)
    dm["matrix"] = cflux(dm["matrix"])
    r = emat.get_dmat_dim(dmat)
    r = emat.resampling(r, dm)
    
    r['matrix'] *= r['dr']*r['dz'] # jtを電流密度とする場合
    
    return r


# パラボリックな電流分布
def d_plasma_cur_parabolic(dmat, r0, z0, ip, radius):
    rmin, rmax, dr = dmat["rmin"], dmat["rmax"], dmat["dr"]
    zmin, zmax, dz = dmat["zmin"], dmat["zmax"], dmat["dz"]
    rpos = np.arange(rmin, rmax + 0.9 * dr, dr)
    zpos = np.arange(zmin, zmax + 0.9 * dz, dz)

    m1 = plasma_cur_parabolic(r0, z0, ip, radius, rpos, zpos)
    dmat["matrix"] = m1
    dmat['matrix'] /= (dr*dz) # jtを電流密度とする場合
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
        d = ((r - r0) ** 2 + (z - z0) ** 2) ** 0.5
        if d < radius:
            return r0**2 - d**2
        else:
            return 0.0

    mat = np.array([[v(r, z, r0, z0, radius) for r in r_pos] for z in z_pos])
    mat = mat / np.sum(mat) * ip

    return mat


def d_set_plasma_parabolic(cond):
    res = copy.deepcopy(cond["resolution"])
    ip = cond["cur_ip"]["ip"]
    r0 = cond["cur_ip"]["r0"]
    z0 = cond["cur_ip"]["z0"]
    radius = cond["cur_ip"]["radius"]

    return d_plasma_cur_parabolic(res, r0, z0, ip, radius)


def trim_plasma_current(cond):
    # ip>0ならjt<0の値は不自然。
    # この場合は全体を底上げした後、トータルを合わせることで
    # トリミングをかける。
    res = copy.deepcopy(cond["resolution"])

    dm = cond["domain"]["matrix"]
    jt = cond["jt"]["matrix"]

    ip = np.sum(jt)
    vmin = np.min(jt)
    vmax = np.max(jt)

    if ip >= 0:
        jt -= vmin
    else:
        jt -= vmax

    jt *= dm
    jt *= ip / np.sum(jt)

    res["matrix"] = jt

    return res

def shift_plasma_profile(cond):
    res = copy.deepcopy(cond["resolution"])
    
    dmat = cond['domain']
    rmin, dr = dmat["rmin"], dmat["dr"]
    zmin, dz = dmat["zmin"], dmat["dz"]
    
    dm = cond["domain"]["matrix"]
    jt = cond["jt"]["matrix"]
    
    # トータルipを保持
    ip0 = np.sum(jt)
    """
    ira = cond["ir_ax"]
    iza = cond["iz_ax"]
    
    ir0 = int((cond["cur_ip"]["r0"]-rmin)/dr)
    iz0 = int((cond["cur_ip"]["z0"]-zmin)/dz)
    
    print(ir0-ira, iz0-iza)
    njt = ssf.shift_x( jt, ir0-ira, 0.0)
    njt = ssf.shift_y(njt, iz0-iza, 0.0)
    """
    # int()は切り捨てなので、round()で四捨五入する。
    ir = round((cond["cur_ip"]["r0"]-cond["r_ax"])/dr)
    iz = round((cond["cur_ip"]["z0"]-cond["z_ax"])/dz)
    #print(ir, iz)
    njt = ssf.shift_x( jt, ir, 0.0)
    njt = ssf.shift_y(njt, iz, 0.0)    
    
    # domain外のjtはゼロにする。
    njt *= dm
    ip1 = np.sum(njt)
    
    # トータルipになるように調整
    njt *= ip0/ip1
    
    res["matrix"] = njt
    
    return res