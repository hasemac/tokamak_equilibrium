import numpy as np
import copy
import coils.cmat as cmat
import plasma.pmat as pmat
import vessel.vmat as vmat
import sub.emat as emat
from global_variables import gparam
from scipy.interpolate import interp1d
from scipy import constants as sc
import sub.plot as pl
import sub.sub_func as ssf
import sub.magnetics_cond as smc

# 正規化フラックスの計算
def get_normalized_flux(cond):
    dm_flux = cond["flux"]
    dm_domain = cond["domain"]
    # dm_flux: total flux (coil + plasma)
    # dm_domain: domain
    # return: dmat, normalized flux
    # 0: 磁気軸、1: 最外殻磁気面、0: 磁気面外
    res = emat.get_dmat_dim(dm_domain)
    faxis, fsurf = cond["f_axis"], cond["f_surf"]
    d = dm_domain["matrix"]
    f = dm_flux["matrix"]
    f = (f - faxis) / (fsurf - faxis)  # normalized flux
    f *= d  # domainの外にあるのはゼロにする。
    # 正規化フラックスは0(axis)-1(boundary)の間の数値
    # 0(axis)のf_axisは２次関数近似、近似がずれて、たまに負の値を出す。
    # というように必ず、0-1の範囲に収めるとする。
    f[f < 0] = 0.0 
    f[f > 1] = 1.0
    #print(f'fmax:{np.max(f)}, fmin:{np.min(f)}')
    res["matrix"] = f
    return res

def get_arr_diff(params, arr_norm_flux):
    """正規化フラックスからdp, またはdi2を算出

    Args:
        params (list[float]): 多項式の係数
        arr_norm_flux (array[float]): 正規化フラックスの1次元配列

    Returns:
        val (array[float]): 要素数は正規化フラックスの要素数に同じ
    """
    f = arr_norm_flux
    num = len(params)
    p0 = np.array([(f**i - f**num) for i in range(num)])
    p0 = p0.transpose()
    p0 = np.dot(p0, params)
    return p0

def get_arr(params, arr_norm_flux, cond):
    f = arr_norm_flux
    num = len(params)

    # 多項式の各項, n, p
    # an: x^n-x^p, これを積分すると次の式
    # an: x^(n+1)/(n+1)-x^(p+1)/(p+1), 1/(n+1)-1/(p+1) if x = 1
    # 例えば最外殻磁気面(x=1)ではプラズマ圧力がゼロとするならオフセットを各項に足す必要ある。つまり、
    # an: (x^(n+1)-1)/(n+1)-(x^(p+1)-1)/(p+1)

    # 積分した各項の行列
    p1 = np.array(
        [
            ((f ** (i + 1) - 1) / (i + 1) - (f ** (num + 1) - 1) / (num + 1))
            for i in range(num)
        ]
    )
    p1 = p1.transpose()
    p1 = np.dot(p1, params)
    
    # 積分の変数変換に伴う係数をかける。
    p1 *= (cond['f_surf']-cond['f_axis'])

    return p1        
        
# 規格化フラックスでの圧力の微分dP/dxと、圧力Pの計算
def get_dpress_press_normal(cond, num):
    params = cond['param_dp']
    f = np.linspace(0.0, 1.0, num)
    
    # 圧力の微分に関する行列
    p0 = get_arr_diff(params, f)
    
    # 圧力に関する行列
    p1 = get_arr(params, f, cond)
        
    return p0, p1

# 圧力の微分dP/dxと、圧力Pの計算
def get_dpress_press(cond):
    dm_normalizedflux = cond["flux_normalized"]
    dm_domain = cond["domain"]
    params = cond["param_dp"]    
    
    g = emat.dm_array(dm_domain)
    nr, nz = g.nr, g.nz

    f = dm_normalizedflux["matrix"].reshape(-1)
    d = dm_domain["matrix"].reshape(-1)

    # 最外殻磁気面の内部のみ取り出す
    ir = g.ir[d == 1]
    iz = g.iz[d == 1]
    f = f[d == 1]

    # 圧力の微分に関する行列
    p0 = get_arr_diff(params, f)
    
    m_dp = np.zeros((nz, nr))
    for v, i, j in zip(p0, ir, iz):
        m_dp[j, i] = v

    # 圧力に関する行列
    p1 = get_arr(params, f, cond)
        
    m_pr = np.zeros((nz, nr))
    for v, i, j in zip(p1, ir, iz):
        m_pr[j, i] = v

    # 圧力に関してはx=1でp=0になるようにしてある。
    dm_dp = emat.get_dmat_dim(dm_domain)
    dm_pr = emat.get_dmat_dim(dm_domain)
        
    dm_dp["matrix"] = m_dp
    dm_pr["matrix"] = m_pr

    return dm_dp, dm_pr

