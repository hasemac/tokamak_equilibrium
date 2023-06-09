import numpy as np
import copy
import plasma.pmat as pmat
import plasma.pmat_br as pmat_br
import plasma.pmat_bz as pmat_bz
import vessel.vmat as vmat
import sub.emat as emat
from global_variables import gparam
from scipy.interpolate import interp1d
from scipy import constants as sc
import sub.plot as pl
import sub.sub_func as ssf
import sub.magnetics_cond as smc

gl = gparam()

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
    cond["axis_ir"] = k
    cond["axis_iz"] = l
    # 近傍9点のデータから極値の補正値を求める。
    zc, rc, fax = ssf.find_extremum_loc_and_val(dm_flx['matrix'][l-1:l+2, k-1:k+2]) # 補正
    cond["axis_r"] = rmin + k * dr + rc * dr
    cond["axis_z"] = zmin + l * dz + zc * dz
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
    cond["aspect_ratio"] = r0/a0
    cond["elongation"] = (z_zmax - z_zmin) / (r_rmax - r_rmin)
    cond["triangularity"] = (r0 - r_zmax) / a0
    cond["volume"] = np.sum(2 * np.pi * r * dr * dz)
    cond["cross_section"] = np.sum(m[m == 1]) * dr * dz

# ベータ値の計算
def calc_beta(cond):
    u0 = sc.mu_0  # 真空の透磁率
    pi = sc.pi

    # 圧力の体積平均
    pv = get_volume_average(cond["pressure"], cond["domain"])
    cond["pressure_average_volume"] = pv
    # factor *2 means ion and electro
    cond["stored_energy"] = (3/2)*pv*cond["volume"]*2
    
    # 圧力の面積平均
    ps = get_cross_section_average(cond["pressure"], cond["domain"])
    cond["pressure_average_section"] = ps
    
    # 磁気軸におけるトロイダル磁場
    # 2 pi R Bt = mu0 I
    ir_ax, iz_ax = cond["axis_ir"], cond["axis_iz"]
    r_ax = cond["axis_r"]
    # プラズマ無しのトロイダル磁場
    bt0 = u0 * cond["cur_tf"]['tf']*cond["cur_tf"]["turn"]
    bt0 /= (2 * pi * r_ax)
    # プラズマ込みのトロイダル磁場
    polcur = cond["pol_current"]["matrix"][iz_ax, ir_ax]
    bt = u0 * polcur / (2 * pi * r_ax)

    # poloidal beta bp = (8 pi <p> S)/(u0 Ip^2)
    ip = cond["cur_ip"]["ip"] # ip
    s = cond["cross_section"] # cross section area
    a = np.sqrt(s/pi) # minor radius
    cond["beta_poloidal"] = (8*pi*ps*s)/(u0*ip*ip) # ps: section average

    # toroidal beta bet_tor = <p>/(bt0^2/(2u0))
    betr = pv / (bt**2 / 2 / u0) # pv: volume average
    cond["beta_toroidal"] = betr

    #  normalized beta
    ipma = ip/(10**6) # unit: MA
    betrper = betr*100 # unit: [%], percent
    betnor = np.abs(betrper*a*bt/ipma) # bt: toroidal with plasma
    cond["beta_normalized"] = betnor
    
    return cond

