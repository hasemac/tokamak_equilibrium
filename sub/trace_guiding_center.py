import numpy as np
import copy
from scipy import constants as sc
import sub.magnetics_cond as smc
import vessel.vmat as svm
import sub.runge_kutta as ruku

class Guiding_center:
    
    cond = None # dict: calculation info and result
    mag = None # Magnetic
    direction = 1 # direction of guiding center (1: same to B, -1: opposite)
    negative_energy = False # negative energy in epara occurs
    prms = {} # dictionary for tentative global
    
    def __init__(self, eqcond, calcond):
        self.cond = copy.deepcopy(calcond)
        cond = self.cond
                
        self.mag = smc.Magnetic(eqcond)
        cond['flux'] = self.mag.fl
        cond['br'] = self.mag.br
        cond['bz'] = self.mag.bz

        self.set_initial_params()
        
    def set_initial_params(self):
        cond = self.cond
        mass = cond['mass']
        
        # calculate energy in Joul
        ene = cond['energy_ev'] * sc.e
        cond['energy'] = ene
        
        # total velocity
        v= np.sqrt(2*ene/mass)
        cond['velocity'] = v
        
        # vpara
        d = np.cos(cond['initial_pitch_angle']/180.0*np.pi)
        vpara = v * d

        # direction of guiding centor
        self.direction = np.sign(d)
              
        epara = (1/2.0)*mass*(vpara**2)
        eperp = ene - epara
        
        # magnetic moment
        absb = self.mag.get_abs_mag(cond['initial_pos'])
        cond['magnetic_moment'] = eperp/absb
        
        # initialize parameters
        cond['time'] = [0.0]
        cond['points'] = []
        cond['epara'] = []
        cond['eperp'] = []
        cond['vpara'] = []
        cond['vperp'] = []
        cond['pitch_angle'] = []
        cond['b_abs'] = []
        cond['cyclotron_freq'] = []
        cond['larmor_radius'] = []
        
        # initial calculation        
        self.get_val(0.0, cond['initial_pos'])
        self.add_cal_result(cond['initial_pos'])
        return cond
    
    def calc_runge(self, num, step_width):
        """caluculat trace of guiding center

        Args:
            num (int): iteration number
            step_width (m): step width to move

        Returns:
            dict_type: calculation result
        """
        step = step_width
        rgk = ruku.Runge_kutta(self)
        p0 = self.cond['initial_pos']
        for e in range(num):
            p1 = rgk.one_step(0.0, p0, step) # 1cm pitch
            
            # wallに接触すれば終了
            if rgk.fnc.is_end(0.0, p1):
                print('touch the wall.')
                break
            
            # 計算過程で負のエネルギーが出たら反転させる
            if self.negative_energy:
                #print('reverse')
                self.negative_energy = False
                self.direction *= -1
                #p0 = self.cond['points'][-1]
                #self.add_cal_result(p0) # 同じ点を登録、ただし向きは逆
                continue
            
            self.add_cal_result(p1)
            self.add_time_data()

            p0 = p1
        
        # 出力の調整
        cond = self.cond
        cond['epara'] = np.array(cond['epara'])/sc.e # [eV]
        cond['eperp'] = np.array(cond['eperp'])/sc.e # [eV]
        cond['cyclotron_freq'] = np.array(cond['cyclotron_freq'])/(10**9) # [GHz]
        return self.cond
    
    def add_cal_result(self, p0):
        self.get_val(0.0, p0)
        
        prms = self.prms
        cond = self.cond
        
        cond['points'].append(p0)
        cond['epara'].append(prms['epara'])
        cond['eperp'].append(prms['eperp'])
        cond['vpara'].append(prms['vpara'])
        cond['vperp'].append(prms['vperp'])
        cond['pitch_angle'].append(prms['pitch_angle'])
        cond['b_abs'].append(prms['b_abs'])
        cond['cyclotron_freq'].append(prms['cyclotron_freq'])
        cond['larmor_radius'].append(prms['larmor_radius'])
        
    def add_time_data(self):
        cond = self.cond
        prms = self.prms

        x0, x1 = cond['points'][-2:]
        dist = np.sqrt(np.sum((x0-x1)**2))
        t1 = cond['time'][-1] + dist/prms['total_velocity']
        cond['time'].append(t1)
        
    def get_val(self, t0, x0):
        mag = self.mag
        cond = self.cond
        self.prms = {}
        prms = self.prms
        
        vec_b = mag.get_mag(x0) # vec_b
        b = np.sqrt(np.sum(vec_b**2)) # abs value of vec_b
        eperp = cond['magnetic_moment'] * b
        epara = cond['energy'] - eperp

        if epara < 0:
            # 負のエネルギーが発生したことを通知する。
            self.negative_energy = True
            return np.array((0, 0, 0))
        
        mass = cond['mass']
        charge = cond['charge']
        
        vpara = self.direction * np.sqrt(2*epara/mass)
        vperp = np.sqrt(2*eperp/mass)
        
        pitch_angle = np.arccos(vpara/cond['velocity'])/np.pi*180
        
        vec_vpara = vpara * mag.get_unit_mag(x0)
        # grad B drift
        vec_drift_gradb = (eperp)/(charge*b**3)*np.cross(vec_b, mag.get_grad_mag(x0))
        # curvature drift
        vec_drift_curve = (2*epara)/(charge*b**3)*np.cross(vec_b, mag.get_grad_mag(x0))
        # total drift 
        #vec_drift = (2*epara + eperp)/(charge*b**3)*np.cross(vec_b, mag.get_grad_mag(x0))
        
        vec = vec_vpara + vec_drift_gradb + vec_drift_curve
        #vec = vec_vpara + vec_drift_gradb
        #vec = vec_drift
        
        v_abs = np.sqrt(np.sum(vec**2))
        vec_unit = vec/v_abs
        
        fc = np.abs(charge)*b/(2*sc.pi*mass)
        
        prms['b_abs'] = b
        prms['cyclotron_freq'] = fc
        prms['larmor_radius'] = vperp/(2*sc.pi*fc)
        prms['epara'] = epara
        prms['eperp'] = eperp
        prms['vpara'] = vpara
        prms['vperp'] = vperp
        prms['pitch_angle'] = pitch_angle
        prms['total_velocity'] = v_abs
        
        return vec_unit
    
    def is_end(self, t0, x0):
        x, y, z = x0
        r = np.sqrt(x**2+y**2)
        return not svm.is_inside_vac(r, z)