def get_di2total_itotal(cond, arr_norm_flux):

    f = arr_norm_flux
    
    # この時点で下のように調節することも考えられるが、
    # 調節した点で、やはり計算誤差が出やすい。
    # 従って、不定形di2/iを計算するときにのみ
    # 補正を入れたほうが良い
    #f = [e if e != 1.0 else 0.999 for e in arr_norm_flux]
    #f = np.array(f)
        
    params = cond['param_di2']
    
    # TFcoilによるポロイダル電流
    i0 = cond["cur_tf"]["tf"]*cond["cur_tf"]["turn"]
    
    # I^2の微分に関する行列
    di2 = get_arr_diff(params, f)
    
    # I^2に関する行列, トロイダルコイルによる成分も加算
    i2 = get_arr(params, f, cond) + i0**2
    
    # ここで正負の判定をする。
    #print('i2:', i2)
    # 場合によっては負の数を返すこともあるみたいなので、
    # その場所はゼロにする。
    i2[i2 < 0] = 0.0
    
    # I^2なのでIにする。
    i = np.sqrt(i2)

    # iは正負の任意性がある。
    # トロイダルコイル電流が負の場合は、x=1(最外殻磁気面）で
    # マイナスになるので、値を反転する。
    if i0 < 0:
        i *= -1.0
    
    return di2, i

# 規格化フラックス内でのポロイダルカレントの微分とポロイダルカレントの計算
def get_di2_i_norm(cond, num):
    """規格化フラックスでのdi2, iを返す。
    np.linspec(0.0, 1.0, num)の正規化フラックス
    x = 0.0 (axis) - 1.0 (boundary)

    Args:
        cond (dict): 平衡計算結果
        num (int): 返す個数

    Returns:
        array_float, array_float: dI^2/df_norm, I
    """

    f = np.linspace(0.0, 1.0, num)
    
    di2total, itotal = get_di2total_itotal(cond, f)

    return di2total, itotal
             
# ポロイダルカレントの微分dI^2/dxとポロイダルカレントの計算
def get_di2_i(cond):
    """di^2/dfとiのdmatを返す。

    Args:
        cond (dict): calculation result

    Returns:
        tuple of dmat: di2, i
    """
    dm_normalizedflux = cond["flux_normalized"]
    dm_domain = cond["domain"]
        
    g = emat.dm_array(dm_domain)
    nr, nz = g.nr, g.nz

    f = dm_normalizedflux["matrix"].reshape(-1)
    d = dm_domain["matrix"].reshape(-1)

    # 最外殻磁気面の内部のみ取り出す
    ir = g.ir[d == 1]
    iz = g.iz[d == 1]
    f = f[d == 1]

    di2total, itotal = get_di2total_itotal(cond, f)
    
    m_di2 = np.zeros((nz, nr))
    for v, i, j in zip(di2total, ir, iz):
        m_di2[j, i] = v
        
    m_i = np.zeros((nz, nr))
    for v, i, j in zip(itotal, ir, iz):
        m_i[j, i] = v
        
    # プラズマの存在しない領域のポロイダル電流を設定
    # これはTFコイル電流に依存する。
    m_i[m_i == 0] = cond["cur_tf"]["tf"]*cond["cur_tf"]["turn"]
    
    dm_di2 = emat.get_dmat_dim(dm_domain)
    dm_i = emat.get_dmat_dim(dm_domain)
     
    dm_di2["matrix"] = m_di2
    dm_i["matrix"] = m_i

    return dm_di2, dm_i

# flux値の極小位置の探索
def search_local_min(dm_flx, dm_vv):
    g = emat.dm_array(dm_flx)
    nr, nz = g.nr, g.nz

    fl, vv = dm_flx["matrix"], dm_vv["matrix"]

    ir, iz = int(nr / 2), int(nz / 2)

    while vv[iz, ir] == 1:  # 真空容器外になったら探索終了
        if fl[iz, ir] > fl[iz + 1, ir]:
            iz += 1
        elif fl[iz, ir] > fl[iz - 1, ir]:
            iz -= 1
        elif fl[iz, ir] > fl[iz, ir + 1]:
            ir += 1
        elif fl[iz, ir] > fl[iz, ir - 1]:
            ir -= 1
        else:
            break

    if vv[iz, ir] == 0:
        ir, iz = 0, 0

    return (ir, iz)

