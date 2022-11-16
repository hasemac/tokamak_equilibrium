import numpy as np
import sub.emat as emat

# R方向の微分
def dm_diff_r(dmat):
    v = dmat['matrix']
    d = np.diff(v, axis = 1) # r方向に差分を取る。
    c = d[:,0]-(d[:, 1]-d[:,0]) # 勾配を維持した値で付加するカラム作成
    c = c.reshape(-1, 1) # ２次元に変換
    d = np.hstack((c, d))/dmat['dr']
    
    return d

# z方向の微分
def dm_diff_z(dmat):
    # iz = 0はzminの場所
    v = dmat['matrix']
    d = np.diff(v, axis = 0) # z方向に差分を取る
    c = d[0,:]-(d[1,:]-d[0,:]) # 勾配を維持した値で付加するカラム作成
    c = c.reshape(1, -1)
    d = np.vstack((c, d))/dmat['dz']
    
    return d

def dm_2pir(d_mat):
    # 1/(2piR)のマトリックスを返す。
    g = emat.dm_array(d_mat)
    r = g.r
    r = r.reshape((g.nz, -1))
    
    # rmin=0のとき発散する。
    # これを避けるために、その隣の値を使用する。
    if 0 == g.rmin:
        r[:,0] = r[:,1]
    
    m = 1/(2*np.pi*r)

    return m

# Brの計算
def get_dm_br(dm_flux):
    r1 = dm_2pir(dm_flux)
    r2 = dm_diff_z(dm_flux)
    r3 = -r1*r2
    dm = emat.get_dmat_dim(dm_flux)
    dm['matrix'] = r3
    return dm

# Bzの計算
def get_dm_bz(dm_flux):
    r1 = dm_2pir(dm_flux)
    r2 = dm_diff_r(dm_flux)
    r3 = r1*r2
    dm = emat.get_dmat_dim(dm_flux)
    dm['matrix'] = r3
    return dm

# Btの計算
def get_dm_bt(dm_pol_cur):
    """プラズマを含むポロイダル電流からBtを計算

    Args:
        dm_pol_cur (dmat): ポロイダル電流 
    """
    r1 = dm_2pir(dm_pol_cur)
    r2 = (4*np.pi*10**(-7))*r1*dm_pol_cur['matrix']
    dm= emat.get_dmat_dim(dm_pol_cur)
    dm['matrix'] = r2
    return dm

class Magnetic:
    
    def __init__(self, dm_flux, dm_polcur):
        self.dm_flux = dm_flux
        self.dm_polcur = dm_polcur
        self.dm_br = get_dm_br(dm_flux)
        self.dm_bz = get_dm_bz(dm_flux)
        self.dm_bt = get_dm_bt(dm_polcur)
        
    def get_br(self, r, z):
        return emat.linval2(r, z, self.dm_br)
    
    def get_bz(self, r, z):
        return emat.linval2(r, z, self.dm_bz)
    
    def get_bt(self, r, z):
        return emat.linval2(r, z, self.dm_bt)
    
    def get_mag(self, p3):
        x, y, z = p3
        r = np.sqrt(x**2 + y**2)
        cos = x/r
        sin = y/r
        
        br = self.get_br(r, z)
        bz = self.get_bz(r, z)
        bt = self.get_bt(r, z)
        
        bx = br*cos - bt*sin
        by = br*sin + bt*cos
        
        return (bx, by, bz)