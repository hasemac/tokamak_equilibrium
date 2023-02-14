# Magnetics Calculation

See 'examples/magnetics/magnetics_calculation.ipynb' as an example.  
The magnetic field can be calculated by entering the magnetic field information in the Magnetic class.  
When the equilibrium calculation result is input, the magnetic field in the equilibrium state is calculated.  

```python
import sub.magnetics_cond as smc

# define magnetic fields condition
eqcond = {
    # TF current
    'cur_tf':{'tf': +50.0e+3, 'turn': 16},
    # PF currents
    'cur_pf':{'pf26t36':1.0e+3},
    'resolution': gl.get_dmat_coarse(),
    }

mag = smc.Magnetic(eqcond)

# calculate br, bz, bt and flux with r, z
r, z = 0.6, 0.0
print('Br: ', mag.get_br(r, z))
print('Bz: ', mag.get_bz(r, z))
print('Bt: ', mag.get_bt(r, z))
print('flux: ', mag.get_fl(r, z))
```
