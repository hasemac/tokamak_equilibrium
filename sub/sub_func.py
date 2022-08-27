import numpy as np
from scipy.optimize import curve_fit

def find_extremum_loc_and_val(data_array2d):
    nz, nr = data_array2d.shape

    r = np.array([[e-int(nr/2) for e in range(nr)] for f in range(nz)])
    z = np.array([[f-int(nz/2) for e in range(nr)] for f in range(nz)])
    
    r = r.reshape(-1)
    z = z.reshape(-1)
    dat = data_array2d.reshape(-1)
    
    def func(u, a, b, c, d, e, f):
        x, y = u
        z = a*x**2 + b*x*y + c*y**2 + d*x + e*y + f
        return z

    (a, b, c, d, e, f), _ = curve_fit(func, (r, z), dat)
    
    # calc position of local minimu or local maximum
    dr = (2*c*d-b*e)/(b**2-4*a*c)
    dz = (2*a*e-b*d)/(b**2-4*a*c)
    
    val = (c*d**2 - b*d*e + a*e**2 + b**2*f - 4*a*c*f)/(b**2 - 
    4*a*c)
    return dz, dr, val