# インダクタンスの計算
def calc_inductance(cond):
    g = emat.dm_array(cond["domain"])
    d = cond["domain"]["matrix"].reshape(-1)
    br = cond['br_jt']["matrix"].reshape(-1)
    bz = cond['bz_jt']["matrix"].reshape(-1)
    
    # domainの場所だけ取り出す。
    br = br[d == 1]
    bz = bz[d == 1]
    ir = g.ir[d == 1]
    iz = g.iz[d == 1]
    nr, nz = g.nr, g.nz
        
    bt2 = br*br + bz*bz
    bt2mat = np.zeros((nz, nr))
    for v, i, j in zip(bt2, ir, iz):
        bt2mat[j, i] = v
        
    bt2jt = copy.deepcopy(gl.get_dmat_coarse())
    bt2jt["matrix"] = bt2mat
    cond["b_theta_jt_square"] = bt2jt
    
    #print('volume average', get_volume_average(bt2jt, cond['domain']))
    #print('section average', get_cross_section_average(bt2jt, cond['domain']))

    # normalized internal inductance
    # vn: <b_theta_square>_(section_average)
    # vd: b_theta(a)^2    
    vn = get_cross_section_average(bt2jt, cond['domain'])
    vd = (4.0*np.pi*10**(-7)*cond['cur_ip']['ip'])**2/(4*np.pi*cond['cross_section'])
    cond['inductance_internal_normalized'] = vn/vd
    
    # フラックスを算出。プラズマ由来であることに注意
    pr, pz = cond['pts']['r_rmin'], cond['pts']['z_rmin']
    fxe = np.abs(emat.linval2(pr, pz, cond['flux_jt'])) # 最外殻磁気面におけるフラックス
    # ピーク位置のフラックス。磁気軸位置とは一致しないことに注意。
    fxt = np.max(np.abs(cond['flux_jt']['matrix'])) # プラズマが存在することによる全磁束 
    fxi = fxt - fxe # プラズマ内部に存在するフラックス
    ip = cond['cur_ip']['ip']

    cond['inductance_internal'] = fxi/ip
    cond['inductance_self'] = fxt/ip
    
    vn = get_volume_average(bt2jt, cond['domain'])*cond['volume']
    vd = (4.0*np.pi*10**(-7))*(cond['cur_ip']['ip']**2)
    cond['inductance_internal_btheta'] = vn/vd
    
    return cond

# safety factorの計算（多項式近似その１）
def calc_safety_poly(cond):
    # トロイダルフラックスをポロイダル電流から計算
    # トロイダルフラックスを多項式で近似
    # その多項式関数の微分をとって安全係数を算出
    
    # この方法は微分を取った後の関数が中心ピークでなかったりするのが問題
    
    poly = 3 # 近似する多項式の次数

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
    
    coef = np.polyfit(x, y, poly) # [3次の係数, 2次係数, 1次係数, 0次係数]
    val = [poly-e for e in range(poly+1)] # [3, 2, 1, 0]
    coef *= val
    coef = coef[:-1] # 多項式関数を微分した係数
    
    cond['toroidal_flux_diff'] = np.poly1d(coef)(x)
    
    # 安全係数(分布)の計算
    fax, fbn = cond["f_axis"], cond["f_surf"]
    q = np.poly1d(coef)(f)/(fbn - fax)
    
    qmat = np.zeros((nz, nr))
    for v, i, j in zip(q, ir, iz):
        qmat[j, i] = v
        
    safety = copy.deepcopy(gl.get_dmat_coarse())
    safety["matrix"] = qmat
    cond["safety_factor"] = safety        
    
    # 安全係数（正規化フラックス）の計算
    f0 = np.linspace(0.0, 1.0, nr)
    q0 = np.poly1d(coef)(f0)/(fbn - fax)

    cond["safety_factor_norm"] = q0
    
    return cond    

# safety factorの計算（多項式近似その２）
def calc_safety_poly2(cond):
    # トロイダルフラックスをポロイダル電流から計算
    # その微分を計算
    # その微分値に対して多項式近似を行う。
    
    poly = 4 # 多項式の次数
    num = 61 # 微分を算出するときのサンプリング数

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

    x = np.linspace(0, 1, num)
    y = [np.sum(func[f <= e]) for e in x]

    cond['toroidal_flux'] = y
    dy = np.diff(y)/(x[1]-x[0]) # 微分を計算
    dy = np.append(dy[0], dy) # 要素数を揃える。
    cond['toroidal_flux_diff'] = dy    
    
    # 微分した値に関する多項式近似
    coef = np.polyfit(x, dy, poly) # [3次の係数, 2次係数, 1次係数, 0次係数]

    # 安全係数(分布)の計算
    fax, fbn = cond["f_axis"], cond["f_surf"]
    q = np.poly1d(coef)(f)/(fbn - fax)
    
    qmat = np.zeros((nz, nr))
    for v, i, j in zip(q, ir, iz):
        qmat[j, i] = v
        
    safety = copy.deepcopy(gl.get_dmat_coarse())
    safety["matrix"] = qmat
    cond["safety_factor"] = safety        
    
    # 安全係数（正規化フラックス）の計算
    f0 = np.linspace(0.0, 1.0, nr)
    q0 = np.poly1d(coef)(f0)/(fbn - fax)

    cond["safety_factor_norm"] = q0
    
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

    safety = copy.deepcopy(gl.get_dmat_coarse())
    safety["matrix"] = qmat
    cond["safety_factor"] = safety

    # 正規化フラックスに応じた値の計算
    f0 = np.linspace(0.0, 1.0, nr)
    q0 = fnc(f0)/(fbn - fax)

    cond["safety_factor_norm"] = q0
    
    return cond

