{
    # TF current
    'cur_tf':{'tf': +50.0e+3, 'turn': 16, 
    #'rewind': True, # rewind of tf coil
    },
    
    # initial plasma profile
    'cur_ip':{'ip':+100.0e+3, 'r0':0.65, 'z0':0.0, 'radius':0.3, 'degree': 2.0},
    
    # PF currents
    'cur_pf':{'hcult16':0.0,'pf17t12':-1.0e+3, 'pf26t36':-1.0e+3,'pf4_1ab3_cc2':0.0,'pf35_2':0.0, },
    
    # number of coefficients
    'num_dpr':1, # dp/df
    'num_di2':1, # di2/df

    # 'constraints':{
    #     'name1':{'point':(0.3, 0.0), 'pressure':20.0, 'weight':1.0},
    #     'name2':{'point':(0.4, 0.0), 'pressure':30.0, 'weight':1.0},  
    #     'name3':{'point':(0.6, 0.0), 'pressure':40.0, 'weight':1.0},

    #     'flc08':{'point':(0.1985,  0.450), 'flux':0.003, 'weight':1.0},
    #     'f_im0':{'point':(0.1985,  0.0  ), 'flux':0.007, 'weight':1.0},
    #     'flc17':{'point':(0.1985, -0.450), 'flux':0.003, 'weight':1.0},

    #     'name4':{'point':(0.2, 0.4), 'br': 0.01, 'weight':0.0},
    #     'name5':{'point':(0.2, 0.0), 'br': 0.00, 'weight':0.0},  
    #     'name6':{'point':(0.2,-0.4), 'br':-0.01, 'weight':0.0},
    
    #     'name7':{'point':(0.0, 0.4), 'bz':0.036, 'weight':0.0},
    #     'name8':{'point':(0.0, 0.0), 'bz':0.060, 'weight':10.0},  
    #     'name9':{'point':(0.0,-0.4), 'bz':0.036, 'weight':0.0},      
    # },

    # flag to fix magnetic axis at initial plasma profile (r0, z0) 
    #'fix_pos': True,

    # calculate flux (r, z): result is set to 'fl_val'.
    'fl_pos':{'flc8':(0.1985, 0.450), 'f_im':(0.1985, 0.0), 'flc17':(0.1985, -0.450),
              'fls1':(1.374, 0.450), 'fls5':(1.374, 0.0), 'fls9':(1.374, -0.481)},
    # calculate Br(r, z): result is set to 'br_val'
    #'br_pos':{'r1000z0':(1.0, 1.0)},
    # calculate Bz(r, z): result is set to 'bz_val'
    #'bz_pos':{'r0z0':(0.0, 0.0)},
}