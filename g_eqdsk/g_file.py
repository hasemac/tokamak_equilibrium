import numpy as np
import sub.emat as emat

# formatの説明
# https://w3.pppl.gov/ntcc/TORAY/G_EQDSK.pdf
#
# g-fileの読書き込みをpythonで行う
# https://github.com/bendudson/pyTokamak/blob/master/tokamak/formats/geqdsk.py
#
# g-fileの例
# \\192.168.71.10\docResearch\simulationCode\EFIT_in_windows\EFIT\Editor\NSTX_data
#
# format (6a8,3i4) 48文字？と4桁右詰め整数が３つ
# format (5e16.9) 16桁科学表記・小数点幅9が５つ
# format (2i5) 5桁右詰め整数が２つ

def split_str(string, lis_int):
    """文字列を文字数の配列に従って分割する。

    Args:
        string (str): 文字列
        lis_int (list[int]): 文字数の配列

    Returns:
        list[str]: 文字数に従って分割された文字列の配列
    """
    a = [0]+list(np.array(lis_int).cumsum())
    ls = [string[a[i]:a[i+1]] for i in range(len(a)-1)]
    return ls

def get_float(string, lis_int):
    a = split_str(string, lis_int)
    return [float(e) for e in a]

def get_shapes(points):
    """pointを線でつなぐ

    Args:
        points (ndarray): [[x0, y0], [x1, y1], [x2, y2],,,,]

    Returns:
        list[dict]: [{'type':'line', 'x0':x0, 'y0':y0, 'x1':x1, 'y1':y1},,,]
    """
    pts = points.tolist() # numpyをlistへ
    lines = []
    for e in range(len(pts)-1):
        lines.append(pts[e]+pts[e+1])
    shp = [dict(type='line', x0=e[0], y0=e[1], x1=e[2], y1=e[3]) for e in lines]
    return shp
    
def read_g_file(absfile):
    with open(absfile, 'r') as f:
        l = f.readlines()
    l = [e.replace('\n', '') for e in l] # 最後の改行コードは削除
    
    # 最初の行の解析
    a = split_str(l[0], [48, 4, 4, 4])
    case, nw, nh = a[0], int(a[2]), int(a[3])

    # 途中の整数の行を検索して解析
    # フォーマットの記述によれば次の記述があって、文字列の長さが10である行が存在している。
    # read (neqdsk,2022) nbbbs,limitr
    # 2022 format (2i5)
    a = np.array([len(e) for e in l])
    idx = (np.where(a == 10))[0][0] # 文字列の長さが10であるインデックスを取得
    a = split_str(l[idx], [5, 5])
    nbbbs, limitr = int(a[0]), int(a[1])

    # 後半部の終わりのインデックスを計算
    # 後半部は次の記述。nbbbs*2個の数値データ。limitr*2個の数値データ
    # read (neqdsk,2020) (rbbbs(i),zbbbs(i),i=1,nbbbs)
    # read (neqdsk,2020) (rlim(i),zlim(i),i=1,limitr)
    # 2020 format (5e16.9)
    idx2 = idx
    qu, su = divmod(nbbbs*2, 5)
    idx2 += qu + (1 if su != 0 else 0)
    qu, su = divmod(limitr*2, 5)
    idx2 += qu + (1 if su != 0 else 0)
    idx2 += 1

    # 前半部と後半部を取得して、それぞれ文字列を作成
    p1 = l[1:idx]
    p2 = l[idx+1:idx2]
    s1 = ""
    for e in p1:
        s1 += e
    s2 = ""
    for e in p2:
        s2 += e

    # 16文字ずつ分割してfloatを取得
    n = 16
    l1 = np.array([float(s1[i:i+n]) for i in range(0, len(s1), n)])
    l2 = np.array([float(s2[i:i+n]) for i in range(0, len(s2), n)])
    
    rdim, zdim, rcentr, rleft, zmid         = l1[0:5]
    rmaxis, zmaxis, simag, sibry, bcentr    = l1[5:10]
    current, simag, xdum, rmaxis, xdum      = l1[10:15]
    zmaxis, xdum, sibry, xdum, xdum         = l1[15:20]
    
    num = 20
    fpol = l1[num:num+nw]

    num += nw
    pres = l1[num:num+nw]

    num += nw
    ffprim = l1[num:num+nw]

    num += nw
    pprime = l1[num:num+nw]

    num += nw
    psizr = l1[num:num+nw*nh].reshape(nh, nw)

    num += nw*nh
    qpsi = l1[num:num+nw]

    bbbs = l2[:nbbbs*2].reshape(-1, 2)
    lim = l2[nbbbs*2:nbbbs*2 + limitr*2].reshape(-1, 2)
    
    shbbbs = get_shapes(bbbs)
    shlim = get_shapes(lim)
    
    # dict型にまとめる
    prm = {}
    # original
    prm['case'] = case
    prm['nw'] = nw # 水平方向のグリッドポイント数
    prm['nh'] = nh # 垂直方向のグリッドポイント数
    prm['rdim'], prm['zdim'] = rdim, zdim # 水平・垂直方向の計算領域[meter]
    prm['rcentr'] = rcentr # bcenterで定義されるトロイダル磁場のR位置
    prm['rleft'], prm['zmid'] = rleft, zmid # 計算領域の左位置と垂直方向の真ん中の位置
    prm['rmaxis'], prm['zmaxis'] = rmaxis, zmaxis # 磁気軸位置
    prm['simag'], prm['sibry'] = simag, sibry # 磁気軸と最外殻におけるポロイダルフラックス[Weber/rad]
    prm['bcentr'] = bcentr # 真空のトロイダル磁場 [Tesla]
    prm['current'] = current # プラズマ電流 [A]
    # x=0 on axis, x=1 on boundary with normalized flux
    prm['fpol'] = fpol      # [meter tesla]  磁気軸から最外殻磁気面までのポロイダル電流
    prm['pres'] = pres # プラズマ圧力 [nt/m^2]
    prm['ffprim'] = ffprim
    prm['pprime'] = pprime
    prm['psizr'] = psizr
    prm['qpsi'] = qpsi # 磁気軸から最外殻までの安全係数
    prm['nbbs'] = nbbbs # 最外殻のポイント数
    prm['limitr'] = limitr # リミターのポイント数
    prm['rbbbs'] = bbbs[:, 0] # 最外殻のポイントのR位置
    prm['zbbbs'] = bbbs[:, 1] # 最外殻のポイントのz位置
    prm['rlim'] = lim[:, 0] # リミターのポイントのR位置
    prm['zlim'] = lim[:, 1] # リミターのポイントのz位置
    
    # additional
    prm['bbbs'] = bbbs
    prm['lim'] = lim
    prm['shbbbs'] = shbbbs
    prm['shlim'] = shlim
    prm['zmin'] = zmid-zdim/2.0
    prm['dr'] = rdim/(nw-1) # 始点と終了点を含むとしたとき、割る数は一つ小さくする必要がある。
    prm['dz'] = zdim/(nh-1)
    return prm

