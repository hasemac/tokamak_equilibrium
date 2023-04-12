# Explanation of input and output parameters

## Input parameters

| name        | subname      | unit | type    | Necessary | description                                     |
|-------------|--------------|------|---------|-----------|-------------------------------------------------|
| constraints |              |      |         | optional  | constraints for pressure, flux, br, and bz      |
|             | user_defined |      |         |           |                                                 |
| br_pos      |              |      |         | optional  | positions to calculate br                       |
|             | user_defined | m    | tuple   |           |                                                 |
| bz_pos      |              |      |         | optional  | positions to calculate bz                       |
|             | user_defined | m    | tuple   |           |                                                 |
| cur_ip      |              |      |         |           | setting for plasma current                      |
|             | ip           | A    | float   |           | plasma current                                  |
|             | r0           | m    | float   |           | initial major radius                            |
|             | z0           | m    | float   |           | initial z position                              |
|             | radius       | m    | float   |           | initial minor radius                            |
|             | degree       |      | float   | optional  | initial current profile(ex. 2: parabolic)       |
| cur_pf      |              |      |         |           | setting for poloidal coils                      |
|             | PF coil name | A    | float   |           | coil current                                    |
| cur_tf      |              |      |         |           | setting for toroidal coils                      |
|             | tf           |      | float   |           | power supply current of tf                      |
|             | turn         |      | int     |           | turns of toroidal coil                          |
|             | rewind       |      | boolean | optional  | rewinding (True: consider, False: not consider) |
| fl_pos      |              |      |         | optional  | position to calculate flux                      |
|             | user_defined | m    | tuple   |           |                                                 |
| num_dpr     |              |      | int     |           | number of terms in the polynominal for p'       |
| num_di2     |              |      | int     |           | number of terms in the polynominal for ff'      |

## Output parameters

| name                           | subname | unit      | type   | description                                      |
|--------------------------------|---------|-----------|--------|--------------------------------------------------|
| aspect_ratio                   |         |           | float  | aspect ratio                                     |
| axis_ir                        |         |           | int    | r-grid number of magnetic axis                   |
| axis_iz                        |         |           | int    | z-grid number of magnetic axis                   |
| axis_r                         |         | m         | float  | r of magnetic axis                               |
| axis_z                         |         | m         | float  | z of magnetic axis                               |
| b_theta_jt_square              |         |           |        |                                                  |
| bad_step                       |         |           |        |                                                  |
| beta_normalized                |         |           | float  | normalized beta                                  |
| beta_poloidal                  |         |           | float  | poloidal beta                                    |
| beta_toroidal                  |         |           | float  | toroidal beta                                    |
| br                             |         | T, Wb/m^2 | matrix | total br (br_jt + br_coil)                       |
| br_coil                        |         | T, Wb/m^2 | matrix | br due to PF coils                               |
| br_jt                          |         | T, Wb/m^2 | matrix | br due to plasma current                         |
| bz                             |         | T, Wb/m^2 | matrix | total bz (bz_jt + bz_coil)                       |
| bz_coil                        |         | T, Wb/m^2 | matrix | bz due to PF coils                               |
| bz_jt                          |         | T, Wb/m^2 | matrix | bz due to plasma current                         |
| cal_result                     |         |           | int    | calculation result (1: success, -1: failure)     |
| conf_div                       |         |           | int    | plasma configuration (1: divertor, 0: limiter)   |
| cross_section                  |         | m^2       | float  | poloidal cross section                           |
| decay_index_on_axis            |         |           | float  | decay index on axis                              |
| diff_i2                        |         |           |        |                                                  |
| diff_i2_norm                   |         |           |        |                                                  |
| diff_pre                       |         |           |        |                                                  |
| diff_pre_norm                  |         |           |        |                                                  |
| domain                         |         |           | matrix | plasma domain (1:inside, 0:outside)              |
| elongation                     |         |           | float  | elongation of plasma                             |
| error                          |         |           |        |                                                  |
| error_messages                 |         |           |        |                                                  |
| f_axis                         |         | Vsec, Wb  | float  | flux of magnetic axis                            |
| f_surf                         |         | Vsec, Wb  | float  | flux of magnetic surface                         |
| fl_val                         |         | Vsec, Wb  | float  |                                                  |
| flux                           |         | Vsec, Wb  | matrix | total flux (flux_jt + flux_coil)                 |
| flux_coil                      |         | Vsec, Wb  | matrix | magnetic flux due to PF coils                    |
| flux_jt                        |         | Vsec, Wb  | matrix | magnetic flux due to plasma current              |
| flux_normalized                |         | Vsec, Wb  | matrix | normalized flux (0:axis, 1:surface)              |
| inductance_internal            |         | H         | float  | internal inductance, Li=Fi/Ip                    |
| inductance_internal_btheta     |         | H         | float  | internal inductance, Li=<Bth^2>V/(m0 Ip^2)       |
| inductance_internal_normalized |         | H         | float  | normalized internal inductance, li               |
| inductance_self                |         | H         | float  | self inductance (total inductance)               |
| iter                           |         |           |        |                                                  |
| jt                             |         | A/m^2     | matrix | toroidal current density (jt_dp + jt_di2)        |
| jt_di2                         |         | A/m^2     | matrix | toroidal current density due to plasma pressure  |
| jt_dp                          |         | A/m^2     | matrix | toroidal current density due to poloidal current |
| major_radius                   |         | m         | float  | major radius of plasma                           |
| minor_radius                   |         | m         | float  | minor radius of plasma                           |
| param_di2                      |         |           |        |                                                  |
| param_dp                       |         |           |        |                                                  |
| pol_current                    |         |           |        |                                                  |
| pol_current_norm               |         |           |        |                                                  |
| pressure                       |         | Pa        | matrix | plasma pressure                                  |
| pressure_norm                  |         | Pa        | array  | plasma pressure (p[0]: axis, p[-1]: surface)     |
| pressure_vol_average           |         | Pa        | float  | volume-averaged plasma pressure                  |
| pts                            |         |           |        |                                                  |
|                                | r_rmin  | m         | float  | inside r                                         |
|                                | z_rmin  | m         | float  | inside z                                         |
|                                | r_rmax  | m         | float  | outside r                                        |
|                                | z_rmax  | m         | float  | outside z                                        |
|                                | r_zmin  | m         | float  | bottom r                                         |
|                                | z_zmin  | m         | float  | bottom z                                         |
|                                | r_zmax  | m         | float  | top r                                            |
|                                | z_zmax  | m         | float  | top z                                            |
| q_center                       |         |           | float  | safety factor at magnetic axis                   |
| q_edge                         |         |           | float  | safety factor at plasma surface                  |
| safety_factor                  |         |           | matrix | safety factor                                    |
| safety_factor_norm             |         |           | array  | safety factor (q[0]: axis, q[-1]: surface)       |
| stored_energy                  |         | Joul      | float  | stored energy, W=3< p >V                           |
| toroidal_flux                  |         |           |        |                                                  |
| toroidal_flux_diff             |         |           |        |                                                  |
| triangularity                  |         |           | float  | triangularity of plasma                          |
| vessel                         |         |           | matrix | vacuum vessel (1:inside, 0:outside)              |
| volume                         |         | m^3       | float  | plamsa volume                                    |