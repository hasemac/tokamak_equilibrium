# Tokamak equilibrium code

We will develop a tokamak equilibrium calculation code.

[Equations of magnetics](doc/magnetics_en.md)

[Procedure of equilibrium calculation](doc/equilibrium_en.md)


## Getting started

1. Clone this project using VS code etc.
1. Execute 'equalibrium.ipynb' in the root directory in order from the top.

## How to set calculation conditions
An example of the calculation conditions can be found in the conditions of'equilibrium.ipynb'.

```python:
condition = {
    # TF current
    'cur_tf':50, 
    
    # initial plasma profile
    'cur_ip':{'ip':-50, 'r0':0.60, 'z0':0.0, 'radius':0.3},
    
    # PF currents
    'cur_pf':{'hcult16':0.0,'pf17t12':0.5, 'pf26t18':1.0,'pf4_1ab3_cc2':1.0,'pf35_2':-0.5, },        
    
    # number of coefficients
    'num_dpr':2, # dp/df
    'num_di2':2, # di2/df
    
    'resolution': gl.get_dmat_coarse(),
    'error':[]
    }
```

Calculation conditions are described in python dictionary type.
Namely, 'parameter name':value, etc.

The specifiable PF coil name can be found in '/colis/data_npy/'.

## How to check the calculation result.
You can see what was calculated with '.keys ()'.

```python:
cond.keys()
```
```python:
dict_keys(['cur_tf', 'cur_ip', 'cur_pf', 'num_dpr', 'num_di2', 'resolution', 'error', 'vessel', 'flux_coil', 'jt', 'flux_jt', 'flux', 'ir_ax', 'iz_ax', 'r_ax', 'z_ax', 'conf_div', 'f_axis', 'f_surf', 'domain', 'param_dp', 'param_di2', 'r_rmin', 'z_rmin', 'r_rmax', 'z_rmax', 'r_zmin', 'z_zmin', 'r_zmax', 'z_zmax', 'major_radius', 'minor_radius', 'elongation', 'triangularity', 'volume', 'cross_section', 'flux_normalized', 'diff_pre', 'pressure', 'diff_i2', 'pol_current', 'pressure_vol_average', 'beta_toroidal', 'coef_toroidal_flux', 'safty_factor'])
```
You can check the calculation result with contour map or heat map.

```python:
pl.d_contour(cond['flux'])
```
![flux](doc/flux.png)

```python:
pl.d_heatmap(cond['domain'])
```
![domain](doc/domain.png)

We are accepting questions at any time.