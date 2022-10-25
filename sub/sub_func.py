import numpy as np
import warnings
from scipy.optimize import curve_fit

def fitting_quad_func(data_array2d):
    """fitting関数の係数を返す。
    2次元データ[y, x]を与えて関数
    z = a*x**2 + b*x*y + c*y**2 + d*x + e*y + f
    でフィッティングした時の径数
    (a, b, c, d, e, f)を返す。

    Args:
        data_array2d (2d_matrix): 最小3 X 3の計9点を与えること

    Returns:
        coef, cov: 最初の要素が係数、次がフィッティング誤差
    """
    nz, nr = data_array2d.shape

    r = np.array([[e-(nr // 2) for e in range(nr)] for f in range(nz)])
    z = np.array([[f-(nz // 2) for e in range(nr)] for f in range(nz)])
    
    r = r.reshape(-1)
    z = z.reshape(-1)
    dat = data_array2d.reshape(-1)
    
    def func(u, a, b, c, d, e, f):
        x, y = u
        z = a*x**2 + b*x*y + c*y**2 + d*x + e*y + f
        return z
    
    #import io
    #import sys
    #with io.StringIO() as f:
    #    sys.stdout = f
    #    a = curve_fit(func, (r, z), dat)        
    #    sys.stdout = sys.__stdout__

    warnings.filterwarnings('ignore')
    res = curve_fit(func, (r, z), dat)
    warnings.filterwarnings('default')
    return res

def find_extremum_loc_and_val(data_array2d):
    """極値のある位置と、極値を返す。
    9点のデータが与えられたときフィッティング関数の
    極値の位置と極値を返す。
    Args:
        data_array2d (2d_matrix): 最小3 X 3の計9点を与えること

    Returns:
        array of float: dz, dr, val (dz, drは[-1, 1]の範囲の値)
    """

    (a, b, c, d, e, f), _ = fitting_quad_func(data_array2d)
    
    # calc position of local minimum or local maximum
    dr = (2*c*d-b*e)/(b**2-4*a*c)
    dz = (2*a*e-b*d)/(b**2-4*a*c)
    
    val = (c*d**2 - b*d*e + a*e**2 + b**2*f - 4*a*c*f)/(b**2 - 4*a*c)
    return dz, dr, val

def find_points_of_quad_func(data_array2d, val):
    """valで与えられる2次関数上の点群を返す。
    val = a*r**2 + b*r*z + c*z**2 + d*r + e*z + f
    で与えられる(z, r)の曲線上の点群を返す。
    Args:
        data_array2d (2d_matrix): 最小3 X 3の計9点を与えること
        val (float): 2時間数を定義する値

    Returns:
        array of (z, r): _description_
    """
    
    nz, nr = data_array2d.shape
    (a, b, c, d, e, f), _ = fitting_quad_func(data_array2d)
    
    r = np.linspace(-(nr // 2), (nr // 2), nr*20) # 1メッシュで20ポイント
    r1 = (e + b*r)**2 - 4*c*(f - val + d*r + a*r**2)
    r2 = r[r1 >= 0] # 解が実数であるrを取得
    r3 = np.sqrt(r1[r1 >= 0]) # その時のルートの値を計算
    
    pz0 = (-e - b*r2 - r3)/(2*c)
    p0 = [(z, r) for z, r in zip(pz0, r2) if -(nz//2) <= z <= (nz//2)]
    
    pz1 = (-e - b*r2 + r3)/(2*c)
    p1 = [(z, r) for z, r in zip(pz1, r2) if -(nz//2) <= z <= (nz//2)]
    
    z = np.linspace(-(nz // 2), (nz // 2), nz*20) # 1メッシュで20ポイント
    z1 = (d + b*z)**2 - 4*a*(f - val + e*z + c*z**2)
    z2 = z[z1 >= 0] # 解が実数であるzを取得
    z3 = np.sqrt(z1[z1 >= 0]) # その時のルートの値を計算
    
    pr0 = (-d - b*z2 -z3)/(2*a)
    p2 = [(z, r) for z, r in zip(z2, pr0) if -(nr//2) <= r <= (nr//2)]
    
    pr1 = (-d - b*z2 +z3)/(2*a)
    p3 = [(z, r) for z, r in zip(z2, pr1) if -(nr//2) <= r <= (nr//2)]
    
    p0.extend(p1)
    p0.extend(p2)
    p0.extend(p3)
    return p0

def shift_x(mat, num: int, val: float):
    """shift mat in x direction

    Args:
        mat (2d_array): 2d_array of numpy
        num (int): shift right when num>0, and left when num<0
        val (float): fill with this value

    Returns:
        2d_array: shifted matrix
    """
    o = np.roll(mat, num, axis=1)
    if num > 0:
        o[:, :num] = val
    elif num < 0:
        o[:, num:] = val
        
    return o

def shift_y(mat, num: int, val: float):
    """shift mat in y direction

    Args:
        mat (2d_array): 2d_array of numpy
        num (int): shift down when num>0, and up when num<0
        val (float): fill with this value

    Returns:
        2d_array: shifted matrix
    """
    o = np.roll(mat, num, axis=0)
    if num > 0:
        o[:num,:] = val
    elif num < 0:
        o[num:,:] = val
    return o