# 最外殻磁気面の探索(ip正負両方に対応)
def search_domain(cond):
    res = search_dom(cond)
    if None != res:
        return res

    # 極小値の探索に失敗しているのでfluxを反転させて再探索
    dm_flx = cond["flux"]
    dm_flx["matrix"] = -dm_flx["matrix"]
    # a = dm_flx['matrix']
    # dm_flx2 = get_dmat_dim(dm_flx)
    # dm_flx2['matrix'] = -a

    res = search_dom(cond)
    
    # 反転させたものを元に戻しておく。
    dm_flx["matrix"] = -dm_flx["matrix"]
    
    if None == res:
        # 反転させても探索失敗の場合
        cond['cal_result'] = -1
        cond['error_messages'] += 'Can not find domain.'
        return res
    
    # これも反転させておく。
    cond["f_axis"] = -cond["f_axis"]
    cond["f_surf"] = -cond["f_surf"]

    return res

# 最外殻磁気面の探索(最小値)
def search_dom(cond):
    # dm_flx: fluxのdmat
    # dm_vv: 真空容器のdmat
    dm_flx = cond["flux"]
    dm_vv = cond["vessel"]
    g = emat.dm_array(dm_flx)
    nz, nr = g.nz, g.nr
    dz, dr = g.dz, g.dr
    zmin, rmin = g.zmin, g.rmin

    # 返り値の作成
    res = emat.get_dmat_dim(dm_flx)

    # 領域の初期化
    dm = np.zeros((nz, nr))

    # 真空容器内の極小値を探索してシードとして追加
    k, l = search_local_min(dm_flx, dm_vv)
    if 0 == k and 0 == l:
        return None

    dm[l, k] = 1.0  # 探索用のシードを極小値を持つ場所にセット

    # 値を記録
    cond["ir_ax"] = k
    cond["iz_ax"] = l
    # 近傍9点のデータから極値の補正値を求める。
    zc, rc, fax = ssf.find_extremum_loc_and_val(dm_flx['matrix'][l-1:l+2, k-1:k+2]) # 補正
    cond["r_ax"] = rmin + k * dr + rc * dr
    cond["z_ax"] = zmin + l * dz + zc * dz
    cond['f_axis'] = fax

    # 磁気軸のフラックスを保存し、
    # 最外殻磁気面とヌル点フラックスの初期値を設定
    #fax = dm_flx["matrix"][l, k]
    fsurf = fax
    fnull = fax

    # 一次元配列を作成
    m0 = dm_flx["matrix"].reshape(-1)
    vv = dm_vv["matrix"].reshape(-1)
    ir = g.ir
    iz = g.iz

    # 小さい値順に並び替える
    ix = m0.argsort()
    m0, ir, iz, vv = m0[ix], ir[ix], iz[ix], vv[ix]

    # パディング
    dm2 = np.pad(dm, [(1, 1), (1, 1)])

    for f, i, j, v in zip(m0, ir, iz, vv):
        ni, nj = i + 1, j + 1  # paddingしているので、1を足す。
        a = dm2[nj - 1 : nj + 2, ni - 1 : ni + 2].reshape(-1)
        a = np.sum(a)  # 近接点にプラズマが存在していること。
        # 新しい点に対する判定
        con = a > 0  # 存在していれば1、その他はゼロ

        # 他のプラズマと接触して、かつ真空容器内
        # この場合、プラズマの存在領域として登録
        if con and 1 == v:
            dm2[nj, ni] = con
            continue

        # 他のプラズマと接触して且つ真空容器外なら探索終了
        # リミター配位、または
        # ダイバータ配位で探索中にレッグが真空容器に到達
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

    # パディング分を取り除く
    dm3 = dm2[1 : 1 + nz, 1 : 1 + nr]

    # ダイバータ配位かどうかの判定
    if fnull != fax:
        # ダイバータ配位の場合、ヌル点近傍でほとんどフラックスが変化しない。
        # ある値で切り上げたほうが多分良い。
        fsurf = fax + 0.90 * (fnull - fax)
        cond["conf_div"] = 1
    else:
        cond["conf_div"] = 0
        
    dm3[iz[m0 >= fsurf], ir[m0 >= fsurf]] = 0
    #print(f'fs:{fsurf}')

    res["matrix"] = dm3
    cond["f_surf"] = fsurf

    return res

