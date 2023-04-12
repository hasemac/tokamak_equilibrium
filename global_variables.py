device_name = "quest"
root_dir = "."
#root_dir = "c:\\home\\code\\tokamak_equilibirum\\"

import sys, os
import numpy as np
import pandas as pd
path = os.path.join(root_dir, 'device', device_name)
sys.path.append(path)
from parameters import equi_params
import sub.sub_func as ssf

class gparam(equi_params):
    
    device_name = device_name
    root_dir = root_dir
    
    nr, nz = None, None
    r_pos, z_pos = [], []
    
    cnr, cnz = None, None
    cr_pos, cz_pos = [], []

    image_frame = None # collection of lines
    vessel = None # dm_mat

    def __init__(self):
        # conversion from real position to num is below
        # round((r-r_rmin)/del_r)
        
        self.set_mesh_info()        
        self.set_image_info()
        self.set_vessel_info()
        
         
    def __setattr__(self, name, value):
        if name in self.__dict__:
            # 定義されたら例外出す
            raise TypeError(f"Caution! Can't rebind const ({name})")
        self.__dict__[name] = value

    def get_dmat_fine(self):
        a = {
            "rmin": self.r_min,
            "rmax": self.r_max,
            "dr": self.del_r,
            "zmin": self.z_min,
            "zmax": self.z_max,
            "dz": self.del_z,
        }
        return a

    def get_dmat_coarse(self):
        a = {
            "rmin": self.cr_min,
            "rmax": self.cr_max,
            "dr": self.cdel_r,
            "zmin": self.cz_min,
            "zmax": self.cz_max,
            "dz": self.cdel_z,
        }
        return a

    def set_mesh_info(self):
        self.r_pos = np.arange(self.r_min, self.r_max + self.del_r / 2, self.del_r)
        self.nr = int((self.r_max - self.r_min) / self.del_r + 1)

        self.z_pos = np.arange(self.z_min, self.z_max + self.del_z / 2, self.del_z)
        self.nz = int((self.z_max - self.z_min) / self.del_z + 1)

        self.cr_pos = np.arange(self.cr_min, self.cr_max + self.cdel_r / 2, self.cdel_r)
        self.cnr = int((self.cr_max - self.cr_min) / self.cdel_r + 1)

        self.cz_pos = np.arange(self.cz_min, self.cz_max + self.cdel_z / 2, self.cdel_z)
        self.cnz = int((self.cz_max - self.cz_min) / self.cdel_z + 1)
                
    def set_image_info(self):
        xl, xr = self.image_x0, self.image_x0 + self.image_sizex
        yt, yb = self.image_y0, self.image_y0 - self.image_sizey
        fr = [
            dict(type='line', x0=xl, y0=yt, x1=xr, y1=yt),
            dict(type='line', x0=xr, y0=yt, x1=xr, y1=yb),
            dict(type='line', x0=xr, y0=yb, x1=xl, y1=yb),
            dict(type='line', x0=xl, y0=yb, x1=xl, y1=yt),
        ]
        if self.image_type == 'lines':
            df = pd.read_csv(self.image_path)
            fr2 = [dict(type='line', x0=e[0], y0=e[1], x1=e[2], y1=e[3]) for e in df.values]
            self.image_frame = fr + fr2
        else:
            self.image_frame = fr

    def set_vessel_info(self):
        path = os.path.join(self.root_dir, 'device', self.device_name, 'vessel')
        
        # ディレクトリ有無の確認
        if not os.path.exists(path):
            os.makedirs(path)
                    
        # ファイル有無の確認
        file = os.path.join(path, 'vessel.npy')
        if os.path.exists(file):
            self.vessel = np.load(file, allow_pickle=True).item()
            return
        
        # ファイルが存在しないので作成する。
        print('making vessel matrix.')
        d_mat = self.get_dmat_fine()
        d_mat['matrix'] = np.zeros((self.nz, self.nr))
        pts = self.vessel_points
        for e in range(len(pts)-1):
            ssf.draw_line(d_mat, pts[e], pts[e+1])
        # 計算エリアの中心点からPaintをする。
        p0 = ((self.r_max+self.r_min)/2.0, (self.z_max+self.z_min)/2.0)
        self.vessel = ssf.draw_paint(d_mat, p0)
        np.save(file, self.vessel)
                
# import sys
# sys.modules["equilibrium_global"]=_const()
