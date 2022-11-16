import numpy as np

class dm_array:
    def __init__(self, dmat):
        self.rmin, self.rmax, self.dr = dmat["rmin"], dmat["rmax"], dmat["dr"]
        self.zmin, self.zmax, self.dz = dmat["zmin"], dmat["zmax"], dmat["dz"]
        self.nr = int((self.rmax - self.rmin) / self.dr + 1)
        self.nz = int((self.zmax - self.zmin) / self.dz + 1)
        
        ir = [[e for e in range(self.nr)] for f in range(self.nz)]
        self.ir = np.array(ir).reshape(-1)
        
        iz = [[f for e in range(self.nr)] for f in range(self.nz)]
        self.iz = np.array(iz).reshape(-1)
        
        self.r = self.rmin + self.ir * self.dr
        self.z = self.zmin + self.iz * self.dz

# 同じ構造のdmatを取得
def get_dmat_dim(dmat):
    rmin, rmax, dr = dmat["rmin"], dmat["rmax"], dmat["dr"]
    zmin, zmax, dz = dmat["zmin"], dmat["zmax"], dmat["dz"]
    a = {
        "rmin": rmin,
        "rmax": rmax,
        "dr": dr,
        "zmin": zmin,
        "zmax": zmax,
        "dz": dz,
    }
    return a

# q[nr, nz], r, z が与えられたときに近傍３点の値から線形補間
def linval(r, z, d_mat):
    # 近傍３点の近似式について
    # 4点の値をld(左下), lu(左上), rd(右下), ru(右上)とする。
    # z = ax+by+cとしたとき、
    # それぞれの点で
    # ld = c
    # rd = a+c
    # lu = b+c
    # ru = a+b+c
    #
    # 左下に近いときはruの値を使わないでa,b,cを求めていく。
    # z = (rd-ld)x +(ru-ld)y +ld
    # 右下: luの値を使わない
    # z = (rd-ld)x +(ru-rd)y +ld
    # 左上： rdの値を使わない
    # z = (ru-lu)x +(lu-ld)y +ld
    # 右上: ldの値を使わない
    # z = (ru-lu)x +(ru-rd)y +(lu+rd-ru)
    # 
    # ただし、この方法は領域を移動するときに、ごくわずかに不連続になる。
    #
    mat = d_mat["matrix"]
    rmin = d_mat["rmin"]
    zmin = d_mat["zmin"]
    dr = d_mat["dr"]
    dz = d_mat["dz"]

    nz, nr = mat.shape

    fr = (r - rmin) / dr  # [0,1)
    ir = int(np.floor(fr))
    fr -= ir

    fz = (z - zmin) / dz  # [0, 1)
    iz = int(np.floor(fz))
    fz -= iz

    ir1 = ir + 1
    iz1 = iz + 1

    # 境界からはみ出る場合は一つ戻す。
    if nr == ir + 1:
        ir1 = ir
    if nz == iz + 1:
        iz1 = iz

    # print(ir, ir1, iz, iz1)

    ld = mat[iz, ir]
    rd = mat[iz, ir1]
    lu = mat[iz1, ir]
    ru = mat[iz1, ir1]

    v = 0
    #print(fr, fz)
    if fr <= 0.5 and fz <= 0.5:  # 左下
        #print('ld')
        v = (rd - ld) * fr + (ru - ld) * fz + ld

    elif fr <= 1.0 and fz <= 0.5:  # 右下
        #print('rd')
        v = (rd - ld) * fr + (ru - rd) * fz + ld

    elif fr <= 0.5 and fz <= 1.0:  # 左上
        #print('lu')
        v = (ru - lu) * fr + (lu - ld) * fz + ld

    else:  # 右上
        #print('ru')
        v = (ru - lu) * fr + (ru - rd) * fz + (lu + rd - ru)

    return v

# q[nr, nz], r, z が与えられたときに、周囲４点の中心点と他の２点の計３点で線形補間
def linval2(r, z, d_mat):
    # これはlinvalと異なり、不連続の値を出さない。
    mat = d_mat["matrix"]
    rmin = d_mat["rmin"]
    zmin = d_mat["zmin"]
    dr = d_mat["dr"]
    dz = d_mat["dz"]

    nz, nr = mat.shape

    fr = (r - rmin) / dr  # [0,1)
    ir = int(np.floor(fr))
    fr -= ir

    fz = (z - zmin) / dz  # [0, 1)
    iz = int(np.floor(fz))
    fz -= iz

    ir1 = ir + 1
    iz1 = iz + 1

    # 境界からはみ出る場合は一つ戻す。
    if nr == ir + 1:
        ir1 = ir
    if nz == iz + 1:
        iz1 = iz
    
    ld = mat[iz, ir]
    rd = mat[iz, ir1]
    lu = mat[iz1, ir]
    ru = mat[iz1, ir1]
    fr = fr*2 -1 # -1 <= fr < 1
    fz = fz*2 -1 # -1 <= fz < 1
    
    c = (ld+lu+rd+ru)/4.0 # ４点の平均
    # 原点でゼロになるようにオフセットを差っ引く
    ld -= c
    rd -= c
    lu -= c
    ru -= c
    
    # z = ax + by, c:周囲４点の平均, x = -1, 1, y = -1, 1
    # 下の領域の場合
    # ld = -a -b
    # rd =  a -b より
    # b = -(ld+rd)/2
    # a = (rd-ld)/2
    # 
    # その他の式
    # ru =  a +b
    # lu = -a -b 
    #
    # 従って右の領域の場合
    # a = (rd+ru)/2, b = (ru-rd)/2
    # 
    # 上の場合
    # a = (ru-lu)/2, b = (ru+lu)/2
    # 
    # 左の場合
    # a = -(lu+ld)/2, b = (lu-ld)/2
    a, b = 0, 0
    if fz <= fr and fz <= -fr: # 下の領域
        a = (rd-ld)/2.0
        b = -(ld+rd)/2.0
        
    elif fz <= fr and fz >= -fr: # 右の領域
        a = (rd+ru)/2.0
        b = (ru-rd)/2.0
        
    elif fz >= fr and fz >= -fr: # 上の領域
        a = (ru-lu)/2.0
        b = (ru+lu)/2.0
        
    elif fz >= fr and fz <= -fr: # 左の領域
        a = -(lu+ld)/2.0
        b = (lu-ld)/2.0
    else:
        print('error linval2')
    

    # 最後に平均を足すのを忘れないように
    return a*fr + b*fz + c
        

# 再サンプリング
def resampling(d_mat0, d_mat1):
    # d_mat0: 作成したい行列
    # d_mat1: もとの行列
    # 作成したい行列の情報を取得
    rmin = d_mat0["rmin"]
    zmin = d_mat0["zmin"]
    rmax = d_mat0["rmax"]
    zmax = d_mat0["zmax"]
    dr = d_mat0["dr"]
    dz = d_mat0["dz"]
    nr = int((rmax - rmin) / dr)
    nz = int((zmax - zmin) / dz)

    # nz, nr = d_mat1['matrix'].shape

    mat = [
        [linval2(rmin + i * dr, zmin + j * dz, d_mat1) for i in range(nr + 1)]
        for j in range(nz + 1)
    ]
    d_mat0["matrix"] = np.array(mat)
    return d_mat0

# 加算
def dm_add(dmat0, dmat1):
    mat = dmat0["matrix"] + dmat1["matrix"]
    dmat2 = get_dmat_dim(dmat0)
    dmat2["matrix"] = mat
    return dmat2
    