# 体積平均の算出
def get_volume_average(dm_val, dm_domain):
    # dm_val: 例えばプラズマ圧力など
    g = emat.dm_array(dm_domain)
    dr, dz = g.dr, g.dz

    m = dm_domain["matrix"].reshape(-1)
    v = dm_val["matrix"].reshape(-1)

    # domain内のみ考える。
    r = g.r[m == 1]
    v = v[m == 1]

    vol = np.sum(2 * np.pi * r * dr * dz)  # plasma volume
    v = np.sum(2 * np.pi * r * dr * dz * v)  # vol*val
    return v / vol

# ポロイダル断面平均の算出
def get_cross_section_average(dm_val, dm_domain):
    g = emat.dm_array(dm_domain)
    dr, dz = g.dr, g.dz

    m = dm_domain["matrix"].reshape(-1)
    v = dm_val["matrix"].reshape(-1)

    # domain内のみ考える。
    v = v[m == 1]
    
    csec = np.sum(m[m == 1]) * dr * dz # cross section
    val = np.sum(dr * dz * v)
    
    return val/csec

# 最外殻磁気面形状
def set_domain_params(cond):
    d_mat = cond["domain"]
    g = emat.dm_array(d_mat)
    rmin, dr = g.rmin, g.dr
    zmin, dz = g.zmin, g.dz

    m = d_mat["matrix"].reshape(-1)
    ir = g.ir[m == 1]
    iz = g.iz[m == 1]
    r = g.r[m == 1]

    fl = cond['flux']['matrix']
    fsur = cond['f_surf']
    
    # ptsの辞書型での初期化
    cond["pts"] = {}
    
    # rminがある位置
    v = np.min(ir)
    #r_rmin = rmin + dr * np.mean(ir[ir == v])
    #z_rmin = zmin + dz * np.mean(iz[ir == v])
    kr = int(np.mean(ir[ir == v]))
    kz = int(np.mean(iz[ir == v]))
    p = ssf.find_points_of_quad_func(fl[kz-1:kz+2, kr-1:kr+2], fsur)
    i = np.argmin([r for z, r in p])
    cz, cr = p[i]
    r_rmin = rmin + dr * (kr+cr)
    z_rmin = zmin + dz * (kz+cz)
    cond["pts"]["r_rmin"] = r_rmin
    cond["pts"]["z_rmin"] = z_rmin

    
    # rmaxがある位置
    v = np.max(ir)
    #r_rmax = rmin + dr * np.mean(ir[ir == v])
    #z_rmax = zmin + dz * np.mean(iz[ir == v])
    kr = int(np.mean(ir[ir == v]))
    kz = int(np.mean(iz[ir == v]))
    p = ssf.find_points_of_quad_func(fl[kz-1:kz+2, kr-1:kr+2], fsur)
    i = np.argmax([r for z, r in p])
    cz, cr = p[i]
    r_rmax = rmin + dr * (kr+cr)
    z_rmax = zmin + dz * (kz+cz)
    cond["pts"]["r_rmax"] = r_rmax
    cond["pts"]["z_rmax"] = z_rmax

    # zminがある位置
    v = np.min(iz)
    #r_zmin = rmin + dr * np.mean(ir[iz == v])
    #z_zmin = zmin + dz * np.mean(iz[iz == v])
    kr = int(np.mean(ir[iz == v]))
    kz = int(np.mean(iz[iz == v]))
    p = ssf.find_points_of_quad_func(fl[kz-1:kz+2, kr-1:kr+2], fsur)
    i = np.argmin([z for z, r in p])
    cz, cr = p[i]
    r_zmin = rmin + dr * (kr+cr)
    z_zmin = zmin + dz * (kz+cz)
    cond["pts"]["r_zmin"] = r_zmin
    cond["pts"]["z_zmin"] = z_zmin

    # zmaxがある位置
    v = np.max(iz)
    #r_zmax = rmin + dr * np.mean(ir[iz == v])
    #z_zmax = zmin + dz * np.mean(iz[iz == v])
    kr = int(np.mean(ir[iz == v]))
    kz = int(np.mean(iz[iz == v]))
    p = ssf.find_points_of_quad_func(fl[kz-1:kz+2, kr-1:kr+2], fsur)
    i = np.argmax([z for z, r in p])
    cz, cr = p[i]
    r_zmax = rmin + dr * (kr+cr)
    z_zmax = zmin + dz * (kz+cz)
    cond["pts"]["r_zmax"] = r_zmax
    cond["pts"]["z_zmax"] = z_zmax

    a0 = (r_rmax - r_rmin) / 2.0
    r0 = (r_rmax + r_rmin) / 2.0
    cond["major_radius"] = r0
    cond["minor_radius"] = a0
    cond["elongation"] = (z_zmax - z_zmin) / (r_rmax - r_rmin)
    cond["triangularity"] = (r0 - r_zmax) / a0
    cond["volume"] = np.sum(2 * np.pi * r * dr * dz)
    cond["cross_section"] = np.sum(m[m == 1]) * dr * dz

