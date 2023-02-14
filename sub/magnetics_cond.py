import numpy as np
import copy
import coils.cmat as cfl
import coils.cmat_br as cbr
import coils.cmat_bz as cbz
import plasma.pmat as pfl
import plasma.pmat_br as pbr
import plasma.pmat_bz as pbz
import sub.emat as emat
import sub.sub_func as ssf

class Magnetic:
    
    fl = None # flux
    br = None # br
    bz = None # bz
    
    def __init__(self, cond):
        cond = ssf.check_tf_rewind(cond)
        
        self.fl_c = cfl.get_flux_of_coil(cond)
        self.br_c = cbr.get_br_of_coil(cond)
        self.bz_c = cbz.get_bz_of_coil(cond)
        
        if 'jt' in cond:
            self.fl_p = pfl.cal_plasma_flux(cond['jt'])
            self.br_p = pbr.cal_plasma_br(cond['jt'])
            self.bz_p = pbz.cal_plasma_bz(cond['jt'])
            self.fl = emat.dm_add(self.fl_c, self.fl_p)
            self.br = emat.dm_add(self.br_c, self.br_p)
            self.bz = emat.dm_add(self.bz_c, self.bz_p)
            
        else:
            self.fl = self.fl_c
            self.br = self.br_c
            self.bz = self.bz_c
            
        if 'pol_current' in cond:
            self.bt = self.get_dm_bt(cond['pol_current'])
        else:
            self.bt = self.get_tor_bt(cond)

    def get_br(self, r, z):
        return emat.linval2(r, z, self.br)
    
    def get_bz(self, r, z):
        return emat.linval2(r, z, self.bz)
    
    def get_bt(self, r, z):
        return emat.linval2(r, z, self.bt)
    
    def get_fl(self, r, z):
        return emat.linval2(r, z, self.fl)
    
    def get_bz_c(self, r, z):
        return emat.linval2(r, z, self.bz_c)
    
    def get_decay_index(self, r, z):
        # decay indexはコイルの磁場から計算
        # プラズマによる磁場は含まない
        w = 1.0e-7
        delbz = (self.get_bz_c(r + w/2, z) - self.get_bz_c(r - w/2, z))/w
        bz = self.get_bz_c(r, z)
        if bz == 0.0:
            bz = 1.0e-7
        return -(r/bz)*delbz
    
    # 磁場ベクトルの取得
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
        
        return np.array((bx, by, bz))
    
    # 磁場強度(スカラー)の取得
    def get_abs_mag(self, p3):
        """get_abs_mag

        Args:
            p3 (tuple): position (x, y, z) to calculate

        Returns:
            float: abs value of B
        """
        b = self.get_mag(p3)
        return np.sqrt(np.sum(b**2))
    
    # 磁場方向の単位ベクトルの取得
    def get_unit_mag(self, p3):
        """get unit vector of B

        Args:
            p3 (tuple): position (x, y, z) to calculate

        Returns:
            np.array: unit vector (bx0, by0, bz0)
        """
        absb = self.get_abs_mag(p3)
        b = self.get_mag(p3)
        return b/absb
    
    def get_grad_mag(self, p3):
        w = 1.0e-7
        p = np.array(p3) # tupleどうしの加算は要素が増える。どっちかはnumpyに変換する必要。
        abmag = self.get_abs_mag
        dbx = (abmag(p+(w/2, 0, 0)) - abmag(p-(w/2, 0, 0)))/w
        dby = (abmag(p+(0, w/2, 0)) - abmag(p-(0, w/2, 0)))/w
        dbz = (abmag(p+(0, 0, w/2)) - abmag(p-(0, 0, w/2)))/w
        return np.array((dbx, dby, dbz))
        
    def dm_2pir(self, d_mat):
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
    
    # Btの計算（プラズマ含まず）
    def get_tor_bt(self, cond):
        dm = copy.deepcopy(cond["resolution"])
        r1 = self.dm_2pir(dm)
        val = cond['cur_tf']['tf'] * cond['cur_tf']['turn']
        r2 = (4*np.pi*10**(-7))*r1*val
        dm['matrix'] = r2
        return dm
    
    # Btの計算（プラズマ含む）
    def get_dm_bt(self, dm_pol_cur):
        """プラズマを含むポロイダル電流からBtを計算

        Args:
            dm_pol_cur (dmat): ポロイダル電流 
        """
        r1 = self.dm_2pir(dm_pol_cur)
        r2 = (4*np.pi*10**(-7))*r1*dm_pol_cur['matrix']
        dm= emat.get_dmat_dim(dm_pol_cur)
        dm['matrix'] = r2
        return dm