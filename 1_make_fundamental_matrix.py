import sys, os
import glob
import pandas as pd
import numpy as np
import plasma.pmat
import plasma.pmat_br
import plasma.pmat_bz

from global_variables import gparam
import sub.magnetics as mag
gl = gparam()

# ディレクトリ情報
dir_c  = os.path.join(gl.root_dir, "coils\\data_csv\\")
dir_fl = os.path.join(gl.root_dir, "coils\\data_npy\\")
dir_br = os.path.join(gl.root_dir, "coils\\data_npy_br\\")
dir_bz = os.path.join(gl.root_dir, "coils\\data_npy_bz\\")

# 連結するマトリックスの情報
inf = {
    'pf17t4':[('pf1t4',1), ('pf7t4', 1)],
    'pf17t8':[('pf1t8',1), ('pf7t8', 1)],
    'pf17t12':[('pf1t12',1), ('pf7t12', 1)],
    'pf17t12':[('pf1t12',1), ('pf7t12', 1)],
    'pf26t18':[('pf2t18',1), ('pf6t18', 1)],
    'pf26t36':[('pf2t36',1), ('pf6t36', 1)],
    'pf26t72':[('pf2t72',1), ('pf6t72', 1)],
    'pf35_1':[('pf3_1',1), ('pf5_1', 1)],  
    'pf35_2':[('pf3_2',1), ('pf5_2', 1)],
    'pf35_12':[('pf3_1',1), ('pf3_2',1), ('pf5_1', 1), ('pf5_2',1)],
    'pf4_1ab3_cc1':[('pf41', 1), ('pf42a', 1), ('pf42b', 1), ('pf43', 1), ('cct1', 1)],
    'pf4_1a3_cc1':[('pf41', 1), ('pf42a', 1), ('pf43', 1), ('cct1', 1)],
    'pf4_1ab3_cc2':[('pf41', 1), ('pf42a', 1), ('pf42b', 1), ('pf43', 1), ('cct2', 1)],
    'pf4_1a3_cc2':[('pf41', 1), ('pf42a', 1), ('pf43', 1), ('cct2', 1)],
    'hcult6':[('hcut6', 1), ('hclt6', -1)],
    'hcult16':[('hcut16', 1), ('hclt16', -1)],
    'pf4_ab_cc2':[('pf42a', 1), ('pf42b', 1), ('cct2', 1)], 
    'tf_rewind':[('tf_rewind_1', -1), ('tf_rewind_2', 1)],
    }

# 初期変数の取得
f_c = glob.glob(dir_c+'*.csv')
c_name = [(e.split('\\')[-1]).split('.')[0] for e in f_c]
# 既に存在しているファイルの取得
ex_f_fl = glob.glob(dir_fl+'*.npy')
ex_f_br = glob.glob(dir_br+'*.npy')
ex_f_bz = glob.glob(dir_bz+'*.npy')

# flux of coil
def make_fl():
    for e in zip(f_c, c_name):
        rf, cn = e
        wf = os.path.join(dir_fl, f"{cn}.npy")
        if wf in ex_f_fl:
            continue
        print(f'making {wf}')
        
        df = pd.read_csv(rf)
        
        mat = np.zeros((gl.nz, gl.nr))
        for e in df.values:
            mat += np.array([[mag.flux(r, z, e[0], e[1], 1) for r in gl.r_pos] for z in gl.z_pos])
        
        np.save(wf, mat)
        
# br of coil
def make_br():
    for e in zip(f_c, c_name):
        rf, cn = e
        wf = os.path.join(dir_br, f"{cn}.npy")
        if wf in ex_f_br:
            continue
        print(f'making {wf}')
        
        df = pd.read_csv(rf)
        
        mat = np.zeros((gl.nz, gl.nr))
        for e in df.values:
            mat += np.array([[mag.br(r, z, e[0], e[1], 1) for r in gl.r_pos] for z in gl.z_pos])
        
        np.save(wf, mat)

# bz of coil
def make_bz():
    for e in zip(f_c, c_name):
        rf, cn = e
        wf = os.path.join(dir_bz, f"{cn}.npy")
        if wf in ex_f_bz:
            continue
        print(f'making {wf}')
        
        df = pd.read_csv(rf)
        
        mat = np.zeros((gl.nz, gl.nr))
        for e in df.values:
            mat += np.array([[mag.bz(r, z, e[0], e[1], 1) for r in gl.r_pos] for z in gl.z_pos])
        
        np.save(wf, mat)

def combine(dir):
    ex_f = glob.glob(dir+'*.npy')
    for e in inf.keys():
        wf = os.path.join(dir, f"{e}.npy")
        if wf in ex_f:
            continue
        print(f'making {wf}')
        
        mat = np.zeros((gl.nz, gl.nr))
        for c in inf[e]:
            mat += c[1] * np.load(os.path.join(dir, f"{c[0]}.npy"))
        np.save(wf, mat)
        
if __name__ == "__main__":
    if not os.path.exists(dir_br):
        os.makedirs(dir_br)
    if not os.path.exists(dir_bz):
        os.makedirs(dir_bz)
    
    make_fl()
    combine(dir_fl)
    
    make_br()
    combine(dir_br)
    
    make_bz()
    combine(dir_bz)
    