# ベータ値の計算
def calc_beta(cond):
    u0 = sc.mu_0  # 真空の透磁率
    pi = sc.pi

    # 圧力の体積平均
    p = get_volume_average(cond["pressure"], cond["domain"])
    cond["pressure_vol_average"] = p

    # 磁気軸におけるプラズマ込みのトロイダル磁場
    ir_ax, iz_ax = cond["ir_ax"], cond["iz_ax"]
    r_ax = cond["r_ax"]
    # 2 pi R Bt = mu0 I
    polcur = cond["pol_current"]["matrix"][iz_ax, ir_ax]
    bt = u0 * polcur / (2 * pi * r_ax)

    # poloidal beta bp = (8 pi <p> S)/(u0 Ip^2)
    ip = cond["cur_ip"]["ip"] # ip
    s = cond["cross_section"] # cross section area
    a = np.sqrt(s/pi) # minor radius
    cond["beta_poloidal"] = (8*pi*p*s)/(u0*ip*ip)

    # toroidal beta bet_tor = <p>/(bt^2/(2u0))
    betr = p / (bt**2 / 2 / u0)
    cond["beta_toroidal"] = betr

    #  normalized beta
    ipma = ip/(10**6) # unit: MA
    betrper = betr*100 # unit: [%], percent
    betnor = np.abs(betrper*a*bt/ipma)
    cond["beta_normalized"] = betnor
    
    return cond

# safety factorの計算
def calc_safety(cond):
    # calc toroidal flux
    # ft = Integrate_area[u0*I/(2*pi*r)]
    g = emat.dm_array(cond["domain"])
    d = cond["domain"]["matrix"].reshape(-1)
    f = cond["flux_normalized"]["matrix"].reshape(-1)
    p = cond["pol_current"]["matrix"].reshape(-1)

    # domainの場所だけ取り出す。
    f = f[d == 1]
    p = p[d == 1]
    r = g.r[d == 1]
    ir = g.ir[d == 1]
    iz = g.iz[d == 1]
    nr, nz = g.nr, g.nz

    # bfの磁気面内の面積分を行う。
    # bf: トロイダル方向の磁束密度
    # 2 pi r bf = u0 I, thus bf = 2.0e-7 * I / r
    func = 2.0 * 10 ** (-7) * p / r
    func *= (g.dr*g.dz) # 面積積分なのでメッシュ面積をかける。

    x = np.linspace(0, 1, 11)
    y = [np.sum(func[f <= e]) for e in x]

    cond['toroidal_flux'] = y
    dy = np.diff(y)/(x[1]-x[0]) # 微分を計算
    dy = np.append(dy[0], dy) # 要素数を揃える。
    cond['toroidal_flux_diff'] = dy
    
    fnc = interp1d(x, dy, kind='cubic') 
    fax, fbn = cond["f_axis"], cond["f_surf"]
    #print(f'fmax:{max(f)}, fmin:{min(f)}, xmin:{x[0]}, xmax:{x[-1]}')
    q = fnc(f)/(fbn - fax)

    qmat = np.zeros((nz, nr))
    for v, i, j in zip(q, ir, iz):
        qmat[j, i] = v

    safety = copy.deepcopy(cond["resolution"])
    safety["matrix"] = qmat
    cond["safety_factor"] = safety

    # 正規化フラックスに応じた値の計算
    f0 = np.linspace(0.0, 1.0, nr)
    q0 = fnc(f0)/(fbn - fax)

    cond["safety_factor_norm"] = q0
    
    return cond

