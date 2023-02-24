import numpy as np


class gparam:

    # fine mesh
    r_min, r_max, del_r = 0.0, 1.8, 0.01
    z_min, z_max, del_z = -1.8, 1.8, 0.01

    nr, nz = None, None
    r_pos, z_pos = [], []

    # coarse mesh(cの文字を付加)

    # cname = "f0"
    # cr_min, cr_max, cdel_r = 0.0, 1.4, 0.02
    # cz_min, cz_max, cdel_z = -1.1, 1.1, 0.02

    #cname = 'f1'
    #cr_min, cr_max, cdel_r = 0.0, 1.8, 0.02
    #cz_min, cz_max, cdel_z = -1.8, 1.8, 0.02

    #cname = "f2"
    #cr_min, cr_max, cdel_r = 0.0, 1.4, 0.01
    #cz_min, cz_max, cdel_z = -1.1, 1.1, 0.01
    
    cname = "f3"
    cr_min, cr_max, cdel_r = 0.0, 1.5, 0.02
    cz_min, cz_max, cdel_z = -1.1, 1.1, 0.02    
    
    cnr, cnz = None, None
    cr_pos, cz_pos = [], []

    # root_dir = "c:\\home\\codes\\tokamak_equilibirum\\"
    root_dir = "."

    def __init__(self):

        self.r_pos = np.arange(self.r_min, self.r_max + self.del_r / 2, self.del_r)
        self.nr = int((self.r_max - self.r_min) / self.del_r + 1)

        self.z_pos = np.arange(self.z_min, self.z_max + self.del_z / 2, self.del_z)
        self.nz = int((self.z_max - self.z_min) / self.del_z + 1)

        self.cr_pos = np.arange(self.cr_min, self.cr_max + self.cdel_r / 2, self.cdel_r)
        self.cnr = int((self.cr_max - self.cr_min) / self.cdel_r + 1)

        self.cz_pos = np.arange(self.cz_min, self.cz_max + self.cdel_z / 2, self.cdel_z)
        self.cnz = int((self.cz_max - self.cz_min) / self.cdel_z + 1)

    def __setattr__(self, name, value):
        if name in self.__dict__:
            # 定義されたら例外出す
            raise TypeError(f"Can't rebind const ({name})")
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


# import sys
# sys.modules["equilibrium_global"]=_const()
