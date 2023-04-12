# How to apply this code to new tokamak

## 1. Determining the device name

Edit "global_variables.py" in root directory, and change the device name of the 1st line of "global_variables.py".  

```python
device_name = "quest"
```

Create directories below under the "device" directory.

```shell
./device/(your_device_name)
./device/(your_device_name)/coils
./device/(your_device_name)/coils/data_csv
```

## 2. Setting of PF coil information

Create setting files and save them in the following location.

```shell
./device/(your_device_name)/coils/data_csv
```

Follow the format below for the setting files.

File name: (PF coil name).csv  
Example file contents:

```shell
x(m),y(m)
1.85,0.492
1.85,-0.492
1.85,0.524
1.85,-0.524
1.85,0.556
1.85,-0.556
1.85,0.588
1.85,-0.588
```

Even if you have coils PF1 and PF7 and normally these two coils are connected in series, create two separate files, "PF1.csv" and "PF7.csv".  
A file called "PF17.csv" is created later in a different way.


## 3. Equilibrium calculation settings

### 1. Creating a parameter file

Create the file below called "parameters.py" in the directory "./device/(your_device_name)".  

```python: parameters.py
class equi_params:
```

Setting will be done by adding variables to the class "equi_params".  

### 2. Poloidal cross section

Equilibrium calculation results are displayed together with poloidal cross-sections including PF coils and vacuum vessel geometry. We will make settings related to this poloidal cross section.  

Poloidal cross sections can be displayed in two ways, namely 'image' or 'lines'.  
One way is to display it as an image file such as png. This method is simple but loses the smoothness of lines when the image is scaled up or down. To display as an image, save an image file such as PNG format in the "./device/(your_device_name)" directory.  
Another way is to construct the cross-section as a collection of lines. This method is tedious to create line data, but the smoothness of lines is not lost when the image is scaled. If you want to draw with lines, create the line-data file in "./device/(your_device_name)" directory.  Please refer to "./device/quest/quest_lines.txt" for the format.  
Drawing with lines is our recommendation, which is drawn smoothly even if you scale it.  

```python
class equi_params:
    
    # image of vacuum vessel and PF coils
    image_type = 'lines' # 'lines' or 'image'
    image_path = "./device/quest/quest_lines.txt"
    #image_path = "./device/quest/quest.png" 
    image_x0 = 0   # [m]: left x coordinate of the image
    image_y0 = 1.8 # [m]: top y coordinate of the image
    image_sizex = 1.8 # [m]: x image size
    image_sizey = 3.6 # [m]: y image size
```

### 3. Vessel

Define the region where the plasma can exist as the vacuum vessel region.  
Define the points in a single stroke.  
Match the first and last points.  

```python
    # vessel points
    # [(x0, y0), (x1, y1), ...., (x0, y0)]
    vessel_points = [(0.2035, 1), (0.996, 1), (1.374, 0.496), 
              (1.374, -0.496), (0.996, -1.0), (0.2035, -1.0), 
              (0.2035, 1.0)]
```

### 4. Fine mesh and coarse mesh

Defines the area to compute. A coarse mesh is created from a fine mesh, so the fine mesh area should be wider and finer than the coarse mesh area. If the magnetic field in the area where the coil exists is also required, set the fine mesh to include that area as well.

Equilibrium calculations are performed based on the coarse mesh. For coarse mesh, set the minimum required area and roughness to shorten the calculation time.

```python
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
```

### 5. Connection between PF coils

It is possible to define a new coil by combining multiple PF coils. The format is as below.  

Case: connecting in the same direction  
Numbers have the same sign.

```python
        'pf17t4':[('pf1t4',1), ('pf7t4', 1)],
```

Case: connecting in the opposite direction  
Numbers have opposite signs.  

```python
        'hcult16':[('hcut16', 1), ('hclt16', -1)],
```

Example of connection:

```python
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
```