# 平衡計算の前処理
def equi_pre_process(condition, verbose=2):
    cond = copy.deepcopy(condition)
    cond['error_messages'] = ""
    cond["error"] = []
    cond["cal_result"] = 0
    cond["bad_step"] = 0
        
    # 真空容器
    dm_vv = vmat.get_vessel(cond)
    cond["vessel"] = dm_vv

    g = emat.dm_array(dm_vv)
    # ポロイダル電流
    dm = emat.get_dmat_dim(dm_vv)
    dm['matrix'] = np.ones((g.nz, g.nr))*cond["cur_tf"]["tf"]*cond["cur_tf"]["turn"]
    cond['pol_current'] = dm
    
    # コイルによるフラックス
    dm_fc = cmat.get_flux_of_coil(cond)
    cond["flux_coil"] = dm_fc

    # プラズマ電流
    dm_jt = pmat.d_set_plasma_parabolic(cond)
    cond["jt"] = dm_jt

    # プラズマ電流によるフラックス
    dm_fp = pmat.cal_plasma_flux(dm_jt)
    cond["flux_jt"] = dm_fp

    # トータルのフラックス
    dm_flux = emat.dm_add(dm_fp, dm_fc)
    cond["flux"] = dm_flux

    # 最外殻磁気面
    dm_dm = search_domain(cond)
    cond["domain"] = dm_dm

    # 領域の中心位置におけるコイルフラックスの値取得
    r = (cond["flux_coil"]["rmin"] + cond["flux_coil"]["rmax"]) / 2.0
    z = (cond["flux_coil"]["zmin"] + cond["flux_coil"]["zmax"]) / 2.0
    f = emat.linval2(r, z, cond["flux_coil"])
    ip = cond["cur_ip"]["ip"]
    # ipとfの積が正の場合は平衡が成り立たないので除外する。
    if 0 < f * ip:
        #cond["domain"] = None
        cond["cal_result"] = -1
        cond["error_messages"] += 'Invalid direction of plasma current.'

    if -1 == cond['cal_result'] and 1 <= verbose:
        print(cond['error_messages'])
    
    if 2 <= verbose:
        print('pre-process:')
        pl.d_contour(cond['flux'])
        
    return cond

# 平衡計算の後処理
def equi_post_process(cond, verbose=2):
    
    g = emat.dm_array(cond['domain'])
    
    # 形状パラメータの計算（elongationなど）
    set_domain_params(cond)

    # 正規化フラックスの計算
    dm_nfl = get_normalized_flux(cond)
    cond["flux_normalized"] = dm_nfl

    # fluxループの位置におけるフラックスの計算    
    if 'fl_pos' in cond.keys():
        pos = cond['fl_pos']
        cond['fl_val'] = {}
        for k in pos.keys():
            r, z = pos[k]
            cond['fl_val'][k] = emat.linval2(r, z, cond['flux'])
    
    # 与えられた位置におけるBrの計算
    if 'br_pos' in cond.keys():
        mag = smc.Magnetic(cond)
        cond['br'] = mag.br
        pos = cond['br_pos']
        cond['br_val'] = {}
        for k in pos.keys():
            r, z = pos[k]
            cond['br_val'][k] = emat.linval2(r, z, cond['br'])
    
    # 与えられた位置におけるBzの計算
    if 'bz_pos' in cond.keys():
        mag = smc.Magnetic(cond)
        cond['bz'] = mag.bz
        pos = cond['bz_pos']
        cond['bz_val'] = {}
        for k in pos.keys():
            r, z = pos[k]
            cond['bz_val'][k] = emat.linval2(r, z, cond['bz'])
            
    # 圧力微分dp/dfと圧力pの計算
    dm_dp, dm_pr = get_dpress_press(cond)
    cond["diff_pre"] = dm_dp
    cond["pressure"] = dm_pr
    
    # 規格化フラックスでの圧力微分dp/dfと圧力pの計算
    dp, pr = get_dpress_press_normal(cond, g.nr)
    cond['diff_pre_norm'] = dp
    cond['pressure_norm'] = pr

    # ポロイダル電流微分di^2/dfとポロイダル電流の計算
    dm_di2, dm_polcur = get_di2_i(cond)
    cond["diff_i2"] = dm_di2
    cond["pol_current"] = dm_polcur
    
    # 規格化フラックスでの電流微分di^2/dfとポロイダル電流の計算
    di2, polcur = get_di2_i_norm(cond, g.nr)
    cond['diff_i2_norm'] = di2
    cond['pol_current_norm'] = polcur

    cond = calc_beta(cond)  # ベータ値の計算
    cond = calc_safety(cond)  # safety factorの計算

    # 計算結果の確認
    # 圧力分布の正負の確認
    a = [e <0 for e in cond["pressure_norm"]]
    if any(a):
        cond["cal_result"] = -1
        cond['error_messages'] += "Negtive pressure found.\n"
    
    # 正常終了の場合
    if cond["cal_result"] != -1:
        cond["cal_result"] = +1

    if -1 == cond["cal_result"]:
        if 1 <= verbose:
            print(cond['error_messages'])
            
    if 2 <= verbose:
        print('post-process:')
        pl.d_contour(cond['flux'])
        
    return cond