# 束縛条件_圧力
def constraints_pressure(cond, const_pressure):
    faxis, fsurf = cond["f_axis"], cond["f_surf"]
    npr = cond["num_dpr"]
    ncu = cond["num_di2"]
    dm_nf = cond['flux_normalized']
    dm_domain = cond['domain']

    array_cf = [] # array of coef
    array_pr = [] # array of pressure
    array_wt = [] # array of weighting factor

    copr = const_pressure
    for e in copr.keys():
        rp,zp = copr[e]['point']
        
        # domainの外は無視
        if 0 == emat.linval2(rp, zp, dm_domain):
            continue

        # pointにおけるnormalized flux
        nfp = emat.linval2(rp, zp, dm_nf) 
        # onp[npr]の形
        onp = [(fsurf-faxis)*((nfp**(i+1)-1)/(i+1) - (nfp**(npr+1)-1)/(npr+1)) for i in range(npr)]
        onp += [0]*ncu # onp[npr + ncu] :パラメータの数

        array_cf.append(onp)
        array_pr.append(copr[e]['pressure'])
        array_wt.append(copr[e]['weight']**2) # squared
    
    # np arrayに変換。この時点で、[point数、パラメータ数]
    array_cf = np.array(array_cf)
    array_pr = np.array(array_pr)
    array_wt = np.array(array_wt)
    #print('cf', array_cf.shape, array_pr.shape, array_wt.shape)
    #print(array_wt)

    return array_cf, array_pr, array_wt

# 束縛条件_flux, br, bz
def constraints_mag(cond, arr_f, syurui, constraints):
    #arr_f[num of plasma points, num of fitting param]
    # syurui: 'flux', 'br', 'bz'

    cofl = constraints
    # 最初に種類に応じて変数をセット
    if syurui == 'flux':
        d_mat = cond['flux_coil']
        basemat = pmat
    elif syurui == 'br':
        d_mat = cond['br_coil']
        basemat = pmat_br
    elif syurui == 'bz':
        d_mat = cond['bz_coil']
        basemat = pmat_bz

    dm_domain = cond['domain']
    d = dm_domain['matrix'].reshape(-1)

    g = emat.dm_array(dm_domain)
    ir = g.ir[d == 1]
    iz = g.iz[d == 1]
    ds = g.dr * g.dz # メッシュ面積

    arr = []
    val = []
    wgt = []
    for e in cofl.keys():
        rf, zf = cofl[e]['point']
        # コイル由来の値
        fxc = emat.linval2(rf, zf, d_mat)
        #print('fxc', fxc)
        # 拘束条件位置のメッシュ番号
        nrf, nzf = emat.coarse_grid_num(rf, zf)
        hmat = [
            basemat.cget(nzp, nrp)[nzf, nrf] for nrp, nzp in zip(ir, iz)
        ]
        # jは電流密度を想定しているのに対して、pmat.cgetは単位電流
        # 電流密度に変更するためにdsをかけておく必要がある。
        hmat = np.array(hmat)
        hmat = np.diag(hmat)
        b = np.sum(np.dot(hmat, arr_f), axis=0)
        arr.append(b)
        val.append(cofl[e][syurui]-fxc) # コイル由来の値は除いておくこと
        
        wgt.append(cofl[e]['weight']**2) # squared
    arr = np.array(arr)*ds
    val = np.array(val)
    wgt = np.array(wgt)
    #print('arr', arr)
    #print(arr.shape, val.shape, wgt.shape)
    return arr, val, wgt

