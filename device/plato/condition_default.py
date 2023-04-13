{
    # TF current
    'cur_tf':{'tf': +2.0e+3, 'turn': 96*16,
              },

    # initial plasma profile
    'cur_ip':{'ip':+20.0e+3, 'r0':0.70, 'z0':0.0, 'radius':0.2, 
              #'degree': 2.0
              },

    # PF currents
    'cur_pf':{'D':-0.1e+3,'H':-0.1e+3, },
    
    # number of coefficients
    'num_dpr':1, # dp/df
    'num_di2':1, # di2/df
    
}