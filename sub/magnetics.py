from cmath import inf
import numpy as np
from scipy.special import *
from scipy import constants as sc

#https://docs.scipy.org/doc/scipy/reference/constants.html#module-scipy.constants

# 全ての定数の表示
#sc.find()
# 特定の値の表示 (value, unit, uncertainty)
#sc.physical_constants["speed of light in vacuum"]

#u0 = 4*np.pi*1.0e-7 # [N/A**2]: 真空の透磁率
#e0 = 8.8541878128e-12 # : 真空の誘電率
#c0 = 1/(u0*e0)**(0.5) # [m/sec]: 光速
# 素電荷e: sc.e
# 電子の質量me: sc.m_e

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
    # 小数点10桁以下を無視
    r = np.round(r, 10)
    z = np.round(z, 10)
    rc = np.round(rc, 10)
    zc = np.round(zc, 10)
        
    if r == rc and z == zc:
        return 0.0
    if r <= 0.0 or rc <= 0.0:
        return 0.0    
    k= 4*r*rc/((r+rc)**2+(z-zc)**2)
    d = (r-rc)**2+(z-zc)**2
    br = (u0*ic/4/pi)*(z-zc)/k**0.5/(r*rc)**0.5
    br *= 2*(2-k)*rc*ellipe(k)/d-k*ellipk(k)/r
    return br

def bz(r, z, rc, zc, ic):
    # 小数点10桁以下を無視
    r = np.round(r, 10)
    z = np.round(z, 10)
    rc = np.round(rc, 10)
    zc = np.round(zc, 10)
    
    if r == rc and z == zc:
        return 0.0
    # zero divisionを避ける
    if r <= 0.0:
        r = 10**(-7)
    if rc <= 0.0:
        rc = 10**(-7)
    
    k= 4*r*rc/((r+rc)**2+(z-zc)**2)
    d = (r-rc)**2+(z-zc)**2
    bz = (u0*ic/4/pi)*k**0.5/(r*rc)**0.5
    bz *= ellipk(k)-(r**2-rc**2+(z-zc)**2)*ellipe(k)/d
    return bz

        