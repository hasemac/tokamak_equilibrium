import os
import glob
import numpy as np
import pandas as pd
from tqdm import tqdm
from global_variables import gparam
import sub.magnetics as mag
gl = gparam()

# ディレクトリの存在確認
dir0 = os.path.join(gl.root_dir, 'device', gl.device_name, 'coils')
dir_c  = os.path.join(dir0, 'data_csv')
dir_fl = os.path.join(dir0, 'data_npy')
dir_br = os.path.join(dir0, 'data_npy_br')
dir_bz = os.path.join(dir0, 'data_npy_bz')
if not os.path.isdir(dir_fl):
    os.makedirs(dir_fl)
if not os.path.isdir(dir_br):
    os.makedirs(dir_br)
if not os.path.isdir(dir_bz):
    os.makedirs(dir_bz)
    
# コイル名の取得
f_c = glob.glob(os.path.join(dir_c, '*.csv'))
c_name = [os.path.split(e)[1].split('.')[0] for e in f_c]

# 既に存在しているファイルの取得
ex_f_fl = glob.glob(os.path.join(dir_fl, '*.npy'))
ex_f_br = glob.glob(os.path.join(dir_br, '*.npy'))
ex_f_bz = glob.glob(os.path.join(dir_bz, '*.npy'))

# 接続するコイルの情報
inf = gl.connection_pf

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
        for e in tqdm(df.values):
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
        for e in tqdm(df.values):
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
        for e in tqdm(df.values):
            mat += np.array([[mag.bz(r, z, e[0], e[1], 1) for r in gl.r_pos] for z in gl.z_pos])
        
        np.save(wf, mat)

def combine(dir):
    ex_f = glob.glob(os.path.join(dir, '*.npy'))
    for e in inf.keys():
        wf = os.path.join(dir, f"{e}.npy")
        if wf in ex_f:
            continue
        print(f'making {wf}')
        
        mat = np.zeros((gl.nz, gl.nr))
        for c in tqdm(inf[e]):
            mat += c[1] * np.load(os.path.join(dir, f"{c[0]}.npy"))
        np.save(wf, mat)

make_fl()
combine(dir_fl)

make_br()
combine(dir_br)

make_bz()
combine(dir_bz)

def check():
    return 