def is_corner(mat):
    """コーナーであるかの判定

    Args:
        mat (np.array[3,3]): element: 1 or 0

    Returns:
        bool: True: corner, False: not corner
    """
    # 自分自身がないものはFalse
    if mat[1, 1] == 0:
        return False
    # 自分を含め周囲に7点があるのもコーナーにはなり得ない。
    s = np.sum(mat.reshape(-1))
    if s >= 7:
        return False
    # 自分を含め周囲が5点以下のものはコーナーである可能性が高い
    if s <= 5:
        return True
    # 周囲が6点ある場合で、コーナーでない場合のパターンで判定
    patterns = [ # patterns of not corner
        [[0, 0, 0],[1, 1, 1],[1, 1, 1]],
        [[1, 1, 0],[1, 1, 0],[1, 1, 0]],
        [[1, 1, 1],[1, 1, 1],[0, 0, 0]],    
        [[0, 1, 1],[0, 1, 1],[0, 1, 1]],    
    ]
    res = True
    for e in patterns:
        if np.array_equal(mat, e):
            res = False
            break
    return res

def get_domain(g_params, dm_type):
    pr = g_params
    xs, ys = pr['rbbbs'], pr['zbbbs'] 
    
    if dm_type == 'LIMITR':
        xs, ys = pr['rlim'], pr['zlim'] 
        
    points = [(xs[0], ys[0])]
    dl = np.min([pr['dr'], pr['dz']]) # width
    # まず、線上の点を算出
    for e in zip(xs, ys):
        last_point = points[-1]
        length = np.sum((np.array(last_point)-np.array(e))**2)**(0.5)
        num = int((length/dl))
        num +=2
        new_points = [(e[0], e[1]) for e in np.linspace(last_point, e, num)]
        points += new_points

    # 線上の点をドメインに記入
    dm = np.zeros(pr['nw']*pr['nh']).reshape(pr['nh'], pr['nw'])
    rmin = pr['rleft']
    zmin = pr['zmid']-pr['zdim']/2.0
    for e in points:
        nr = int((e[0]-rmin)/pr['dr'])
        nz = int((e[1]-zmin)/pr['dz'])
        dm[nz, nr] = 1

    # 点で挟まれた領域を追加する
    for e in dm:
        n = np.where(e == 1)
        n = n[0]
        if len(n) <= 1:
            continue
        e[n[0]:n[-1]] = 1    
        
    return dm

def arg_closest_point(pt, pts):
    dist = [(pt[0]-e[0])**2+(pt[1]-e[1])**2 for e in pts]
    return np.argmin(dist)