# フィッティング係数を求めるためのプラズマ電流密度のマトリックスを作成
def make_initial_matrix(cond):

    # 下の式の、Fとj0を作成する。
    # j1 = F c
    # j0

    # 各matrixの取得
    dm_jt = cond["jt"]
    dm_nf = cond["flux_normalized"]
    dm_domain = cond["domain"]

    # 時数の取得
    npr = cond["num_dpr"]
    ncu = cond["num_di2"]

    g = emat.dm_array(dm_domain)

    # 一次元化
    f = dm_nf["matrix"].reshape(-1)
    j = dm_jt["matrix"].reshape(-1)
    d = dm_domain["matrix"].reshape(-1)

    # 最外殻磁気面の内部のみ取り出す。
    r = g.r[d == 1]
    j = j[d == 1]
    f = f[d == 1]

    # 例えばパラメータ数が３の場合の時
    # (1-x^3) *a0 + (x^1-x^3)*a1 + (x^2-x^3)*a2
    # という形になることに注意すること

    # 圧力に関する行列作成 [npr+1, ポイント数]
    # 圧力由来のjt = 2*pi*r * (dp/df)
    p0 = np.array([2 * np.pi * r * (f**i - f**npr) for i in range(npr)])
    
    # I^2に関する行列作成 [ncu+1, ポイント数]
    # ポロイダル電流由来: jt = 10**(-7)/r * (di^2/df)
    p1 = np.array(
        [10 ** (-7) / (r + 10 ** (-7)) * (f**i - f**ncu) for i in range(ncu)]
    )
    
    # 結合させて転置、この時点で[point数, パラメータ数]の形
    a = np.vstack([p0, p1]).transpose() # matrix

    return a, j    

# 束縛条件のマトリックスをオリジナルにスタックしていく
def const_stack_matrix(mat0, val0, wgt0, mat1, val1, wgt1, j0):
    # mat0, val0, wgt0: original
    # mat1, val1, wgt1: additional_constraints
    # trimming weight with j0 (initial plasma current)

    j0_ave = np.average(np.abs(j0))
    num = len(j0)
    val1_ave = np.average(np.abs(val1))
    
    if 0.0 == val1_ave:
        val1_ave = 1.0
    
    tw = (j0_ave/val1_ave)**2 # trimming factor for weight_squared
    wgt1 *= tw # 値が同等になるためのweightの補正
    wgt1 *= num # j0は式の数が多いので、式の数に対する補正

    a1 = np.vstack((mat0, mat1)) 
    v1 = np.append(val0, val1)
    w1 = np.append(wgt0, wgt1)
    
    return a1, v1, w1

def constraints_procedure(cond, mat0, val0, wgt0, mat_jt, jt):
    # mat_jt : matrix derived from only jt. [num of plasma points, num of coefs]
    # jt : jt
    a1 = copy.copy(mat0)
    v1 = copy.copy(val0)
    w1 = copy.copy(wgt0)

    if 'constraints' not in cond.keys():
        return a1, v1, w1
    
    # constraintsを種類ごとに分ける
    const_pressure  = {}
    const_flux      = {}
    const_br        = {}
    const_bz        = {}
    
    dic = cond['constraints']
    for e in dic.keys():
        if 'pressure' in dic[e].keys():
            const_pressure[e] = dic[e]
        if 'flux' in dic[e].keys():
            const_flux[e] = dic[e]
        if 'br' in dic[e].keys():
            const_br[e] = dic[e]
        if 'bz' in dic[e].keys():
            const_bz[e] = dic[e]
    
    # 束縛条件が存在していれば、それをスタック
    if len(const_pressure) != 0:
        mat, val, wgt = constraints_pressure(cond, const_pressure)
        a1, v1, w1 = const_stack_matrix(a1, v1, w1, mat, val, wgt, jt)        
    
    if len(const_flux) != 0:
        mat, val, wgt = constraints_mag(cond, mat_jt, 'flux', const_flux)
        a1, v1, w1 = const_stack_matrix(a1, v1, w1, mat, val, wgt, jt)        

    if len(const_br) != 0:
        mat, val, wgt = constraints_mag(cond, mat_jt, 'br', const_br)
        a1, v1, w1 = const_stack_matrix(a1, v1, w1, mat, val, wgt, jt) 
        
    if len(const_bz) != 0:
        mat, val, wgt = constraints_mag(cond, mat_jt, 'bz', const_bz)
        a1, v1, w1 = const_stack_matrix(a1, v1, w1, mat, val, wgt, jt) 
    
    return a1, v1, w1

