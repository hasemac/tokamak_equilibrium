import numpy as np
import plot as pl
import coils.cmat as cmat
import vessel.vmat as vmat
import plasma.pmat as pmat
from global_variables import gparam
gl = gparam()

# 同じ構造のdmatを取得
def get_dmat_dim(dmat):
    rmin, rmax, dr = dmat['rmin'], dmat['rmax'], dmat['dr']
    zmin, zmax, dz = dmat['zmin'], dmat['zmax'], dmat['dz']
    a = {
        'rmin': rmin, 'rmax': rmax, 'dr': dr,
        'zmin': zmin, 'zmax': zmax, 'dz': dz,
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
    mat = d_mat['matrix']
    rmin = d_mat['rmin']
    zmin = d_mat['zmin']
    dr = d_mat['dr']
    dz = d_mat['dz']
    
    nz, nr = mat.shape
    
    fr = (r-rmin)/dr # [0,1)
    ir = int(np.floor(fr))
    fr -= ir
    
    fz = (z-zmin)/dz # [0, 1)
    iz = int(np.floor(fz))
    fz -= iz
    
    ir1 = ir+1
    iz1 = iz+1
    
    # 境界からはみ出る場合は一つ戻す。
    if nr == ir+1:
        ir1 = ir
    if nz == iz+1:
        iz1 = iz
    
    #print(ir, ir1, iz, iz1)
    
    ld = mat[iz,  ir ]
    rd = mat[iz,  ir1]
    lu = mat[iz1, ir ]
    ru = mat[iz1, ir1]
    
    v = 0
    if fr <= 0.5 and fz <= 0.5: # 左下
        v = (rd-ld)*fr +(ru-ld)*fz +ld
    
    elif fr <=1.0 and fz <= 0.5: # 右下
        v = (rd-ld)*fr +(ru-rd)*fz +ld
    
    elif fr <=0.5 and fz <= 1.0: # 左上
        v = (ru-lu)*fr +(lu-ld)*fz +ld
        
    else: # 右上
        v = (ru-lu)*fr +(ru-rd)*fz +(lu+rd-ru)
    
    return v

# 再サンプリング
def resampling(d_mat0, d_mat1):
    # d_mat0: 作成したい行列
    # d_mat1: もとの行列
    # 作成したい行列の情報を取得
    rmin = d_mat0['rmin']
    zmin = d_mat0['zmin']
    rmax = d_mat0['rmax']
    zmax = d_mat0['zmax']    
    dr = d_mat0['dr']
    dz = d_mat0['dz']
    nr = int((rmax-rmin)/dr)
    nz = int((zmax-zmin)/dz)
    
    #nz, nr = d_mat1['matrix'].shape
    
    mat = [[linval(rmin + i*dr, zmin + j*dz, d_mat1) 
            for i in range(nr+1)] 
           for j in range(nz+1)]
    d_mat0['matrix']=np.array(mat)
    return d_mat0

# 加算
def dm_add(dmat0, dmat1):
    mat = dmat0['matrix'] + dmat1['matrix']
    dmat2 = get_dmat_dim(dmat0)
    dmat2['matrix'] = mat
    return dmat2

def get_normalized_flux(dm_flux, dm_domain):
    # dm_flux: total flux (coil + plasma)
    # dm_domain: domain
    # return: dmat, normalized flux
    # 0: 磁気軸、1: 最外殻磁気面、0: 磁気面外
    res = get_dmat_dim(dm_domain)
    faxis, fsurf = dm_domain['f_axis'], dm_domain['f_surf']
    d = dm_domain['matrix']
    f = dm_flux['matrix']
    f = (f-faxis)/(fsurf-faxis) # normalized flux
    f *= d # domainの外にあるのはゼロにする。
    res['matrix'] = f
    return res

def get_pressure_polcurrent(dm_flux, dm_domain, param_press, param_polcur):
    # params_press: プラズマ圧力の多項式の係数
    # param_polcur: ポロイダルカレントI^2の係数
    
    rmin, rmax, dr = dm_domain['rmin'], dm_domain['rmax'], dm_domain['dr']
    zmin, zmax, dz = dm_domain['zmin'], dm_domain['zmax'], dm_domain['dz']
    nr, nz = int((rmax-rmin)/dr+1), int((zmax-zmin)/dz+1)  

    ir = np.array([[e for e in range(nr)] for f in range(nz)]).reshape(-1)
    iz = np.array([[f for e in range(nr)] for f in range(nz)]).reshape(-1)    
    r = rmin + ir*dr        

    dm_nf = get_normalized_flux(dm_flux, dm_domain)
    f = dm_nf['matrix'].reshape(-1)
    d = dm_domain['matrix'].reshape(-1)   
        
    # 最外殻磁気面の内部のみ取り出す。
    ir = ir[d == 1]
    iz = iz[d == 1]
    r = r[d == 1]
    f = f[d == 1]
    
    npr = len(param_press)
    ncu = len(param_polcur)
    
    # 多項式の各項, n, p
    # an: x^n-x^p, これを積分すると次の式
    # an: x^(n+1)/(n+1)-x^(p+1)/(p+1), 1/(n+1)-1/(p+1) if x = 1
    # 例えば最外殻磁気面(x=1)ではプラズマ圧力がゼロとするならオフセットを各項に足す必要ある。つまり、
    # an: (x^(n+1)-1)/(n+1)-(x^(p+1)-1)/(p+1)
    
    # 圧力に関する行列作成
    p0 = np.array([((f**(i+1)-1)/(i+1)-(f**(npr+1)-1)/(npr+1)) for i in range(npr)])    
    p0 = p0.transpose()
    p0 = np.dot(p0, param_press)
    m_pre = np.zeros((nz, nr))
    for v, i, j in zip(p0, ir, iz):
        m_pre[j, i] = v
        
    # I^2に関する行列作成
    p1 = np.array([((f**(i+1)-1)/(i+1)-(f**(npr+1)-1)/(npr+1)) for i in range(ncu)])
    p1 = p1.transpose()
    p1 = np.dot(p1, param_polcur)
    m_pol = np.zeros((nz, nr))
    for vi, i, j in zip(p1, ir, iz):
        m_pol[j, i] = v
        
    dm_press  = get_dmat_dim(dm_flux)
    dm_polcur = get_dmat_dim(dm_flux)

    dm_press['matrix'] = m_pre
    dm_polcur['matrix'] = m_pol
    
    return dm_press, dm_polcur
        
# flux値の極小位置の探索
def search_local_min(dm_flx, dm_vv):
    rmin, rmax, dr = dm_flx['rmin'], dm_flx['rmax'], dm_flx['dr']
    zmin, zmax, dz = dm_flx['zmin'], dm_flx['zmax'], dm_flx['dz']
    nr, nz = int((rmax-rmin)/dr+1), int((zmax-zmin)/dz+1)
    
    fl, vv = dm_flx['matrix'], dm_vv['matrix']
    
    ir, iz = int(nr/2), int(nz/2)
    
    while vv[iz, ir] == 1: # 真空容器外になったら探索終了
        if fl[iz, ir] > fl[iz+1, ir]:
            iz += 1
        elif fl[iz, ir] > fl[iz-1, ir]:
            iz -= 1
        elif fl[iz, ir] > fl[iz, ir+1]:
            ir += 1
        elif fl[iz, ir] > fl[iz, ir-1]:
            ir -= 1
        else:
            break
    
    if vv[iz, ir] == 0:
        ir, iz = 0, 0
        
    return (ir, iz)
     
# 最外殻磁気面の探索
def search_domain(dm_flx, dm_vv):
    # dm_flx: fluxのdmat
    # dm_vv: 真空容器のdmat
    rmin, rmax, dr = dm_flx['rmin'], dm_flx['rmax'], dm_flx['dr']
    zmin, zmax, dz = dm_flx['zmin'], dm_flx['zmax'], dm_flx['dz']
    nr, nz = int((rmax-rmin)/dr+1), int((zmax-zmin)/dz+1)
    
    # 返り値の作成
    res = get_dmat_dim(dm_flx)
        
    # 領域の初期化
    dm = np.zeros((nz, nr))    
    
    # 真空容器内の極小値を探索してシードとして追加
    k, l = search_local_min(dm_flx, dm_vv)
    dm[l, k+1]= 1.0 # 極小値の一つ右側に設定
    
    # 値を記録
    res['ir_ax'] = k
    res['iz_ax'] = l
    res['r_ax'] = rmin + k*dr
    res['z_ax'] = zmin + l*dr
            
    # 磁気軸と最外殻磁気面とヌル点フラックスの定義
    fax = dm_flx['matrix'][l, k]
    fsurf = fax
    fnull = fax
    
    # 一次元配列を作成
    m0 = dm_flx['matrix'].reshape(-1)
    vv = dm_vv['matrix'].reshape(-1)
    ir = np.array([[e for e in range(nr)] for f in range(nz)]).reshape(-1)
    iz = np.array([[f for e in range(nr)] for f in range(nz)]).reshape(-1)    

    # 小さい値順に並び替える
    ix = m0.argsort()
    m0, ir, iz, vv = m0[ix], ir[ix], iz[ix], vv[ix]
    
    # パディング
    dm2 = np.pad(dm, [(1, 1), (1, 1)])
    
    for f, i, j, v in zip(m0, ir, iz, vv):
        ni, nj = i+1, j+1 # paddingしているので、1を足す。    
        a = dm2[nj-1:nj+2, ni-1:ni+2].reshape(-1)
        a = np.sum(a) # 近接点にプラズマが存在していること。
        # 新しい点に対する判定
        con = a > 0 # 存在していれば1、その他はゼロ
        
        # 他のプラズマと接触して、かつ真空容器内
        if con and 1 == v:
            dm2[nj, ni] = con
            continue

        # 他のプラズマと接触して且つ真空容器外なら探索終了
        # リミター配位
        if con and 0 == v:
            fsurf = f
            break   
            
        # 接触しておらず、真空容器外
        # この場合はなにもしない。
        
        # 接触しておらず、真空容器内
        # この場合はダイバータ配位のプライベートリージョン
        # ヌル点のフラックス値を記録しておく。
        if not con and 1 == v:
            fnull = f
            
    dm3 = dm2[1:1+nz, 1:1+nr]
        
    # ダイバータ配位かどうかの判定
    if fnull != fax:
        # ダイバータ配位の場合、ヌル点近傍でほとんどフラックスが変化しない。
        # ある値で切り上げたほうが多分良い。
        fsurf = fax + 0.88*(fnull-fax)
        dm3[iz[m0 >= fsurf], ir[m0 >= fsurf]] = 0
        
        res['conf_div'] = 1
    else:
        res['conf_div'] = 0

    res['matrix'] = dm3
    res['f_axis'] = fax
    res['f_surf'] = fsurf
    
    return res

# 体積平均の算出
def get_volume_average(dm_val, dm_domain):
    # dm_val: 例えばプラズマ圧力など
    rmin, rmax, dr = dm_domain['rmin'], dm_domain['rmax'], dm_domain['dr']
    zmin, zmax, dz = dm_domain['zmin'], dm_domain['zmax'], dm_domain['dz']
    nr, nz = int((rmax-rmin)/dr+1), int((zmax-zmin)/dz+1)
        
    m = dm_domain['matrix'].reshape(-1)
    v = dm_val['matrix'].reshape(-1)    
    ir = np.array([[e for e in range(nr)] for f in range(nz)]).reshape(-1)
    iz = np.array([[f for e in range(nr)] for f in range(nz)]).reshape(-1)

    # domain内のみ考える。
    ir = ir[m == 1]
    iz = iz[m == 1]
    v = v[m == 1]

    r = rmin + dr*ir
    vol = np.sum(2*np.pi*r*dr*dz) # plasma volume
    v = np.sum(2*np.pi*r*dr*dz*v) # vol*val
    
    return v/vol
         
# 最外殻磁気面形状
def set_domain_params(dmat):
    rmin, rmax, dr = dmat['rmin'], dmat['rmax'], dmat['dr']
    zmin, zmax, dz = dmat['zmin'], dmat['zmax'], dmat['dz']
    nr, nz = int((rmax-rmin)/dr+1), int((zmax-zmin)/dz+1)

    m = dmat['matrix'].reshape(-1)
    ir = np.array([[e for e in range(nr)] for f in range(nz)]).reshape(-1)
    iz = np.array([[f for e in range(nr)] for f in range(nz)]).reshape(-1)
    ir = ir[m == 1]
    iz = iz[m == 1]
    r = rmin + dr*ir
    z = zmin + dz*iz
    
    # rminがある位置
    v = np.min(ir)
    r_rmin = rmin + dr*np.mean(ir[ir == v])
    z_rmin = zmin + dz*np.mean(iz[ir == v])    
    dmat['r_rmin'] = r_rmin
    dmat['z_rmin'] = z_rmin
    
    # rmaxがある位置
    v = np.max(ir)
    r_rmax = rmin + dr*np.mean(ir[ir == v])
    z_rmax = zmin + dz*np.mean(iz[ir == v])
    dmat['r_rmax'] = r_rmax
    dmat['z_rmax'] = z_rmax

    # zminがある位置
    v = np.min(iz)
    r_zmin = rmin + dr*np.mean(ir[iz == v])
    z_zmin = zmin + dz*np.mean(iz[iz == v])
    dmat['r_zmin'] = r_zmin
    dmat['z_zmin'] = z_zmin
    
    # zmaxがある位置
    v = np.max(iz)
    r_zmax = rmin + dr*np.mean(ir[iz == v])
    z_zmax = zmin + dz*np.mean(iz[iz == v])
    dmat['r_zmax'] = r_zmax
    dmat['z_zmax'] = z_zmax
    
    a0 = (r_rmax - r_rmin)/2.0
    r0 = (r_rmax + r_rmin)/2.0
    dmat['major_radius'] = r0
    dmat['minor_radius'] = a0
    dmat['elongation'] = (z_zmax - z_zmin)/(r_rmax-r_rmin)
    dmat['triangularity'] = (r0 - r_zmax)/a0
    dmat['volume'] = np.sum(2*np.pi*r*dr*dz)
    dmat['cross_section'] = np.sum(m[m == 1])*dr*dz
       
# 平衡計算
def calc_equi(dm_jt, dm_flux, dm_domain, npr, ncu):
    # dm_jt: プラズマ電流
    # dm_flux: total fluxのdmat (コイル由来＋プラズマ由来)
    # dm_domain: 最外殻磁気面のdmat
    # npr: pressureに関するパラメータの個数
    # ncu: poloidal電流に関するパラメータの個数
    #
    # out: dmat_jt
    
    rmin, rmax, dr = dm_domain['rmin'], dm_domain['rmax'], dm_domain['dr']
    zmin, zmax, dz = dm_domain['zmin'], dm_domain['zmax'], dm_domain['dz']
    nr, nz = int((rmax-rmin)/dr+1), int((zmax-zmin)/dz+1)  
    
    ir = np.array([[e for e in range(nr)] for f in range(nz)]).reshape(-1)
    iz = np.array([[f for e in range(nr)] for f in range(nz)]).reshape(-1)    
    r = rmin + ir*dr

    # fluxの正規化
    dm_nf = get_normalized_flux(dm_flux, dm_domain)
    f = dm_nf['matrix'].reshape(-1)

    j = dm_jt['matrix'].reshape(-1)
    jtotal = np.sum(j) # 全電流を保持しておく
    
    d = dm_domain['matrix'].reshape(-1)   
    
    # 最外殻磁気面の内部のみ取り出す。
    ir = ir[d == 1]
    iz = iz[d == 1]
    r = r[d == 1]
    j = j[d == 1]
    f = f[d == 1]
    
    # 例えばパラメータ数が３の場合の時
    # (1-x^3) *a0 + (x^1-x^3)*a1 + (x^2-x^3)*a2
    # という形になることに注意すること
    
    # 圧力に関する行列作成
    p0 = np.array([2 * np.pi * r *(f**i-f**npr) for i in range(npr)])
    # I^2に関する行列作成
    p1 = np.array([10**(-7)/(r+10**(-7)) * (f**i-f**ncu) for i in range(ncu)])
    # 結合させて転置、この時点で[point数, パラメータ数]の形
    a = np.vstack([p0, p1]).transpose()
    
    # 次にAbs(a x -j)を最小とするxを求めればよい。
    # A[p, n] x[n] = j[p]
    # このときのxは、At.A x = At.jを満たすxである。
    
    m0 = np.dot(a.transpose(), a)    
    m1 = np.dot(a.transpose(), j)
    
    # m0にほんのわずかな値を加算してsingular matrixになるのを避ける
    #dd = np.min(np.abs(m0))*10**(-7)
    #m0 += np.identity(npr+ncu)*dd
    
    params = np.dot(np.linalg.inv(m0), m1)
    
    # エラー値の算出
    j0 = np.dot(a, params) # 新しい電流
    j0 *= jtotal/np.sum(j0) # トータルの電流値が維持されるように調整
    
    errest = np.sum((j0-j)**2)/2
    # 評価方法はいくつか考えられる。単位メッシュ当たりのエラーに直すとか。
    
    # 新しい電流分布の作成
    j_new = np.zeros((nz, nr))
    for i, j, v in zip(ir, iz, j0):
        j_new[j, i] = v
    
    res = get_dmat_dim(dm_jt)
    res['matrix'] = j_new
    res['error'] = errest
    res['param_p'] = params[0:npr]
    res['param_i2'] = params[npr:]
    return res   

# 平衡計算
def equilibrium(coil_currents, plasma_current, npre, npol):
    # npre: pressureの係数の個数
    # npol: poloidal currentの係数の個数
    
    err = []
    
    # 真空容器
    dm_vv = gl.get_dmat_coarse()
    dm_vv = vmat.get_vessel_mat(dm_vv)

    # コイルによるフラックス
    dm_fc = gl.get_dmat_coarse()
    dm_fc = cmat.get_coil_flux(dm_fc, coil_currents)
    
    # プラズマ電流
    dm_jt = gl.get_dmat_coarse()
    dm_jt = pmat.d_plasma_cur_parabolic(dm_jt, 0.6, 0.0, plasma_current, 0.3)
    
    for i in range(100):
        # プラズマ電流によるフラックス
        dm_fp = gl.get_dmat_coarse()
        dm_fp = pmat.cal_plasma_flux(dm_jt)
        
        # トータルのフラックス
        dm_flux = dm_add(dm_fp, dm_fc)
        
        # 最外殻磁気面
        dm_dm = search_domain(dm_flux, dm_vv)

        # プラズマ平衡
        dm_jt = calc_equi(dm_jt, dm_flux, dm_dm, npre, npol)
        
        # エラー値を記録
        err.append(dm_jt['error'])
        
        print(dm_jt['error'])
        
        if len(err) <=1:
            continue 
        
        # 前回値よりエラー値が大きくなったら終了        
        if err[-1] > err[-2]:
            break
        
        # 一番最初の変化量に対して、最新の変化量が十分小さければ終了
        v = np.abs((err[-1]-err[-2])/(err[1]-err[0]))
        if v < 10**(-5):
            break
    
    set_domain_params(dm_dm)
    dm_nfl = get_normalized_flux(dm_flux, dm_dm)
    dm_press, dm_polcur = get_pressure_polcurrent(dm_flux, dm_dm, dm_jt['param_p'], dm_jt['param_i2'])
    
    res = {
        'vessel': dm_vv,
        'flux': dm_flux,            # total flux
        'flux_coil': dm_fc,         # coil flux
        'flux_jt': dm_fp,           # jt flux
        'flux_normalized': dm_nfl,   # normalized flux
        'jt': dm_jt,                # jt
        'domain': dm_dm,            # domain
        'pressure': dm_press,        # plasma pressure
        'polcur': dm_polcur,        # poloidal current
        }    
    pl.d_contour(dm_flux)
    
    return res
    


    