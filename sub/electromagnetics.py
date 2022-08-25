from cmath import inf
import numpy as np
from scipy.special import *
from scipy import constants as sc
import sub.functions as sfn

# 全ての定数の表示
#sc.find()
# 特定の値の表示 (value, unit, uncertainty)
#sc.physical_constants["speed of light in vacuum"]

#u0 = 4*np.pi*1.0e-7 # [N/A**2]: 真空の透磁率
#e0 = 8.8541878128e-12 # : 真空の誘電率
#c0 = 1/(u0*e0)**(0.5) # [m/sec]: 光速

u0 = sc.mu_0 # 真空の透磁率
e0 = sc.epsilon_0 # 真空の誘電率
c0 = sc.c # 光速
pi = sc.pi

def flux(r, z, rc, zc, ic):
    # 小数点10桁以下を無視
    r = np.round(r, 10)
    z = np.round(z, 10)
    rc = np.round(rc, 10)
    zc = np.round(zc, 10)
    
    if r <= 0.0 or rc <= 0.0:
        return 0.0
    if r == rc and z == zc:
        return 0.0
    k= 4*r*rc/((r+rc)**2+(z-zc)**2)
    fx = (2*pi*r)*(u0*ic/pi/k**0.5)*(rc/r)**0.5
    fx *= (1-k/2)*ellipk(k)-ellipe(k)
    if fx == inf:
        print(r, z, rc, zc, ic)
    return fx

def br(r, z, rc, zc, ic):
    if 0 == r or 0 == rc:
        return 0.0    
    k= 4*r*rc/((r+rc)**2+(z-zc)**2)
    d = (r-rc)**2+(z-zc)**2
    br = (u0*ic/4/pi)*(z-zc)/k**0.5/(r*rc)**0.5
    br *= 2*(2-k)*rc*ellipe(k)/d-k*ellipk(k)/r
    return br

def bz(r, z, rc, zc, ic):
    k= 4*r*rc/((r+rc)**2+(z-zc)**2)
    d = (r-rc)**2+(z-zc)**2
    bz = (u0*ic/4/pi)*k**0.5/(r*rc)**0.5
    bz *= ellipk(k)-(r**2-rc**2+(z-zc)**2)*ellipe(k)/d
    return bz

class Magnetic:
    
    def __init__(self, dm_flux, dm_polcur):
        self.dm_flux = dm_flux
        self.dm_polcur = dm_polcur
        self.dm_br = sfn.get_dm_br(dm_flux)
        self.dm_bz = sfn.get_dm_bz(dm_flux)
        self.dm_bt = sfn.get_dm_bt(dm_polcur)
        
    def get_br(self, r, z):
        return sfn.linval(r, z, self.dm_br)
    
    def get_bz(self, r, z):
        return sfn.linval(r, z, self.dm_bz)
    
    def get_bt(self, r, z):
        return sfn.linval(r, z, self.dm_bt)
    
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
        