# 1次元配列をd_matに変換
def conv_1d_array_to_dmat(cond, array):
    dm_domain = cond['domain']
    g = emat.dm_array(dm_domain)
    d = dm_domain["matrix"].reshape(-1)
    ir = g.ir[d == 1]
    iz = g.iz[d == 1]

    mat = np.zeros((g.nz, g.nr))
    for i, j, v in zip(ir, iz, array):
        mat[j, i] = v
    res = emat.get_dmat_dim(dm_domain)
    res['matrix'] = mat
    return res

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
    
    # TFコイル巻き戻しのチェック
    cond = ssf.check_tf_rewind(cond)
    
    # プラズマ電流
    cond["jt"] = pmat.d_set_plasma_parabolic(cond)

    # 磁場クラスの作成
    mag = smc.Magnetic(cond)

    # コイルによるフラックス, br, bz
    cond["flux_coil"] = mag.fl_c
    cond["br_coil"] = mag.br_c
    cond["bz_coil"] = mag.bz_c

    # プラズマ電流によるフラックス,br, bz
    cond["flux_jt"] = mag.fl_p
    cond["br_jt"] = mag.br_p
    cond["bz_jt"] = mag.bz_p

    # トータルのフラックス, br, bz
    cond["flux"] = mag.fl
    cond["br"] = mag.br
    cond["bz"] = mag.bz

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
    # 最期、ドメインの探索をして終わっているので、
    # まれにドメインと実際がずれているときがある。
    # 従って、再度normalized_fluxを計算する必要がある。
    dm_nfl = get_normalized_flux(cond)
    cond["flux_normalized"] = dm_nfl

    # 磁場に関する計算
    mag = smc.Magnetic(cond)

    cond['br'] = mag.br
    cond['bz'] = mag.bz

    # fluxループの位置におけるフラックスの計算    
    if 'fl_pos' in cond.keys():
        pos = cond['fl_pos']
        cond['fl_val'] = {}
        for k in pos.keys():
            r, z = pos[k]
            cond['fl_val'][k] = mag.get_fl(r, z)
    
    # 与えられた位置におけるBrの計算
    if 'br_pos' in cond.keys():
        pos = cond['br_pos']
        cond['br_val'] = {}
        for k in pos.keys():
            r, z = pos[k]
            cond['br_val'][k] = mag.get_br(r, z)
    
    # 与えられた位置におけるBzの計算
    if 'bz_pos' in cond.keys():
        pos = cond['bz_pos']
        cond['bz_val'] = {}
        for k in pos.keys():
            r, z = pos[k]
            cond['bz_val'][k] = mag.get_bz(r, z)
    
    # decay index on magnetic acis
    cond['decay_index_on_axis'] = mag.get_decay_index(cond['axis_r'], cond['axis_z'])
            
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
    
    # safety factorの計算
    #cond = calc_safety(cond)  # 微分を取って補間
    #cond = calc_safety_poly(cond)  # 多項式近似した後に微分
    cond = calc_safety_poly2(cond)  # 微分後に多項式近似
    cond['q_center'] = cond['safety_factor_norm'][0]
    cond['q_edge'] = cond['safety_factor_norm'][-1]
    
    # inductanceの計算
    cond = calc_inductance(cond)
    
    # 拘束条件の再現度
    if 'constraints' in cond.keys():
        dic = cond['constraints']
        for e in dic.keys():
            rp, zp = dic[e]['point']
            if 'pressure' in dic[e].keys():
                dic[e]['pressure_calc'] = emat.linval2(rp, zp, cond['pressure'])
            if 'flux' in dic[e].keys():
                dic[e]['flux_calc'] = emat.linval2(rp, zp, cond['flux'])
            if 'br' in dic[e].keys():
                dic[e]['br_calc'] = emat.linval2(rp, zp, cond['br'])
            if 'bz' in dic[e].keys():
                dic[e]['bz_calc'] = emat.linval2(rp, zp, cond['bz'])                            

            
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
        #pl.d_contour(cond['flux'])
        pl.double_contour(cond['jt'], cond['flux'])
        
    return cond