# 平衡計算(１回)
def equi_fit_and_evaluate_error(condition):
    cond = copy.deepcopy(condition)
    
    dm_jt = cond["jt"]
    dm_domain = cond["domain"]
    npr = cond["num_dpr"]
    ncu = cond["num_di2"]

    # dm_jt: プラズマ電流
    # dm_domain: 最外殻磁気面のdmat
    # npr: pressureに関するパラメータの個数
    # ncu: poloidal電流に関するパラメータの個数
    #
    # out: dmat_jt

    g = emat.dm_array(dm_domain)

    # 1メッシュの面積を計算
    ds = g.dr*g.dz
    
    # fluxの正規化
    dm_nf = get_normalized_flux(cond)
    f = dm_nf["matrix"].reshape(-1)
    j = dm_jt["matrix"].reshape(-1)
    jtotal = np.sum(j)  # 全電流を保持しておく

    d = dm_domain["matrix"].reshape(-1)

    # 最外殻磁気面の内部のみ取り出す。
    ir = g.ir[d == 1]
    iz = g.iz[d == 1]
    r = g.r[d == 1]
    j = j[d == 1]
    f = f[d == 1]

    # 例えばパラメータ数が３の場合の時
    # (1-x^3) *a0 + (x^1-x^3)*a1 + (x^2-x^3)*a2
    # という形になることに注意すること

    # 圧力に関する行列作成
    p0 = np.array([2 * np.pi * r * (f**i - f**npr) for i in range(npr)])
    # I^2に関する行列作成
    p1 = np.array(
        [10 ** (-7) / (r + 10 ** (-7)) * (f**i - f**ncu) for i in range(ncu)]
    )
    
    # 結合させて転置、この時点で[point数, パラメータ数]の形
    a = np.vstack([p0, p1]).transpose()
    
    # 次にAbs(a x -j)を最小とするxを求めればよい。
    # A[p, n] x[n] = j[p]
    # このときのxは、At.A x = At.jを満たすxである。

    # フィッティングする場合は電流密度の値を用いる。
    m0 = np.dot(a.transpose(), a)
    #m1 = np.dot(a.transpose(), j/ds)
    m1 = np.dot(a.transpose(), j) # jtを電流密度とする場合

    # m0にほんのわずかな値を加算してsingular matrixになるのを避ける
    # dd = np.min(np.abs(m0))*10**(-7)
    # m0 += np.identity(npr+ncu)*dd

    # もしsingular matrixになったらそこで計算終了
    if np.linalg.det(m0) == 0:
        cond['cal_result'] = -1
        cond['error_messages'] += 'Singular matrix occurs.\n'
        return cond
    params = np.dot(np.linalg.inv(m0), m1)

    # エラー値の算出
    j0 = np.dot(a, params)  # 新しい電流
    jsum = np.sum(j0)
    j0 *= jtotal / jsum  # トータルの電流値が維持されるように調整
    # この時点で、１メッシュ内に流れるトータルの電流に正規化される。

    # 評価方法はいくつか考えられる。単位メッシュ当たりのエラーに直すとか。    
    # これは単純な二乗残差、domainが大きい場合はエラーが大きくなる？
    #errest = np.sum((j0 - j) ** 2) / 2
    # 二乗残差の平均(メッシュ当たりのエラー)、domainの大きさに依存しない
    # errest = np.average((j0 - j) ** 2) / 2
    # メッシュ当たりのパーセンテージ絶対誤差の平均のようなもの 
    #errest = np.average(np.abs(j0-j))/np.average(np.abs(j))
    # メッシュの絶対誤差の最大値とメッシュの平均値の比
    errest = np.max(np.abs(j0-j))/np.average(np.abs(j))
    
    # 新しい電流分布の作成
    j_new = np.zeros((g.nz, g.nr))
    for i, j, v in zip(ir, iz, j0):
        j_new[j, i] = v
    res = emat.get_dmat_dim(dm_jt)
    res["matrix"] = j_new
    cond['jt'] = res
    
    # 新しい圧力由来電流分布の作成
    j0_p = np.dot(a[:, 0:npr], params[0:npr])
    j_pres = np.zeros((g.nz, g.nr))
    for i, j, v in zip(ir, iz, j0_p):
        j_pres[j, i] = v
    res = emat.get_dmat_dim(dm_jt)
    res['matrix'] = j_pres * jtotal / jsum
    cond['jt_dp'] = res

    # 新しいポロイダル電流由来電流分布の作成
    j0_d = np.dot(a[:, npr:], params[npr:])
    j_di2 = np.zeros((g.nz, g.nr))
    for i, j, v in zip(ir, iz, j0_d):
        j_di2[j, i] = v
    res = emat.get_dmat_dim(dm_jt)
    res['matrix'] = j_di2 * jtotal / jsum
    cond['jt_di2'] = res
    
    cond["error"].append(errest)
    cond["param_dp"] = params[0:npr]
    cond["param_di2"] = params[npr:]
    
    return cond

