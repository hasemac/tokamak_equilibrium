class equi_params:
    
    # image of vacuum vessel and PF coils
    image_type = 'lines' # 'lines' or 'image'
    image_path = "./device/plato/others/plato_lines.txt"
    #image_path = "./device/quest/quest.png" 
    image_x0 = 0   # [m]: left x coordinate of the image
    image_y0 = 0.9 # [m]: top y coordinate of the image
    image_sizex = 1.31 # [m]: x image size
    image_sizey = 1.8 # [m]: y image size
    
    # fine mesh
    r_min, r_max, del_r = 0.0, 1.3, 0.01
    z_min, z_max, del_z = -0.9, 0.9, 0.01
    
    # coarse mesh
    # total area, 10mm pitch
    # cname = "c0" 
    # cr_min, cr_max, cdel_r = 0.0, 1.3, 0.01
    # cz_min, cz_max, cdel_z = -0.9, 0.9, 0.01

    # total area, 20mm pitch, much faster than 'c0'
    cname = "c1" 
    cr_min, cr_max, cdel_r = 0.0, 1.3, 0.02
    cz_min, cz_max, cdel_z = -0.9, 0.9, 0.02

    # limited area, 10mm pitch
    # cname = "c2"
    # cr_min, cr_max, cdel_r = 0.40, 1.05, 0.01
    # cz_min, cz_max, cdel_z = -0.5, 0.5, 0.01
    
    # vessel points
    # [(x0, y0), (x1, y1), ...., (x0, y0)]
    vessel_points = [(0.442, 0.356), (0.531, 0.465), (0.836, 0.465), 
                     (1.006, 0.247), (1.006, -0.247), (0.836, -0.465), 
                     (0.531, -0.465), (0.442, -0.356), (0.442, 0.356)]
    
    # 連結するPFコイルの情報
    connection_pf = {
        'Q':[('QU',1), ('QD', 1)],
        'F2':[('F2U',1), ('F2D', 1)],
        'H':[('HU',1), ('HD', 1)],
        'F1':[('F1U',1), ('F1D', 1)],
        'C':[('CU',1), ('CD', 1)],
        'D':[('DU',1), ('DD', 1)],
        'OH-C':[('OH-CI', 1), ('OH-CO', 1)],
        'OH-D':[('OH-DI', 1), ('OH-DO', 1)],
        'OH-U':[('OH-UI', 1), ('OH-UO', 1)],
        'OH':[('OH-CI', 1), ('OH-CO', 1), ('OH-DI', 1), ('OH-DO', 1), ('OH-UI', 1), ('OH-UO', 1)],             
        }