# 平衡計算(１回)
def equi_fit_and_evaluate_error(condition):
    cond = copy.deepcopy(condition)
    
    # 正規化フラックスの作成と保存
    dm_nf = get_normalized_flux(cond) # 正規化flux
    cond["flux_normalized"] = dm_nf
    # 1メッシュの面積を計算
    #ds = g.dr*g.dz

    # make_initial_matrix returns: 
    # a[num of plasma points, num of coef]
    # j[num of plasma points]
    a, j = make_initial_matrix(cond) 
    jtotal = np.sum(j)  # 全電流を保持しておく

    # a1, v1, w1: including other constrains (ex. pressure)
    a1 = a.copy()
    v1 = j.copy() # value v[point数]
    w1 = np.array([1.0]*len(v1)) # weighting factor w[point数]

    # 束縛条件の追加
    a1, v1, w1 = constraints_procedure(cond, a1, v1, w1, a, j)

    w1 = np.diag(w1) # weighting matrixの作成

    # 重み付きの式の時、下の式を満たすcを求めればよい。
    # A_t W A c = (W A)_t v0 
    # A[nt, nc] (nt:ポイント数、nc:パラメータ数)
    # w[nt, nt]
    # v[nt]
    # フィッティングする場合は電流密度の値を用いる。
    m0 = np.dot(a1.transpose(), w1) # [np, nc]
    m0 = np.dot(m0, a1) # [np, np]
    #m1 = np.dot(a.transpose(), j/ds)
    m1 = np.dot(w1, a1).transpose() # [np, nc]
    m1 = np.dot(m1, v1) # jtを電流密度とする場合 [np]

    # m0にほんのわずかな値を加算してsingular matrixになるのを避ける
    # dd = np.min(np.abs(m0))*10**(-7)
    # m0 += np.identity(npr+ncu)*dd

    # もしsingular matrixになったらそこで計算終了
    if np.linalg.det(m0) == 0:
        cond['cal_result'] = -1
        cond['error_messages'] += 'Singular matrix occurs.\n'
        return cond
    params = np.dot(np.linalg.inv(m0), m1)

    j0 = np.dot(a, params)  # 新しい電流
    jsum = np.sum(j0)
    
    if jsum == 0.0:
        cond['cal_result'] = -1
        cond['error_messages'] += 'Sum of jt become zero.\n'
        return cond

    # 次数の取得
    npr = cond["num_dpr"]

    # 新しい電流分布の作成と保存
    # この時点で、１メッシュ内に流れるトータルの電流に正規化される。
    j0 *= jtotal / jsum  # トータルの電流値が維持されるように調整
    cond['jt'] = conv_1d_array_to_dmat(cond, j0)

    # 新しい圧力由来電流分布の作成と保存
    j0_p = np.dot(a[:, 0:npr], params[0:npr]) * (jtotal/jsum)
    cond['jt_dp'] = conv_1d_array_to_dmat(cond, j0_p)

    # 新しいポロイダル電流由来電流分布の作成と保存
    j0_d = np.dot(a[:, npr:], params[npr:]) * (jtotal/jsum)
    cond['jt_di2'] = conv_1d_array_to_dmat(cond, j0_d)

    # エラー値の算出_エラーの評価方法の幾つか    
    # 1. 単純な二乗残差
    #   domainが大きい場合はエラーが大きくなる？
    #   errest = np.sum((j0 - j) ** 2) / 2
    # 2. 二乗残差の平均(メッシュ当たりのエラー）
    #   domainの大きさに依存しないが、電流の大小に影響を受ける
    #   errest = np.average((j0 - j) ** 2) / 2
    # 3. メッシュ当たりのパーセンテージ絶対誤差の平均のようなもの 
    #   domain, 電流の値に依存しない
    #   errest = np.average(np.abs(j0-j))/np.average(np.abs(j))
    # 4. メッシュの絶対誤差の最大値とメッシュの平均値の比
    errest = np.max(np.abs(j0-j))/np.average(np.abs(j))
    
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

    # プラズマ電流によるフラックス,br, bz
    # ここの箇所は計算時間がかかるので必要最小限に。
    cond["flux_jt"] = pmat.cal_plasma_flux(cond["jt"])
    # cond["br_jt"] = pmat_br.cal_plasma_br(cond["jt"])
    # cond["bz_jt"] = pmat_bz.cal_plasma_bz(cond["jt"])

    # トータルのフラックス, br, bz
    cond["flux"] = emat.dm_add(cond["flux_jt"], cond["flux_coil"])
    #cond["br"] = emat.dm_add(cond["br_jt"], cond["br_coil"])
    #cond["bz"] = emat.dm_add(cond["bz_jt"], cond["bz_coil"])

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