def get_boundary_points(dmat):
    g = emat.dm_array(dmat)
    ir = g.ir
    iz = g.iz
    nr = g.nr
    nz = g.nz
    rr = g.r
    zz = g.z
    d = dmat['matrix']
    d2 = np.pad(d, [(1, 1), (1, 1)])
    bnd = np.zeros((nz, nr))
    bna = []

    # 境界の点を抽出
    for i, j, r, z in zip(ir, iz, rr, zz):
        ni, nj = i + 1, j +1
        m = d2[nj-1:nj+2, ni-1:ni+2]
        if is_corner(m): # 境界にある点を抽出
            bnd[j, i] = 1.0 # 境界の点をマトリックスで登録
            bna.append([z, r])
    
    # 点の順番の並び替え
    res = []
    p0 = bna[0]
    res.append(p0)
    near = np.delete(bna, 0, axis=0)
    while len(near) != 0:
        i = arg_closest_point(p0, near)
        p0 = near[i]
        res.append(p0)
        near = np.delete(near, i, axis=0)

    res = [[e[1], e[0]] for e in res] # [x0, z0]の順番にする
    res.append(res[0]) # 最初のポイントを最後に追加して線を閉じる。
    res = np.array(res)
    return res

def convert_to_g_parm(cond):
    
    da = emat.dm_array(cond['domain'])
    
    pr = {}
    pr['case'] = 'comment'
    pr['nw'] = da.nr
    pr['nh'] = da.nz
    pr['rdim'] = da.rmax - da.rmin
    pr['zdim'] = da.zmax - da.zmin
    pr['rcentr'] = 1.0
    total_tf = cond['cur_tf']['tf']*cond['cur_tf']['turn']
    pr['bcentr'] = (2.0*np.pi)**(0.5)*2.0*1.0e-7*total_tf/pr['rcentr']
    pr['rleft'] = da.rmin
    pr['zmid'] = (da.zmax + da.zmin)/2.0
    pr['rmaxis'] = cond['r_ax']
    pr['zmaxis'] = cond['z_ax']
    pr['simag'] = cond['f_axis']
    pr['sibry'] = cond['f_surf']
    pr['current'] = cond['cur_ip']['ip']
    pr['fpol'] = cond['pol_current_norm']*(2.0*np.pi)**(0.5) * 2.0*1.0e-7
    pr['pres'] = cond['pressure_norm']*(2.0*np.pi)
    pr['ffprim'] = cond['diff_i2_norm']*(2.0*np.pi) /2.0 * (2.0*1.0e-7)**2
    pr['pprime'] = cond['diff_pre_norm']*(2.0*np.pi)
    pr['psizr'] = cond['flux']
    pr['qpsi'] = cond['safety_factor_norm']
    plbound = get_boundary_points(cond['domain'])
    vacvess = get_boundary_points(cond['vessel'])
    pr['nbbbs'] = len(plbound)
    pr['limitr'] = len(vacvess)
    pr['rbbbs'] = plbound[:, 0]
    pr['zbbbs'] = plbound[:, 1]
    pr['rlim'] = vacvess[:, 0]
    pr['zlim'] = vacvess[:, 1]
    
    pr['xdum'] = 0.0 # dummy
    
    # additional
    pr['bbbs'] = plbound
    pr['lim'] = vacvess
    
    return pr

def fl_to_str_for_gfile(arr_float):
    """float配列を受け取り、規定文字数ごとの文字列配列に変換。

    Args:
        arr_float (array(float)): float配列

    Returns:
        list(str): float配列を文字列配列に変換したもの
    """
    numchar = 80 # 1行当たりの文字数
    
    # 一つの数値を16文字(小数点以下9桁)に変換して結合
    st = "".join([f"{e:16.9e}" for e in arr_float])
    
    # numchar毎に分割
    res = []
    while len(st) >= numchar:
        res.append(st[:numchar])
        st = st[numchar:]
    if len(st) != 0:
        res.append(st)
        
    return res

def write_g_file(absfile, cond):
    
    pr = convert_to_g_parm(cond)
    
    a = ['rdim', 'zdim', 'rcentr', 'rleft', 'zmid', 
        'rmaxis', 'zmaxis', 'simag', 'sibry', 'bcentr', 
        'current', 'simag', 'xdum', 'rmaxis', 'xdum', 
        'zmaxis', 'xdum', 'sibry', 'xdum', 'xdum', ]
    b = [pr[e] for e in a]
    
    wrli = [f"{pr['case']: <48}{3: 4}{pr['nw']: 4}{pr['nh']: 4}"]
    wrli += fl_to_str_for_gfile(b)
    wrli += fl_to_str_for_gfile(pr['fpol'])
    wrli += fl_to_str_for_gfile(pr['pres'])
    wrli += fl_to_str_for_gfile(pr['ffprim'])
    wrli += fl_to_str_for_gfile(pr['pprime'])
    wrli += fl_to_str_for_gfile(pr['psizr']['matrix'].reshape(-1))
    wrli += fl_to_str_for_gfile(pr['qpsi'])
    wrli += [f"{pr['nbbbs']: 5}{pr['limitr']: 5}"]
    wrli += fl_to_str_for_gfile(pr['bbbs'].reshape(-1))
    wrli += fl_to_str_for_gfile(pr['lim'].reshape(-1))

    # 改行コードの追加
    wrli = [e+'\n' for e in wrli]
    
    with open(absfile, 'w') as f:
        f.writelines(wrli)