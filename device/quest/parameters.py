class equi_params:
    
    # image of vacuum vessel and PF coils
    image_type = 'lines' # 'lines' or 'image'
    image_path = "./device/quest/quest.png" 
    image_x0 = 0   # [m]: left x coordinate of the image
    image_y0 = 1.8 # [m]: top y coordinate of the image
    image_sizex = 1.8 # [m]: x image size
    image_sizey = 3.6 # [m]: y image size

    vessel_points = [(0.2035, 1), (0.996, 1), (1.374, 0.496), 
              (1.374, -0.496), (0.996, -1.0), (0.2035, -1.0), 
              (0.2035, 1.0)]
    
    # fine mesh
    r_min, r_max, del_r = 0.0, 1.8, 0.01
    z_min, z_max, del_z = -1.8, 1.8, 0.01
    
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
    
    # 連結するPFコイルの情報
    connection_pf = {
        'pf17t4':[('pf1t4',1), ('pf7t4', 1)],
        'pf17t8':[('pf1t8',1), ('pf7t8', 1)],
        'pf17t12':[('pf1t12',1), ('pf7t12', 1)],
        'pf17t12':[('pf1t12',1), ('pf7t12', 1)],
        'pf26t18':[('pf2t18',1), ('pf6t18', 1)],
        'pf26t36':[('pf2t36',1), ('pf6t36', 1)],
        'pf26t72':[('pf2t72',1), ('pf6t72', 1)],
        'pf35_1':[('pf3_1',1), ('pf5_1', 1)],  
        'pf35_2':[('pf3_2',1), ('pf5_2', 1)],
        'pf35_12':[('pf3_1',1), ('pf3_2',1), ('pf5_1', 1), ('pf5_2',1)],
        'pf4_1ab3_cc1':[('pf41', 1), ('pf42a', 1), ('pf42b', 1), ('pf43', 1), ('cct1', 1)],
        'pf4_1a3_cc1':[('pf41', 1), ('pf42a', 1), ('pf43', 1), ('cct1', 1)],
        'pf4_1ab3_cc2':[('pf41', 1), ('pf42a', 1), ('pf42b', 1), ('pf43', 1), ('cct2', 1)],
        'pf4_1a3_cc2':[('pf41', 1), ('pf42a', 1), ('pf43', 1), ('cct2', 1)],
        'pf4_13':[('pf41', 1), ('pf43', 1)],
        'hcult6':[('hcut6', 1), ('hclt6', -1)],
        'hcult16':[('hcut16', 1), ('hclt16', -1)],
        'pf4_ab_cc2':[('pf42a', 1), ('pf42b', 1), ('cct2', 1)], 
        'tf_rewind':[('tf_rewind_1', -1), ('tf_rewind_2', 1)],
        }