def equi_calc_one_step(condition, verbose=2):
    cond = copy.deepcopy(condition)

    # プラズマ平衡
    cond = equi_fit_and_evaluate_error(cond)
    if -1 == cond['cal_result']:
        if 1 <= verbose:
            print(cond['error_messages'])
        return cond
    
    # プラズマ電流のトリミング
    # ip>0なら全ての領域でjt>0となるようにする。
    dm_jt2 = pmat.trim_plasma_current(cond)
    cond["jt"] = dm_jt2

    # 磁気軸位置をプラズマ初期位置に一致させる。
    if ('fix_pos' in cond) and cond['fix_pos']:
        dm_jt = pmat.shift_plasma_profile(cond)
        cond["jt"] = dm_jt
    
    # プラズマ電流によるフラックス
    dm_fp = pmat.cal_plasma_flux(cond["jt"])
    cond["flux_jt"] = dm_fp

    # トータルのフラックス
    dm_flux = emat.dm_add(cond["flux_jt"], cond["flux_coil"])
    cond["flux"] = dm_flux

    # 最外殻磁気面の探索
    dm_dm = search_domain(cond)
    cond["domain"] = dm_dm
    if -1 == cond['cal_result']:
        if 1 <= verbose:
            print(cond['error_messages'])
        return cond

    # エラー値を記録
    err = cond["error"]
    cond["iter"] = len(err)
    # 前回よりエラーが増えていたらbat_stepを+1
    if (len(err) >= 2) and (err[-1] > err[-2]):
        cond['bad_step'] += 1
        
    if 1 <= verbose:
        print(f'{len(err)} loss: {err[-1]:.3e}')
    if 2 <= verbose:
        pl.d_contour(cond['flux'])
        
    return cond
              
# 平衡計算
def calc_equilibrium(condition, iteration=100, verbose=1):
    # iteration: イタレーション数。
    #   指定があった場合は、最後までイタレーションする。
    # verbose: 1:詳細表示, 0:なし

    cond = copy.deepcopy(condition)
    cond = equi_pre_process(cond, verbose=verbose)
    if cond["cal_result"] == -1:
        return cond

    for i in range(iteration):
        
        cond = equi_calc_one_step(cond, verbose=verbose)
        if cond["cal_result"] == -1:
            return cond
    
        # 少なくとも２回は計算を行う。
        err = cond["error"]
        if len(err) <= 2:
            continue
        
        # iterationがデフォルト値でない場合は、設定されたという事。
        # このときは、最後までiterationする。
        if iteration < 100:
            continue

        # 2回連続して、前回値よりエラー値が大きくなったら終了
        # その時の配位がリミター配位なら収束しなかったとみなす。
        #if (err[-1] > err[-2]) and (err[-2] > err[-3]):
        #    if 0 == cond["conf_div"]:
        #        cond['error_messages'] += 'Error value increased in limiter configuration.\n'
        #        cond['cal_result'] = -1
        #    break

        # エラー値が悪くなった回数が規定に達したら、収束せず振動しているとみなす。
        if cond['bad_step'] > 4:
            cond["error_messages"] += "Calculation doesn't converge.\n"
            cond["cal_result"] = -1
            break
        
        # 一番最初の変化量に対して、最新の変化量が十分小さければ終了
        #v = np.abs((err[-1] - err[-2]) / (err[1] - err[0]))
        #if v < 10 ** (-5):
        #    break
    
        # error値が、ある値より小さくなったら終了
        if err[-1] < 0.05:
            break
        
    cond = equi_post_process(cond, verbose=verbose+1)

    return cond
