import numpy as np
from numpy import pi
import os.path as path
import getopt, sys
import json
import os
import importlib
from clusters.default_cluster import DefaultCluster
from clusters.carbonfet import CarbonfetCluster
from clusters.mini import MiniCluster
from clusters.minidox import MinidoxCluster
from clusters.trackball_orbyl import TrackballOrbyl
from clusters.trackball_wilder import TrackballWild
from clusters.trackball_cj import TrackballCJ
from clusters.custom_cluster import CustomCluster
from clusters.trackball_btu import TrackballBTU
from clusters.rename_me import RenameMeCluster


def deg2rad(degrees: float) -> float:
    return degrees * pi / 180


def rad2deg(rad: float) -> float:
    return rad * 180 / pi


debug_exports = False
debug_trace = False


def debugprint(info):
    if debug_trace:
        print(info)

###############################################
# EXTREMELY UGLY BUT FUNCTIONAL BOOTSTRAP
###############################################

## IMPORT DEFAULT CONFIG IN CASE NEW PARAMETERS EXIST


def make_dactyl():

    right_cluster = None
    left_cluster = None

    left_wall_x_offset = 8
    left_wall_x_row_offsets = [
        8, 8, 8, 8, 8, 8
    ]
    left_wall_z_offset = 3
    left_wall_lower_y_offset = 0
    left_wall_lower_z_offset = 0

    symmetry = None
    column_style = None
    save_path = path.join(r"..", "things")

    def cluster(side="right"):
        return right_cluster if side == "right" else left_cluster

    import generate_configuration as cfg
    for item in cfg.shape_config:
        globals()[item] = cfg.shape_config[item]

    data = None

        ## CHECK FOR CONFIG FILE AND WRITE TO ANY VARIABLES IN FILE.
    opts, args = getopt.getopt(sys.argv[1:], "", ["config=", "save_path="])
    for opt, arg in opts:
        if opt in '--config':
            with open(os.path.join(r"..", "configs", arg + '.json'), mode='r') as fid:
                data = json.load(fid)
        elif opt in '--save_path':
            print("save_path set to argument: ", arg)
            save_path = arg

    if data is None:
        print("NO CONFIGURATION SPECIFIED, USING run_config.json")
        with open(os.path.join(r".", 'run_config.json'), mode='r') as fid:
            data = json.load(fid)

    if data["overrides"] not in [None, ""]:
        save_path = path.join(save_path, data["overrides"])
        override_file = path.join(save_path, data["overrides"] + '.json')
        with open(override_file, mode='r') as fid:
            override_data = json.load(fid)
        for item in override_data:
            data[item] = override_data[item]

    for item in data:
        globals()[item] = data[item]

    if save_name not in ['', None]:
        config_name = save_name
    elif overrides is not None:
        config_name = overrides + "_" + str(nrows) + "x" + str(ncols) + "_" + thumb_style

    ENGINE = data["ENGINE"]
    # Really rough setup.  Check for ENGINE, set it not present from configuration.
    try:
        print('Found Current Engine in Config = {}'.format(ENGINE))
    except Exception:
        print('Engine Not Found in Config')
        ENGINE = 'solid'
        # ENGINE = 'cadquery'
        print('Setting Current Engine = {}'.format(ENGINE))

    parts_path = os.path.abspath(path.join(r".", "parts"))

    if save_dir not in ['', None, '.']:
        save_path = save_dir
        print("save_path set to save_dir json setting: ", save_path)
            # parts_path = path.join(r"..", r"..", "src", "parts")
        # parts_path = path.join(r"..", r"..", "src", "parts")

        # parts_path = path.jo

    dir_exists = os.path.isdir(save_path)
    if not dir_exists:
        os.makedirs(save_path, exist_ok=True)

    ###############################################
    # END EXTREMELY UGLY BOOTSTRAP
    ###############################################

    ####################################################
    # HELPER FUNCTIONS TO MERGE CADQUERY AND OPENSCAD
    ####################################################

    if ENGINE == 'cadquery':
        globals().update(importlib.import_module("helpers_cadquery").__dict__)
    else:
        globals().update(importlib.import_module("helpers_solid").__dict__)

    ####################################################
    # END HELPER FUNCTIONS
    ####################################################

    if oled_mount_type is not None and oled_mount_type != "NONE":
        for item in oled_configurations[oled_mount_type]:
            globals()[item] = oled_configurations[oled_mount_type][item]

    if nrows > 5:
        column_style = column_style_gt5

    centerrow = nrows - centerrow_offset

    lastrow = nrows - 1
    cornerrow = lastrow - 1
    lastcol = ncols - 1

    oled_row = nrows - 1
    plate_file = None

    # Derived values
    if plate_style in ['NUB', 'HS_NUB']:
        keyswitch_height = nub_keyswitch_height
        keyswitch_width = nub_keyswitch_width
    elif plate_style in ['UNDERCUT', 'HS_UNDERCUT', 'NOTCH', 'HS_NOTCH']:
        keyswitch_height = undercut_keyswitch_height
        keyswitch_width = undercut_keyswitch_width
    else:
        keyswitch_height = hole_keyswitch_height
        keyswitch_width = hole_keyswitch_width

    if 'HS_' in plate_style:
        symmetry = "asymmetric"
        pname = r"hot_swap_plate"
        if plate_file_name is not None:
            pname = plate_file_name
        plate_file = path.join(parts_path, pname)
        # plate_offset = 0.0 # this overwrote the config variable

    if (trackball_in_wall or ('TRACKBALL' in thumb_style)) and not ball_side == 'both':
        symmetry = "asymmetric"

    mount_width = keyswitch_width + 2 * plate_rim
    mount_height = keyswitch_height + 2 * plate_rim
    mount_thickness = plate_thickness

    if default_1U_cluster and thumb_style == 'DEFAULT':
        double_plate_height = (.7 * sa_double_length - mount_height) / 3
    elif thumb_style == 'DEFAULT':
        double_plate_height = (.95 * sa_double_length - mount_height) / 3
    else:
        double_plate_height = (sa_double_length - mount_height) / 3

    if oled_mount_type is not None and oled_mount_type != "NONE":
        left_wall_x_offset = oled_left_wall_x_offset_override
        if nrows == 4:
            left_wall_x_row_offsets = [22, 22, 22, 22]
        elif nrows == 5:
            left_wall_x_row_offsets = [22, 22, 22, 8, 8]
        elif nrows == 6:
            left_wall_x_row_offsets = [22, 22, 22, 8, 8, 8]
        # left_wall_x_row_offsets = [22 if row > oled_row else 8 for row in range(lastrow)]
        left_wall_z_offset = oled_left_wall_z_offset_override
        left_wall_lower_y_offset = oled_left_wall_lower_y_offset
        left_wall_lower_z_offset = oled_left_wall_lower_z_offset

    cap_top_height = plate_thickness + sa_profile_key_height
    row_radius = ((mount_height + extra_height) / 2) / (np.sin(alpha / 2)) + cap_top_height
    column_radius = (
                            ((mount_width + extra_width) / 2) / (np.sin(beta / 2))
                    ) + cap_top_height
    column_x_delta = -1 - column_radius * np.sin(beta)
    # Is this the main angle?? why does nothing change
    column_base_angle = beta * (centercol - 2)

    teensy_width = 20
    teensy_height = 12
    teensy_length = 33
    teensy2_length = 53
    teensy_pcb_thickness = 2
    teensy_offset_height = 5
    teensy_holder_top_length = 18
    teensy_holder_width = 7 + teensy_pcb_thickness
    teensy_holder_height = 6 + teensy_width

    # save_path = path.join("..", "things", save_dir)
    if not path.isdir(save_path):
        os.mkdir(save_path)


    def column_offset(column: int) -> list:
        result = column_offsets[column]
        # if (pinky_1_5U and column == lastcol):
        #     result[0] = result[0] + 1
        return result


    # column_style='fixed'


    def single_plate(cylinder_segments=100, side="right"):
        if plate_style in ['NUB', 'HS_NUB']:
            tb_border = (mount_height - keyswitch_height) / 2
            top_wall = box(mount_width, tb_border, plate_thickness)
            top_wall = translate(top_wall, (0, (tb_border / 2) + (keyswitch_height / 2), plate_thickness / 2))

            lr_border = (mount_width - keyswitch_width) / 2
            left_wall = box(lr_border, mount_height, plate_thickness)
            left_wall = translate(left_wall, ((lr_border / 2) + (keyswitch_width / 2), 0, plate_thickness / 2))

            side_nub = cylinder(radius=1, height=2.75)
            side_nub = rotate(side_nub, (90, 0, 0))
            side_nub = translate(side_nub, (keyswitch_width / 2, 0, 1))

            nub_cube = box(1.5, 2.75, plate_thickness)
            nub_cube = translate(nub_cube, ((1.5 / 2) + (keyswitch_width / 2), 0, plate_thickness / 2))

            side_nub2 = tess_hull(shapes=(side_nub, nub_cube))
            side_nub2 = union([side_nub2, side_nub, nub_cube])

            plate_half1 = union([top_wall, left_wall, side_nub2])
            plate_half2 = plate_half1
            plate_half2 = mirror(plate_half2, 'XZ')
            plate_half2 = mirror(plate_half2, 'YZ')

            plate = union([plate_half1, plate_half2])

        else:  # 'HOLE' or default, square cutout for non-nub designs.
            plate = box(mount_width, mount_height, mount_thickness)
            plate = translate(plate, (0.0, 0.0, mount_thickness / 2.0))

            shape_cut = box(keyswitch_width, keyswitch_height, mount_thickness * 2 + .02)
            shape_cut = translate(shape_cut, (0.0, 0.0, mount_thickness - .01))

            plate = difference(plate, [shape_cut])

        if plate_file is not None:
            socket = import_file(plate_file)
            socket = translate(socket, [0, 0, plate_thickness + plate_offset])
            plate = union([plate, socket])

        if plate_style in ['UNDERCUT', 'HS_UNDERCUT', 'NOTCH', 'HS_NOTCH']:
            if plate_style in ['UNDERCUT', 'HS_UNDERCUT']:
                undercut = box(
                    keyswitch_width + 2 * clip_undercut,
                    keyswitch_height + 2 * clip_undercut,
                    mount_thickness
                )

            if plate_style in ['NOTCH', 'HS_NOTCH']:
                undercut = box(
                    notch_width,
                    keyswitch_height + 2 * clip_undercut,
                    mount_thickness
                )
                undercut = union([undercut,
                                  box(
                                      keyswitch_width + 2 * clip_undercut,
                                      notch_width,
                                      mount_thickness
                                  )
                                  ])

            undercut = translate(undercut, (0.0, 0.0, -clip_thickness + mount_thickness / 2.0))

            if ENGINE == 'cadquery' and undercut_transition > 0:
                undercut = undercut.faces("+Z").chamfer(undercut_transition, clip_undercut)

            plate = difference(plate, [undercut])

        # if plate_file is not None:
        #     socket = import_file(plate_file)
        #     socket = translate(socket, [0, 0, plate_thickness + plate_offset])
        #     plate = union([plate, socket])

        if plate_holes:
            half_width = plate_holes_width / 2.
            half_height = plate_holes_height / 2.
            x_off = plate_holes_xy_offset[0]
            y_off = plate_holes_xy_offset[1]
            holes = [
                translate(
                    cylinder(radius=plate_holes_diameter / 2, height=plate_holes_depth + .01),
                    (x_off + half_width, y_off + half_height, plate_holes_depth / 2 - .01)
                ),
                translate(
                    cylinder(radius=plate_holes_diameter / 2, height=plate_holes_depth + .01),
                    (x_off - half_width, y_off + half_height, plate_holes_depth / 2 - .01)
                ),
                translate(
                    cylinder(radius=plate_holes_diameter / 2, height=plate_holes_depth + .01),
                    (x_off - half_width, y_off - half_height, plate_holes_depth / 2 - .01)
                ),
                translate(
                    cylinder(radius=plate_holes_diameter / 2, height=plate_holes_depth + .01),
                    (x_off + half_width, y_off - half_height, plate_holes_depth / 2 - .01)
                ),
            ]
            plate = difference(plate, holes)

        if side == "left":
            plate = mirror(plate, 'YZ')

        return plate


    def trackball_cutout(segments=100, side="right"):
        shape = cylinder(trackball_hole_diameter / 2, trackball_hole_height)
        return shape


    def trackball_socket(btus=False,segments=100, side="right"):
        # shape = sphere(ball_diameter / 2)
        # cyl = cylinder(ball_diameter / 2 + 4, 20)
        # cyl = translate(cyl, (0, 0, -8))
        # shape = union([shape, cyl])

        tb_file = path.join(parts_path, r"trackball_socket_body_34mm")
        tbcut_file = path.join(parts_path, r"trackball_socket_cutter_34mm")

        if btus:
            tb_file = path.join(parts_path, r"btu_trackball_socket_square")
            tbcut_file = path.join(parts_path, r"trackball_socket_w_btus_cutter")

        sens_file = path.join(parts_path, r"trackball_sensor_mount")
        senscut_file = path.join(parts_path, r"trackball_sensor_cutter")

        # shape = import_file(tb_file)
        # # shape = difference(shape, [import_file(senscut_file)])
        # # shape = union([shape, import_file(sens_file)])
        # cutter = import_file(tbcut_file)

        shape = import_file(tb_file)
        sensor = import_file(sens_file)
        cutter = import_file(tbcut_file)
        cutter = union([cutter, import_file(senscut_file)])

        # return shape, cutter
        return shape, cutter, sensor


    def trackball_ball(segments=100, side="right"):
        shape = sphere(ball_diameter / 2)
        return shape


    ################
    ## SA Keycaps ##
    ################


    def sa_cap(Usize=1):
        # MODIFIED TO NOT HAVE THE ROTATION.  NEEDS ROTATION DURING ASSEMBLY
        # sa_length = 18.25

        if Usize == 1:
            bl2 = 18.5 / 2
            bw2 = 18.5 / 2
            m = 17 / 2
            pl2 = 6
            pw2 = 6

        elif Usize == 2:
            bl2 = sa_length
            bw2 = sa_length / 2
            m = 0
            pl2 = 16
            pw2 = 6

        elif Usize == 1.5:
            bl2 = sa_length / 2
            bw2 = 27.94 / 2
            m = 0
            pl2 = 6
            pw2 = 11

        elif Usize == 1.25:  # todo
            bl2 = sa_length / 2
            bw2 = 22.64 / 2
            m = 0
            pl2 = 16
            pw2 = 11

        k1 = polyline([(bw2, bl2), (bw2, -bl2), (-bw2, -bl2), (-bw2, bl2), (bw2, bl2)])
        k1 = extrude_poly(outer_poly=k1, height=0.1)
        k1 = translate(k1, (0, 0, 0.05))
        k2 = polyline([(pw2, pl2), (pw2, -pl2), (-pw2, -pl2), (-pw2, pl2), (pw2, pl2)])
        k2 = extrude_poly(outer_poly=k2, height=0.1)
        k2 = translate(k2, (0, 0, 12.0))
        if m > 0:
            m1 = polyline([(m, m), (m, -m), (-m, -m), (-m, m), (m, m)])
            m1 = extrude_poly(outer_poly=m1, height=0.1)
            m1 = translate(m1, (0, 0, 6.0))
            key_cap = hull_from_shapes((k1, k2, m1))
        else:
            key_cap = hull_from_shapes((k1, k2))

        key_cap = translate(key_cap, (0, 0, 5 + plate_thickness))

        if show_pcbs:
            key_cap = add([key_cap, key_pcb()])

        return key_cap


    def key_pcb():
        shape = box(pcb_width, pcb_height, pcb_thickness)
        shape = translate(shape, (0, 0, -pcb_thickness / 2))
        hole = cylinder(pcb_hole_diameter / 2, pcb_thickness + .2)
        hole = translate(hole, (0, 0, -(pcb_thickness + .1) / 2))
        holes = [
            translate(hole, (pcb_hole_pattern_width / 2, pcb_hole_pattern_height / 2, 0)),
            translate(hole, (-pcb_hole_pattern_width / 2, pcb_hole_pattern_height / 2, 0)),
            translate(hole, (-pcb_hole_pattern_width / 2, -pcb_hole_pattern_height / 2, 0)),
            translate(hole, (pcb_hole_pattern_width / 2, -pcb_hole_pattern_height / 2, 0)),
        ]
        shape = difference(shape, holes)

        return shape


    #########################
    ## Placement Functions ##
    #########################


    def rotate_around_x(position, angle):
        # debugprint('rotate_around_x()')
        t_matrix = np.array(
            [
                [1, 0, 0],
                [0, np.cos(angle), -np.sin(angle)],
                [0, np.sin(angle), np.cos(angle)],
            ]
        )
        return np.matmul(t_matrix, position)


    def rotate_around_y(position, angle):
        # debugprint('rotate_around_y()')
        t_matrix = np.array(
            [
                [np.cos(angle), 0, np.sin(angle)],
                [0, 1, 0],
                [-np.sin(angle), 0, np.cos(angle)],
            ]
        )
        return np.matmul(t_matrix, position)


    def apply_key_geometry(
            shape,
            translate_fn,
            rotate_x_fn,
            rotate_y_fn,
            column,
            row,
            column_style=column_style,
    ):
        debugprint('apply_key_geometry()')

        column_angle = beta * (centercol - column)

        column_x_delta_actual = column_x_delta
        if (pinky_1_5U and column == lastcol):
            if row >= first_1_5U_row and row <= last_1_5U_row:
                column_x_delta_actual = column_x_delta - 1.5
                column_angle = beta * (centercol - column - 0.27)

        # if column_style == "orthographic":

        #     column_z_delta = column_radius * (1 - np.cos(column_angle))
        #     shape = translate_fn(shape, [0, 0, -row_radius])
        #     shape = rotate_x_fn(shape, alpha * (centerrow - row))
        #     shape = translate_fn(shape, [0, 0, row_radius])
        #     shape = rotate_y_fn(shape, column_angle)
        #     shape = translate_fn(
        #         shape, [-(column - centercol) * column_x_delta_actual, 0, column_z_delta]
        #     )
        #     shape = translate_fn(shape, column_offset(column))

        # elif column_style == "fixed":
        #     shape = rotate_y_fn(shape, fixed_angles[column])
        #     shape = translate_fn(shape, [fixed_x[column], 0, fixed_z[column]])
        #     shape = translate_fn(shape, [0, 0, -(row_radius + fixed_z[column])])
        #     shape = rotate_x_fn(shape, alpha * (centerrow - row))
        #     shape = translate_fn(shape, [0, 0, row_radius + fixed_z[column]])
        #     shape = rotate_y_fn(shape, fixed_tenting)
        #     shape = translate_fn(shape, [0, column_offset(column)[1], 0])

        # else:

        # This is the only 'column_style' that is used regardless of the setting
        shape = translate_fn(shape, [0, 0, -row_radius])
        shape = rotate_x_fn(shape, alpha * (centerrow - row) + x_rotation_offset)
        shape = translate_fn(shape, [0, 0, row_radius])
        shape = translate_fn(shape, [0, 0, -column_radius])
        shape = rotate_y_fn(shape, column_angle)
        shape = translate_fn(shape, [0, 0, column_radius])
        shape = translate_fn(shape, column_offset(column))

        shape = rotate_y_fn(shape, tenting_angle)
        shape = translate_fn(shape, [0, 0, keyboard_z_offset])

        return shape


    def valid_key(column, row):
        if (full_last_rows):
            return (not (column in [0, 1])) or (not row == lastrow)

        return (column in [2, 3]) or (not row == lastrow)


    def x_rot(shape, angle):
        # debugprint('x_rot()')
        return rotate(shape, [rad2deg(angle), 0, 0])


    def y_rot(shape, angle):
        # debugprint('y_rot()')
        return rotate(shape, [0, rad2deg(angle), 0])


    def key_place(shape, column, row):
        debugprint('key_place()')
        return apply_key_geometry(shape, translate, x_rot, y_rot, column, row)


    def add_translate(shape, xyz):
        debugprint('add_translate()')
        vals = []
        for i in range(len(shape)):
            vals.append(shape[i] + xyz[i])
        return vals


    def key_position(position, column, row):
        debugprint('key_position()')
        return apply_key_geometry(
            position, add_translate, rotate_around_x, rotate_around_y, column, row
        )


    def key_holes(side="right"):
        debugprint('key_holes()')
        # hole = single_plate()
        holes = []
        for column in range(ncols):
            for row in range(nrows):
                if valid_key(column, row):
                    holes.append(key_place(single_plate(side=side), column, row))

        shape = union(holes)

        return shape


    def caps():
        caps = None
        for column in range(ncols):
            size = 1
            if pinky_1_5U and column == lastcol:
                if row >= first_1_5U_row and row <= last_1_5U_row:
                    size = 1.5
            for row in range(nrows):
                if valid_key(column, row):
                    if caps is None:
                        caps = key_place(sa_cap(size), column, row)
                    else:
                        caps = add([caps, key_place(sa_cap(size), column, row)])

        return caps


    ####################
    ## Web Connectors ##
    ####################


    def web_post():
        debugprint('web_post()')
        post = box(post_size, post_size, web_thickness)
        post = translate(post, (0, 0, plate_thickness - (web_thickness / 2)))
        return post


    def web_post_tr(wide=False):
        if wide:
            w_divide = 1.2
        else:
            w_divide = 2.0

        return translate(web_post(), ((mount_width / w_divide) - post_adj, (mount_height / 2) - post_adj, 0))


    def web_post_tl(wide=False):
        if wide:
            w_divide = 1.2
        else:
            w_divide = 2.0
        return translate(web_post(), (-(mount_width / w_divide) + post_adj, (mount_height / 2) - post_adj, 0))


    def web_post_bl(wide=False):
        if wide:
            w_divide = 1.2
        else:
            w_divide = 2.0
        return translate(web_post(), (-(mount_width / w_divide) + post_adj, -(mount_height / 2) + post_adj, 0))


    def web_post_br(wide=False):
        if wide:
            w_divide = 1.2
        else:
            w_divide = 2.0
        return translate(web_post(), ((mount_width / w_divide) - post_adj, -(mount_height / 2) + post_adj, 0))


    def get_torow(column):
        torow = lastrow
        if full_last_rows:
            torow = lastrow + 1
        if column in [0, 1]:
            torow = lastrow
        return torow


    def connectors():
        debugprint('connectors()')
        hulls = []
        for column in range(ncols - 1):
            torow = get_torow(column)
            for row in range(torow):  # need to consider last_row?
                # for row in range(nrows):  # need to consider last_row?
                places = []
                places.append(key_place(web_post_tl(), column + 1, row))
                places.append(key_place(web_post_tr(), column, row))
                places.append(key_place(web_post_bl(), column + 1, row))
                places.append(key_place(web_post_br(), column, row))
                hulls.append(triangle_hulls(places))

        for column in range(ncols):
            torow = get_torow(column)
            # for row in range(nrows-1):
            for row in range(torow - 1):
                places = []
                places.append(key_place(web_post_bl(), column, row))
                places.append(key_place(web_post_br(), column, row))
                places.append(key_place(web_post_tl(), column, row + 1))
                places.append(key_place(web_post_tr(), column, row + 1))
                hulls.append(triangle_hulls(places))

        for column in range(ncols - 1):
            torow = get_torow(column)
            # for row in range(nrows-1):  # need to consider last_row?
            for row in range(torow - 1):  # need to consider last_row?
                places = []
                places.append(key_place(web_post_br(), column, row))
                places.append(key_place(web_post_tr(), column, row + 1))
                places.append(key_place(web_post_bl(), column + 1, row))
                places.append(key_place(web_post_tl(), column + 1, row + 1))
                hulls.append(triangle_hulls(places))

        return union(hulls)


    ############
    ## Thumbs ##
    ############


    def adjustable_plate_size(Usize=1.5):
        return (Usize * sa_length - mount_height) / 2


    def adjustable_plate_half(Usize=1.5):
        debugprint('double_plate()')
        adjustable_plate_height = adjustable_plate_size(Usize)
        top_plate = box(mount_width, adjustable_plate_height, web_thickness)
        top_plate = translate(top_plate,
                              [0, (adjustable_plate_height + mount_height) / 2, plate_thickness - (web_thickness / 2)]
                              )
        return top_plate


    def adjustable_plate(Usize=1.5):
        debugprint('double_plate()')
        top_plate = adjustable_plate_half(Usize)
        return union((top_plate, mirror(top_plate, 'XZ')))


    def double_plate_half():
        debugprint('double_plate()')
        top_plate = box(mount_width, double_plate_height, web_thickness)
        top_plate = translate(top_plate,
                              [0, (double_plate_height + mount_height) / 2, plate_thickness - (web_thickness / 2)]
                              )
        return top_plate


    def double_plate():
        debugprint('double_plate()')
        top_plate = double_plate_half()
        return union((top_plate, mirror(top_plate, 'XZ')))


    ############################
    # MINI THUMB CLUSTER
    ############################


    ############################
    # MINIDOX (3-key) THUMB CLUSTER
    ############################


    ############################
    # Carbonfet THUMB CLUSTER
    ############################


    ############################
    # Wilder Trackball (Ball + 4-key) THUMB CLUSTER
    ############################


    ############################
    # CJ TRACKBALL THUMB CLUSTER
    ############################

    # single_plate = the switch shape


    ##########
    ## Case ##
    ##########

    def left_key_position(row, direction, low_corner=False, side='right'):
        debugprint("left_key_position()")
        pos = np.array(
            key_position([-mount_width * 0.5, direction * mount_height * 0.5, 0], 0, row)
        )
        if trackball_in_wall and (side == ball_side or ball_side == 'both'):

            if low_corner:
                y_offset = tbiw_left_wall_lower_y_offset
                z_offset = tbiw_left_wall_lower_z_offset
            else:
                y_offset = 0.0
                z_offset = 0.0

            return list(pos - np.array([
                tbiw_left_wall_x_offset_override,
                -y_offset,
                tbiw_left_wall_z_offset_override + z_offset
            ]))

        if low_corner:
            y_offset = left_wall_lower_y_offset
            z_offset = left_wall_lower_z_offset
        else:
            y_offset = 0.0
            z_offset = 0.0

        return list(pos - np.array([left_wall_x_row_offsets[row], -y_offset, left_wall_z_offset + z_offset]))


    def left_key_place(shape, row, direction, low_corner=False, side='right'):
        debugprint("left_key_place()")
        pos = left_key_position(row, direction, low_corner=low_corner, side=side)
        return translate(shape, pos)


    def wall_locate1(dx, dy):
        debugprint("wall_locate1()")
        return [dx * wall_thickness, dy * wall_thickness, -1]


    def wall_locate2(dx, dy):
        debugprint("wall_locate2()")
        return [dx * wall_x_offset, dy * wall_y_offset, -wall_z_offset]


    def wall_locate3(dx, dy, back=False):
        debugprint("wall_locate3()")
        if back:
            return [
                dx * (wall_x_offset + wall_base_x_thickness),
                dy * (wall_y_offset + wall_base_back_thickness),
                -wall_z_offset,
            ]
        else:
            return [
                dx * (wall_x_offset + wall_base_x_thickness),
                dy * (wall_y_offset + wall_base_y_thickness),
                -wall_z_offset,
            ]
        # return [
        #     dx * (wall_xy_offset + wall_thickness),
        #     dy * (wall_xy_offset + wall_thickness),
        #     -wall_z_offset,
        # ]


    def wall_brace(place1, dx1, dy1, post1, place2, dx2, dy2, post2, back=False):
        debugprint("wall_brace()")
        hulls = []

        hulls.append(place1(post1))
        hulls.append(place1(translate(post1, wall_locate1(dx1, dy1))))
        hulls.append(place1(translate(post1, wall_locate2(dx1, dy1))))
        hulls.append(place1(translate(post1, wall_locate3(dx1, dy1, back))))

        hulls.append(place2(post2))
        hulls.append(place2(translate(post2, wall_locate1(dx2, dy2))))
        hulls.append(place2(translate(post2, wall_locate1(dx2, dy2))))
        hulls.append(place2(translate(post2, wall_locate2(dx2, dy2))))
        hulls.append(place2(translate(post2, wall_locate3(dx2, dy2, back))))
        shape1 = hull_from_shapes(hulls)

        hulls = []
        hulls.append(place1(translate(post1, wall_locate2(dx1, dy1))))
        hulls.append(place1(translate(post1, wall_locate3(dx1, dy1, back))))
        hulls.append(place2(translate(post2, wall_locate2(dx2, dy2))))
        hulls.append(place2(translate(post2, wall_locate3(dx2, dy2, back))))
        shape2 = bottom_hull(hulls)

        return union([shape1, shape2])
        # return shape1


    def key_wall_brace(x1, y1, dx1, dy1, post1, x2, y2, dx2, dy2, post2, back=False):
        debugprint("key_wall_brace()")
        return wall_brace(
            (lambda shape: key_place(shape, x1, y1)),
            dx1,
            dy1,
            post1,
            (lambda shape: key_place(shape, x2, y2)),
            dx2,
            dy2,
            post2,
            back
        )


    def back_wall():
        print("back_wall()")
        x = 0
        shape = union([key_wall_brace(x, 0, 0, 1, web_post_tl(), x, 0, 0, 1, web_post_tr(), back=True)])
        for i in range(ncols - 1):
            x = i + 1
            shape = union([shape, key_wall_brace(x, 0, 0, 1, web_post_tl(), x, 0, 0, 1, web_post_tr(), back=True)])
            shape = union([shape, key_wall_brace(
                x, 0, 0, 1, web_post_tl(), x - 1, 0, 0, 1, web_post_tr(), back=True
            )])
        shape = union([shape, key_wall_brace(
            lastcol, 0, 0, 1, web_post_tr(), lastcol, 0, 1, 0, web_post_tr(), back=True
        )])
        return shape


    def right_wall():
        print("right_wall()")

        torow = lastrow - 1

        if (full_last_rows):
            torow = lastrow

        tocol = lastcol

        y = 0
        shape = union([
            key_wall_brace(
                tocol, y, 1, 0, web_post_tr(), tocol, y, 1, 0, web_post_br()
            )
        ])

        for i in range(torow):
            y = i + 1
            shape = union([shape, key_wall_brace(
                tocol, y - 1, 1, 0, web_post_br(), tocol, y, 1, 0, web_post_tr()
            )])

            shape = union([shape, key_wall_brace(
                tocol, y, 1, 0, web_post_tr(), tocol, y, 1, 0, web_post_br()
            )])
            # STRANGE PARTIAL OFFSET

        shape = union([
            shape,
            key_wall_brace(lastcol, torow, 0, -1, web_post_br(), lastcol, torow, 1, 0, web_post_br())
        ])
        return shape


    def left_wall(side='right'):
        print('left_wall()')
        shape = union([wall_brace(
            (lambda sh: key_place(sh, 0, 0)), 0, 1, web_post_tl(),
            (lambda sh: left_key_place(sh, 0, 1, side=side)), 0, 1, web_post(),
        )])

        shape = union([shape, wall_brace(
            (lambda sh: left_key_place(sh, 0, 1, side=side)), 0, 1, web_post(),
            (lambda sh: left_key_place(sh, 0, 1, side=side)), -1, 0, web_post(),
        )])

        for i in range(lastrow):
            # TODO add as run_config setting
            # Skip last row's walls to make space for the thumb cluster

            if skip_last_rows_wall and i == lastrow - 1 :
                print(f'skipping {i}, {lastrow}')
                continue
            y = i
            low = (y == (lastrow - 1))
            temp_shape1 = wall_brace(
                (lambda sh: left_key_place(sh, y, 1, side=side)), -1, 0, web_post(),
                (lambda sh: left_key_place(sh, y, -1, low_corner=low, side=side)), -1, 0, web_post(),
            )
            temp_shape2 = hull_from_shapes((
                key_place(web_post_tl(), 0, y),
                key_place(web_post_bl(), 0, y),
                left_key_place(web_post(), y, 1, side=side),
                left_key_place(web_post(), y, -1, low_corner=low, side=side),
            ))
            shape = union([shape, temp_shape1])
            shape = union([shape, temp_shape2])

        for i in range(lastrow - 1):
            y = i + 1
            low = (y == (lastrow - 1))
            temp_shape1 = wall_brace(
                (lambda sh: left_key_place(sh, y - 1, -1, side=side)), -1, 0, web_post(),
                (lambda sh: left_key_place(sh, y, 1, side=side)), -1, 0, web_post(),
            )
            temp_shape2 = hull_from_shapes((
                key_place(web_post_tl(), 0, y),
                key_place(web_post_bl(), 0, y - 1),
                left_key_place(web_post(), y, 1, side=side),
                left_key_place(web_post(), y - 1, -1, side=side),
                left_key_place(web_post(), y - 1, -1, side=side),
            ))
            shape = union([shape, temp_shape1])
            shape = union([shape, temp_shape2])

        return shape


    def front_wall():
        print('front_wall()')

        torow = lastrow - 1
        if (full_last_rows):
            torow = lastrow

        shape = union([
            key_wall_brace(
                lastcol, 0, 0, 1, web_post_tr(), lastcol, 0, 1, 0, web_post_tr()
            )
        ])
        shape = union([shape, key_wall_brace(
            3, lastrow, 0, -1, web_post_bl(), 3, lastrow, 0.5, -1, web_post_br()
        )])
        shape = union([shape, key_wall_brace(
            3, lastrow, 0.5, -1, web_post_br(), 4, torow, 1, -1, web_post_bl()
        )])
        for i in range(ncols - 4):
            x = i + 4
            shape = union([shape, key_wall_brace(
                x, torow, 0, -1, web_post_bl(), x, torow, 0, -1, web_post_br()
            )])
        for i in range(ncols - 5):
            x = i + 5
            shape = union([shape, key_wall_brace(
                x, torow, 0, -1, web_post_bl(), x - 1, torow, 0, -1, web_post_br()
            )])

        return shape


    def case_walls(side='right'):
        print('case_walls()')
        return (
            union([
                back_wall(),
                left_wall(side=side),
                right_wall(),
                front_wall(),
                cluster(side=side).walls(side=side),
                cluster(side=side).connection(side=side),
            ])
        )


    rj9_start = list(
        np.array([0, -3, 0])
        + np.array(
            key_position(
                list(np.array(wall_locate3(0, 1)) + np.array([0, (mount_height / 2), 0])),
                0,
                0,
            )
        )
    )

    rj9_position = (rj9_start[0], rj9_start[1], 11)


    def rj9_cube():
        debugprint('rj9_cube()')
        shape = box(14.78, 13, 22.38)

        return shape


    def rj9_space():
        debugprint('rj9_space()')
        return translate(rj9_cube(), rj9_position)


    def rj9_holder():
        print('rj9_holder()')
        shape = union([translate(box(10.78, 9, 18.38), (0, 2, 0)), translate(box(10.78, 13, 5), (0, 0, 5))])
        shape = difference(rj9_cube(), [shape])
        shape = translate(shape, rj9_position)

        return shape


    usb_holder_position = key_position(
        list(np.array(wall_locate2(0, 1)) + np.array([0, (mount_height / 2), 0])), 1, 0
    )
    usb_holder_size = [6.5, 10.0, 13.6]
    usb_holder_thickness = 4


    def usb_holder():
        print('usb_holder()')
        shape = box(
            usb_holder_size[0] + usb_holder_thickness,
            usb_holder_size[1],
            usb_holder_size[2] + usb_holder_thickness,
        )
        shape = translate(shape,
                          (
                              usb_holder_position[0],
                              usb_holder_position[1],
                              (usb_holder_size[2] + usb_holder_thickness) / 2,
                          )
                          )
        return shape


    def usb_holder_hole():
        debugprint('usb_holder_hole()')
        shape = box(*usb_holder_size)
        shape = translate(shape,
                          (
                              usb_holder_position[0],
                              usb_holder_position[1],
                              (usb_holder_size[2] + usb_holder_thickness) / 2,
                          )
                          )
        return shape


    external_start = list(
        # np.array([0, -3, 0])
        np.array([external_holder_width / 2, 0, 0])
        + np.array(
            key_position(
                list(np.array(wall_locate3(0, 1)) + np.array([0, (mount_height / 2), 0])),
                0,
                0,
            )
        )
    )


    def external_mount_hole():
        print('external_mount_hole()')
        shape = box(external_holder_width, 20.0, external_holder_height + .1)
        undercut = box(external_holder_width + 8, 10.0, external_holder_height + 8 + .1)
        shape = union([shape, translate(undercut, (0, -5, 0))])

        shape = translate(shape,
                          (
                              external_start[0] + external_holder_xoffset,
                              external_start[1] + external_holder_yoffset,
                              external_holder_height / 2 - .05,
                          )
                          )
        return shape


    def generate_trackball(pos, rot, cluster):
        tb_t_offset = tb_socket_translation_offset
        tb_r_offset = tb_socket_rotation_offset

        if cluster is not None and cluster.has_btus():
            tb_t_offset = tb_btu_socket_translation_offset
            tb_r_offset = tb_btu_socket_rotation_offset

        precut = trackball_cutout()
        precut = rotate(precut, tb_r_offset)
        precut = translate(precut, tb_t_offset)
        precut = rotate(precut, rot)
        precut = translate(precut, pos)

        shape, cutout, sensor = trackball_socket(btus=cluster.has_btus())

        shape = rotate(shape, tb_r_offset)
        shape = translate(shape, tb_t_offset)
        shape = rotate(shape, rot)
        shape = translate(shape, pos)

        if cluster is not None:
            shape = cluster.get_extras(shape, pos)

        cutout = rotate(cutout, tb_r_offset)
        cutout = translate(cutout, tb_t_offset)
        # cutout = rotate(cutout, tb_sensor_translation_offset)
        # cutout = translate(cutout, tb_sensor_rotation_offset)
        cutout = rotate(cutout, rot)
        cutout = translate(cutout, pos)

        # Small adjustment due to line to line surface / minute numerical error issues
        # Creates small overlap to assist engines in union function later
        sensor = rotate(sensor, tb_r_offset)
        sensor = translate(sensor, tb_t_offset)
        # sensor = rotate(sensor, tb_sensor_translation_offset)
        # sensor = translate(sensor, tb_sensor_rotation_offset)
        sensor = translate(sensor, (0, 0, .005))
        sensor = rotate(sensor, rot)
        sensor = translate(sensor, pos)

        ball = trackball_ball()
        ball = rotate(ball, tb_r_offset)
        ball = translate(ball, tb_t_offset)
        ball = rotate(ball, rot)
        ball = translate(ball, pos)

        # return precut, shape, cutout, ball
        return precut, shape, cutout, sensor, ball


    def generate_trackball_in_cluster(cluster):
        pos, rot = cluster.position_rotation() if ball_side != "left" else left_cluster.position_rotation()
        return generate_trackball(pos, rot, cluster)


    def tbiw_position_rotation():
        base_pt1 = key_position(
            list(np.array([-mount_width / 2, 0, 0]) + np.array([0, (mount_height / 2), 0])),
            0, cornerrow - tbiw_ball_center_row - 1
        )
        base_pt2 = key_position(
            list(np.array([-mount_width / 2, 0, 0]) + np.array([0, (mount_height / 2), 0])),
            0, cornerrow - tbiw_ball_center_row + 1
        )
        base_pt0 = key_position(
            list(np.array([-mount_width / 2, 0, 0]) + np.array([0, (mount_height / 2), 0])),
            0, cornerrow - tbiw_ball_center_row
        )

        left_wall_x_offset = tbiw_left_wall_x_offset_override

        tbiw_mount_location_xyz = (
                (np.array(base_pt1) + np.array(base_pt2)) / 2.
                + np.array(((-left_wall_x_offset / 2), 0, 0))
                + np.array(tbiw_translational_offset)
        )

        # tbiw_mount_location_xyz[2] = (oled_translation_offset[2] + base_pt0[2])/2

        angle_x = np.arctan2(base_pt1[2] - base_pt2[2], base_pt1[1] - base_pt2[1])
        angle_z = np.arctan2(base_pt1[0] - base_pt2[0], base_pt1[1] - base_pt2[1])
        tbiw_mount_rotation_xyz = (rad2deg(angle_x), 0, rad2deg(angle_z)) + np.array(tbiw_rotation_offset)

        return tbiw_mount_location_xyz, tbiw_mount_rotation_xyz


    def generate_trackball_in_wall():
        pos, rot = tbiw_position_rotation()
        return generate_trackball(pos, rot, None)


    def oled_position_rotation(side='right'):
        _oled_center_row = None
        if trackball_in_wall and (side == ball_side or ball_side == 'both'):
            _oled_center_row = tbiw_oled_center_row
            _oled_translation_offset = tbiw_oled_translation_offset
            _oled_rotation_offset = tbiw_oled_rotation_offset

        elif oled_center_row is not None:
            _oled_center_row = oled_center_row
            _oled_translation_offset = oled_translation_offset
            _oled_rotation_offset = oled_rotation_offset

        if _oled_center_row is not None:
            base_pt1 = key_position(
                list(np.array([-mount_width / 2, 0, 0]) + np.array([0, (mount_height / 2), 0])), 0, _oled_center_row - 1
            )
            base_pt2 = key_position(
                list(np.array([-mount_width / 2, 0, 0]) + np.array([0, (mount_height / 2), 0])), 0, _oled_center_row + 1
            )
            base_pt0 = key_position(
                list(np.array([-mount_width / 2, 0, 0]) + np.array([0, (mount_height / 2), 0])), 0, _oled_center_row
            )

            if trackball_in_wall and (side == ball_side or ball_side == 'both'):
                _left_wall_x_offset = tbiw_left_wall_x_offset_override
            else:
                _left_wall_x_offset = left_wall_x_offset

            oled_mount_location_xyz = (np.array(base_pt1) + np.array(base_pt2)) / 2. + np.array(
                ((-_left_wall_x_offset / 2), 0, 0)) + np.array(_oled_translation_offset)
            oled_mount_location_xyz[2] = (oled_mount_location_xyz[2] + base_pt0[2]) / 2

            angle_x = np.arctan2(base_pt1[2] - base_pt2[2], base_pt1[1] - base_pt2[1])
            angle_z = np.arctan2(base_pt1[0] - base_pt2[0], base_pt1[1] - base_pt2[1])
            if trackball_in_wall and (side == ball_side or ball_side == 'both'):
                # oled_mount_rotation_xyz = (0, rad2deg(angle_x), -rad2deg(angle_z)-90) + np.array(oled_rotation_offset)
                # oled_mount_rotation_xyz = (rad2deg(angle_x)*.707, rad2deg(angle_x)*.707, -45) + np.array(oled_rotation_offset)
                oled_mount_rotation_xyz = (0, rad2deg(angle_x), -90) + np.array(_oled_rotation_offset)
            else:
                oled_mount_rotation_xyz = (rad2deg(angle_x), 0, -rad2deg(angle_z)) + np.array(_oled_rotation_offset)

        return oled_mount_location_xyz, oled_mount_rotation_xyz


    def oled_sliding_mount_frame(side='right'):
        mount_ext_width = oled_mount_width + 2 * oled_mount_rim
        mount_ext_height = (
                oled_mount_height + 2 * oled_edge_overlap_end
                + oled_edge_overlap_connector + oled_edge_overlap_clearance
                + 2 * oled_mount_rim
        )
        mount_ext_up_height = oled_mount_height + 2 * oled_mount_rim
        top_hole_start = -mount_ext_height / 2.0 + oled_mount_rim + oled_edge_overlap_end + oled_edge_overlap_connector
        top_hole_length = oled_mount_height

        hole = box(mount_ext_width, mount_ext_up_height, oled_mount_cut_depth + .01)
        hole = translate(hole, (0., top_hole_start + top_hole_length / 2, 0.))

        hole_down = box(mount_ext_width, mount_ext_height, oled_mount_depth + oled_mount_cut_depth / 2)
        hole_down = translate(hole_down, (0., 0., -oled_mount_cut_depth / 4))
        hole = union([hole, hole_down])

        shape = box(mount_ext_width, mount_ext_height, oled_mount_depth)

        conn_hole_start = -mount_ext_height / 2.0 + oled_mount_rim
        conn_hole_length = (
                oled_edge_overlap_end + oled_edge_overlap_connector
                + oled_edge_overlap_clearance + oled_thickness
        )
        conn_hole = box(oled_mount_width, conn_hole_length + .01, oled_mount_depth)
        conn_hole = translate(conn_hole, (
            0,
            conn_hole_start + conn_hole_length / 2,
            -oled_edge_overlap_thickness
        ))

        end_hole_length = (
                oled_edge_overlap_end + oled_edge_overlap_clearance
        )
        end_hole_start = mount_ext_height / 2.0 - oled_mount_rim - end_hole_length
        end_hole = box(oled_mount_width, end_hole_length + .01, oled_mount_depth)
        end_hole = translate(end_hole, (
            0,
            end_hole_start + end_hole_length / 2,
            -oled_edge_overlap_thickness
        ))

        top_hole_start = -mount_ext_height / 2.0 + oled_mount_rim + oled_edge_overlap_end + oled_edge_overlap_connector
        top_hole_length = oled_mount_height
        top_hole = box(oled_mount_width, top_hole_length, oled_edge_overlap_thickness + oled_thickness - oled_edge_chamfer)
        top_hole = translate(top_hole, (
            0,
            top_hole_start + top_hole_length / 2,
            (oled_mount_depth - oled_edge_overlap_thickness - oled_thickness - oled_edge_chamfer) / 2.0
        ))

        top_chamfer_1 = box(
            oled_mount_width,
            top_hole_length,
            0.01
        )
        top_chamfer_2 = box(
            oled_mount_width + 2 * oled_edge_chamfer,
            top_hole_length + 2 * oled_edge_chamfer,
            0.01
        )
        top_chamfer_1 = translate(top_chamfer_1, (0, 0, -oled_edge_chamfer - .05))

        top_chamfer_1 = hull_from_shapes([top_chamfer_1, top_chamfer_2])

        top_chamfer_1 = translate(top_chamfer_1, (
            0,
            top_hole_start + top_hole_length / 2,
            oled_mount_depth / 2.0 + .05
        ))

        top_hole = union([top_hole, top_chamfer_1])

        shape = difference(shape, [conn_hole, top_hole, end_hole])

        oled_mount_location_xyz, oled_mount_rotation_xyz = oled_position_rotation(side=side)

        shape = rotate(shape, oled_mount_rotation_xyz)
        shape = translate(shape,
                          (
                              oled_mount_location_xyz[0],
                              oled_mount_location_xyz[1],
                              oled_mount_location_xyz[2],
                          )
                          )

        hole = rotate(hole, oled_mount_rotation_xyz)
        hole = translate(hole,
                         (
                             oled_mount_location_xyz[0],
                             oled_mount_location_xyz[1],
                             oled_mount_location_xyz[2],
                         )
                         )
        return hole, shape


    def oled_clip_mount_frame(side='right'):
        mount_ext_width = oled_mount_width + 2 * oled_mount_rim
        mount_ext_height = (
                oled_mount_height + 2 * oled_clip_thickness
                + 2 * oled_clip_undercut + 2 * oled_clip_overhang + 2 * oled_mount_rim
        )
        hole = box(mount_ext_width, mount_ext_height, oled_mount_cut_depth + .01)

        shape = box(mount_ext_width, mount_ext_height, oled_mount_depth)
        shape = difference(shape, [box(oled_mount_width, oled_mount_height, oled_mount_depth + .1)])

        clip_slot = box(
            oled_clip_width + 2 * oled_clip_width_clearance,
            oled_mount_height + 2 * oled_clip_thickness + 2 * oled_clip_overhang,
            oled_mount_depth + .1
        )

        shape = difference(shape, [clip_slot])

        clip_undercut = box(
            oled_clip_width + 2 * oled_clip_width_clearance,
            oled_mount_height + 2 * oled_clip_thickness + 2 * oled_clip_overhang + 2 * oled_clip_undercut,
            oled_mount_depth + .1
        )

        clip_undercut = translate(clip_undercut, (0., 0., oled_clip_undercut_thickness))
        shape = difference(shape, [clip_undercut])

        plate = box(
            oled_mount_width + .1,
            oled_mount_height - 2 * oled_mount_connector_hole,
            oled_mount_depth - oled_thickness
        )
        plate = translate(plate, (0., 0., -oled_thickness / 2.0))
        shape = union([shape, plate])

        oled_mount_location_xyz, oled_mount_rotation_xyz = oled_position_rotation(side=side)

        shape = rotate(shape, oled_mount_rotation_xyz)
        shape = translate(shape,
                          (
                              oled_mount_location_xyz[0],
                              oled_mount_location_xyz[1],
                              oled_mount_location_xyz[2],
                          )
                          )

        hole = rotate(hole, oled_mount_rotation_xyz)
        hole = translate(hole,
                         (
                             oled_mount_location_xyz[0],
                             oled_mount_location_xyz[1],
                             oled_mount_location_xyz[2],
                         )
                         )

        return hole, shape


    def oled_clip():
        mount_ext_width = oled_mount_width + 2 * oled_mount_rim
        mount_ext_height = (
                oled_mount_height + 2 * oled_clip_thickness + 2 * oled_clip_overhang
                + 2 * oled_clip_undercut + 2 * oled_mount_rim
        )

        oled_leg_depth = oled_mount_depth + oled_clip_z_gap

        shape = box(mount_ext_width - .1, mount_ext_height - .1, oled_mount_bezel_thickness)
        shape = translate(shape, (0., 0., oled_mount_bezel_thickness / 2.))

        hole_1 = box(
            oled_screen_width + 2 * oled_mount_bezel_chamfer,
            oled_screen_length + 2 * oled_mount_bezel_chamfer,
            .01
        )
        hole_2 = box(oled_screen_width, oled_screen_length, 2.05 * oled_mount_bezel_thickness)
        hole = hull_from_shapes([hole_1, hole_2])

        shape = difference(shape, [translate(hole, (0., 0., oled_mount_bezel_thickness))])

        clip_leg = box(oled_clip_width, oled_clip_thickness, oled_leg_depth)
        clip_leg = translate(clip_leg, (
            0.,
            0.,
            # (oled_mount_height+2*oled_clip_overhang+oled_clip_thickness)/2,
            -oled_leg_depth / 2.
        ))

        latch_1 = box(
            oled_clip_width,
            oled_clip_overhang + oled_clip_thickness,
            .01
        )
        latch_2 = box(
            oled_clip_width,
            oled_clip_thickness / 2,
            oled_clip_extension
        )
        latch_2 = translate(latch_2, (
            0.,
            -(-oled_clip_thickness / 2 + oled_clip_thickness + oled_clip_overhang) / 2,
            -oled_clip_extension / 2
        ))
        latch = hull_from_shapes([latch_1, latch_2])
        latch = translate(latch, (
            0.,
            oled_clip_overhang / 2,
            -oled_leg_depth
        ))

        clip_leg = union([clip_leg, latch])

        clip_leg = translate(clip_leg, (
            0.,
            (oled_mount_height + 2 * oled_clip_overhang + oled_clip_thickness) / 2 - oled_clip_y_gap,
            0.
        ))

        shape = union([shape, clip_leg, mirror(clip_leg, 'XZ')])

        return shape


    def oled_undercut_mount_frame(side='right'):
        mount_ext_width = oled_mount_width + 2 * oled_mount_rim
        mount_ext_height = oled_mount_height + 2 * oled_mount_rim
        hole = box(mount_ext_width, mount_ext_height, oled_mount_cut_depth + .01)

        shape = box(mount_ext_width, mount_ext_height, oled_mount_depth)
        shape = difference(shape, [box(oled_mount_width, oled_mount_height, oled_mount_depth + .1)])
        undercut = box(
            oled_mount_width + 2 * oled_mount_undercut,
            oled_mount_height + 2 * oled_mount_undercut,
            oled_mount_depth)
        undercut = translate(undercut, (0., 0., -oled_mount_undercut_thickness))
        shape = difference(shape, [undercut])

        oled_mount_location_xyz, oled_mount_rotation_xyz = oled_position_rotation(side=side)

        shape = rotate(shape, oled_mount_rotation_xyz)
        shape = translate(shape, (
            oled_mount_location_xyz[0],
            oled_mount_location_xyz[1],
            oled_mount_location_xyz[2],
        )
                          )

        hole = rotate(hole, oled_mount_rotation_xyz)
        hole = translate(hole, (
            oled_mount_location_xyz[0],
            oled_mount_location_xyz[1],
            oled_mount_location_xyz[2],
        )
                         )

        return hole, shape


    def teensy_holder():
        print('teensy_holder()')
        teensy_top_xy = key_position(wall_locate3(-1, 0), 0, centerrow - 1)
        teensy_bot_xy = key_position(wall_locate3(-1, 0), 0, centerrow + 1)
        teensy_holder_length = teensy_top_xy[1] - teensy_bot_xy[1]
        teensy_holder_offset = -teensy_holder_length / 2
        teensy_holder_top_offset = (teensy_holder_top_length / 2) - teensy_holder_length

        s1 = box(3, teensy_holder_length, 6 + teensy_width)
        s1 = translate(s1, [1.5, teensy_holder_offset, 0])

        s2 = box(teensy_pcb_thickness, teensy_holder_length, 3)
        s2 = translate(s2,
                       (
                           (teensy_pcb_thickness / 2) + 3,
                           teensy_holder_offset,
                           -1.5 - (teensy_width / 2),
                       )
                       )

        s3 = box(teensy_pcb_thickness, teensy_holder_top_length, 3)
        s3 = translate(s3,
                       [
                           (teensy_pcb_thickness / 2) + 3,
                           teensy_holder_top_offset,
                           1.5 + (teensy_width / 2),
                       ]
                       )

        s4 = box(4, teensy_holder_top_length, 4)
        s4 = translate(s4,
                       [teensy_pcb_thickness + 5, teensy_holder_top_offset, 1 + (teensy_width / 2)]
                       )

        shape = union((s1, s2, s3, s4))

        shape = translate(shape, [-teensy_holder_width, 0, 0])
        shape = translate(shape, [-1.4, 0, 0])
        shape = translate(shape,
                          [teensy_top_xy[0], teensy_top_xy[1] - 1, (6 + teensy_width) / 2]
                          )

        return shape


    def screw_insert_shape(bottom_radius, top_radius, height):
        debugprint('screw_insert_shape()')
        if bottom_radius == top_radius:
            base = translate(cylinder(radius=bottom_radius, height=height),
                             (0, 0, -height / 2)
                             )
        else:
            base = translate(cone(r1=bottom_radius, r2=top_radius, height=height), (0, 0, -height / 2))

        shape = union((
            base,
            translate(sphere(top_radius), (0, 0, height / 2)),
        ))
        return shape


    def screw_insert(column, row, bottom_radius, top_radius, height, side='right'):
        debugprint('screw_insert()')
        shift_right = column == lastcol
        shift_left = column == 0
        shift_up = (not (shift_right or shift_left)) and (row == 0)
        shift_down = (not (shift_right or shift_left)) and (row >= lastrow)

        if screws_offset == 'INSIDE':
            # debugprint('Shift Inside')
            shift_left_adjust = wall_base_x_thickness
            shift_right_adjust = -wall_base_x_thickness / 3
            shift_down_adjust = -wall_base_y_thickness / 2
            shift_up_adjust = -wall_base_y_thickness / 3

        elif screws_offset == 'OUTSIDE':
            debugprint('Shift Outside')
            shift_left_adjust = 0
            shift_right_adjust = wall_base_x_thickness / 2
            shift_down_adjust = wall_base_y_thickness * 2 / 3
            shift_up_adjust = wall_base_y_thickness * 2 / 3

        else:
            # debugprint('Shift Origin')
            shift_left_adjust = 0
            shift_right_adjust = 0
            shift_down_adjust = 0
            shift_up_adjust = 0

        if shift_up:
            position = key_position(
                list(np.array(wall_locate2(0, 1)) + np.array([0, (mount_height / 2) + shift_up_adjust, 0])),
                column,
                row,
            )
        elif shift_down:
            position = key_position(
                list(np.array(wall_locate2(0, -1)) - np.array([0, (mount_height / 2) + shift_down_adjust, 0])),
                column,
                row,
            )
        elif shift_left:
            position = list(
                np.array(left_key_position(row, 0, side=side)) + np.array(wall_locate3(-1, 0)) + np.array(
                    (shift_left_adjust, 0, 0))
            )
        else:
            position = key_position(
                list(np.array(wall_locate2(1, 0)) + np.array([(mount_height / 2), 0, 0]) + np.array(
                    (shift_right_adjust, 0, 0))
                     ),
                column,
                row,
            )

        shape = screw_insert_shape(bottom_radius, top_radius, height)
        shape = translate(shape, [position[0], position[1], height / 2])

        return shape


    def screw_insert_thumb(bottom_radius, top_radius, height, side='right'):
        position = cluster(side).screw_positions()

        shape = screw_insert_shape(bottom_radius, top_radius, height)
        shape = translate(shape, [position[0], position[1], height / 2])
        return shape


    def screw_insert_all_shapes(bottom_radius, top_radius, height, offset=0, side='right'):
        print('screw_insert_all_shapes()')
        shape = [
            translate(screw_insert(0, 0, bottom_radius, top_radius, height, side=side), (0, 0, offset)),  # rear left
            translate(screw_insert(3, lastrow, bottom_radius, top_radius, height, side=side),
                      (0, 0, offset)),  # front middle
            translate(screw_insert(3, 0, bottom_radius, top_radius, height, side=side), (0, 0, offset)),  # rear middle
            translate(screw_insert(lastcol, 0, bottom_radius, top_radius, height, side=side),
                      (0, 0, offset)),  # rear right
            translate(screw_insert(lastcol, lastrow - 1, bottom_radius, top_radius, height, side=side),
                      (-2, -8, offset)),  # front right # TODO CONFIGURE IN JSON
            translate(screw_insert_thumb(bottom_radius, top_radius, height, side), (0, 0, offset)),  # thumb cluster
        ]
        # front left
        if thumb_style == RenameMeCluster.name():
            shape.append(translate(screw_insert(0, lastrow - 2, bottom_radius, top_radius, height, side=side),
                      (0, left_wall_lower_y_offset, offset)))
        else:
            shape.append(translate(screw_insert(0, lastrow - 1, bottom_radius, top_radius, height, side=side),
                      (0, left_wall_lower_y_offset, offset)))

        return shape


    def screw_insert_holes(side='right'):
        return screw_insert_all_shapes(
            screw_insert_bottom_radius, screw_insert_top_radius, screw_insert_height + .02, offset=-.01, side=side
        )


    def screw_insert_outers(side='right'):
        return screw_insert_all_shapes(
            screw_insert_bottom_radius + 1.6,
            screw_insert_top_radius + 1.6,
            screw_insert_height + 1.5,
            side=side
        )


    def screw_insert_screw_holes(side='right'):
        return screw_insert_all_shapes(1.7, 1.7, 350, side=side)


    def wire_post(direction, offset):
        debugprint('wire_post()')
        s1 = box(
            wire_post_diameter, wire_post_diameter, wire_post_height
        )
        s1 = translate(s1, [0, -wire_post_diameter * 0.5 * direction, 0])

        s2 = box(
            wire_post_diameter, wire_post_overhang, wire_post_diameter
        )
        s2 = translate(s2,
                       [0, -wire_post_overhang * 0.5 * direction, -wire_post_height / 2]
                       )

        shape = union((s1, s2))
        shape = translate(shape, [0, -offset, (-wire_post_height / 2) + 3])
        shape = rotate(shape, [-alpha / 2, 0, 0])
        shape = translate(shape, (3, -mount_height / 2, 0))

        return shape

    # not referenced?  WIP?
    # def wire_posts():
    #     debugprint('wire_posts()')
    #     shape = current_cluster.ml_place(wire_post(1, 0).translate([-5, 0, -2]))
    #     shape = union([shape, current_cluster.ml_place(wire_post(-1, 6).translate([0, 0, -2.5]))])
    #     shape = union([shape, current_cluster.ml_place(wire_post(1, 0).translate([5, 0, -2]))])
    #
    #     for column in range(lastcol):
    #         for row in range(lastrow - 1):
    #             shape = union([
    #                 shape,
    #                 key_place(wire_post(1, 0).translate([-5, 0, 0]), column, row),
    #                 key_place(wire_post(-1, 6).translate([0, 0, 0]), column, row),
    #                 key_place(wire_post(1, 0).translate([5, 0, 0]), column, row),
    #             ])
    #     return shape


    def model_side(side="right"):
        print('model_side()' + side)
        shape = union([key_holes(side=side)])
        if debug_exports:
            export_file(shape=shape, fname=path.join(r"..", "things", r"debug_key_plates"))
        connector_shape = connectors()
        shape = union([shape, connector_shape])
        if debug_exports:
            export_file(shape=shape, fname=path.join(r"..", "things", r"debug_connector_shape"))
        thumb_shape = cluster(side).thumb(side=side)
        if debug_exports:
            export_file(shape=thumb_shape, fname=path.join(r"..", "things", r"debug_thumb_shape"))
        shape = union([shape, thumb_shape])
        thumb_connector_shape = cluster(side).thumb_connectors(side=side)
        shape = union([shape, thumb_connector_shape])
        if debug_exports:
            export_file(shape=shape, fname=path.join(r"..", "things", r"debug_thumb_connector_shape"))
        walls_shape = case_walls(side=side)
        if debug_exports:
            export_file(shape=walls_shape, fname=path.join(r"..", "things", r"debug_walls_shape"))
        s2 = union([walls_shape])
        s2 = union([s2, *screw_insert_outers(side=side)])

        if controller_mount_type in ['RJ9_USB_TEENSY', 'USB_TEENSY']:
            s2 = union([s2, teensy_holder()])

        if controller_mount_type in ['RJ9_USB_TEENSY', 'RJ9_USB_WALL', 'USB_WALL', 'USB_TEENSY']:
            s2 = union([s2, usb_holder()])
            s2 = difference(s2, [usb_holder_hole()])

        if controller_mount_type in ['RJ9_USB_TEENSY', 'RJ9_USB_WALL']:
            s2 = difference(s2, [rj9_space()])

        if controller_mount_type in ['EXTERNAL']:
            s2 = difference(s2, [external_mount_hole()])

        if controller_mount_type in ['None']:
            0  # do nothing, only here to expressly state inaction.

        s2 = difference(s2, [union(screw_insert_holes(side=side))])
        shape = union([shape, s2])

        if controller_mount_type in ['RJ9_USB_TEENSY', 'RJ9_USB_WALL']:
            shape = union([shape, rj9_holder()])

        if oled_mount_type == "UNDERCUT":
            hole, frame = oled_undercut_mount_frame(side=side)
            shape = difference(shape, [hole])
            shape = union([shape, frame])

        elif oled_mount_type == "SLIDING":
            hole, frame = oled_sliding_mount_frame(side=side)
            shape = difference(shape, [hole])
            shape = union([shape, frame])

        elif oled_mount_type == "CLIP":
            hole, frame = oled_clip_mount_frame(side=side)
            shape = difference(shape, [hole])
            shape = union([shape, frame])

        if trackball_in_wall and (side == ball_side or ball_side == 'both'):
            tbprecut, tb, tbcutout, sensor, ball = generate_trackball_in_wall()

            shape = difference(shape, [tbprecut])
            # export_file(shape=shape, fname=path.join(save_path, config_name + r"_test_1"))
            shape = union([shape, tb])
            # export_file(shape=shape, fname=path.join(save_path, config_name + r"_test_2"))
            shape = difference(shape, [tbcutout])
            # export_file(shape=shape, fname=path.join(save_path, config_name + r"_test_3a"))
            # export_file(shape=add([shape, sensor]), fname=path.join(save_path, config_name + r"_test_3b"))
            shape = union([shape, sensor])

            if show_caps:
                shape = add([shape, ball])

        if (trackball_in_wall or ('TRACKBALL' in thumb_style)) and (side == ball_side or ball_side == 'both'):
            tbprecut, tb, tbcutout, sensor, ball = generate_trackball_in_cluster(cluster(side))

            shape = difference(shape, [tbprecut])
            if cluster(side).has_btus():
                shape = difference(shape, [tbcutout])
                shape = union([shape, tb])
            else:
                # export_file(shape=shape, fname=path.join(save_path, config_name + r"_test_1"))
                shape = union([shape, tb])
                # export_file(shape=shape, fname=path.join(save_path, config_name + r"_test_2"))
                shape = difference(shape, [tbcutout])
                # export_file(shape=shape, fname=path.join(save_path, config_name + r"_test_3a"))
                # export_file(shape=add([shape, sensor]), fname=path.join(save_path, config_name + r"_test_3b"))
                shape = union([shape, sensor])

            if show_caps:
                shape = add([shape, ball])

        block = box(350, 350, 40)
        block = translate(block, (0, 0, -20))
        shape = difference(shape, [block])

        if show_caps:
            shape = add([shape, cluster(side).thumbcaps(side=side)])
            shape = add([shape, caps()])

        if side == "left":
            shape = mirror(shape, 'YZ')

        return shape

    def wrist_rest(base, plate, side="right"):
        rest = import_file(path.join(parts_path, "dactyl_wrist_rest_v3_" + side))
        rest = rotate(rest, (0, 0, -60))
        rest = translate(rest, (30, -150, 26))
        rest = union([rest, translate(base, (0, 0, 5)), plate])
        return rest

    # NEEDS TO BE SPECIAL FOR CADQUERY
    def baseplate(wedge_angle=None, side='right'):
        if ENGINE == 'cadquery':
            # shape = mod_r
            shape = union([case_walls(side=side), *screw_insert_outers(side=side)])
            # tool = translate(screw_insert_screw_holes(side=side), [0, 0, -10])
            tool = screw_insert_all_shapes(screw_hole_diameter / 2., screw_hole_diameter / 2., 350, side=side)
            for item in tool:
                item = translate(item, [0, 0, -10])
                shape = difference(shape, [item])

            shape = translate(shape, (0, 0, -0.0001))

            square = cq.Workplane('XY').rect(1000, 1000)
            for wire in square.wires().objects:
                plane = cq.Workplane('XY').add(cq.Face.makeFromWires(wire))
            shape = intersect(shape, plane)

            outside = shape.vertices(cq.DirectionMinMaxSelector(cq.Vector(1, 0, 0), True)).objects[0]
            sizes = []
            max_val = 0
            inner_index = 0
            base_wires = shape.wires().objects
            for i_wire, wire in enumerate(base_wires):
                is_outside = False
                for vert in wire.Vertices():
                    if vert.toTuple() == outside.toTuple():
                        outer_wire = wire
                        outer_index = i_wire
                        is_outside = True
                        sizes.append(0)
                if not is_outside:
                    sizes.append(len(wire.Vertices()))
                if sizes[-1] > max_val:
                    inner_index = i_wire
                    max_val = sizes[-1]
            debugprint(sizes)
            inner_wire = base_wires[inner_index]

            # inner_plate = cq.Workplane('XY').add(cq.Face.makeFromWires(inner_wire))
            if wedge_angle is not None:
                cq.Workplane('XY').add(cq.Solid.revolve(outerWire, innerWires, angleDegrees, axisStart, axisEnd))
            else:
                inner_shape = cq.Workplane('XY').add(
                    cq.Solid.extrudeLinear(outerWire=inner_wire, innerWires=[], vecNormal=cq.Vector(0, 0, base_thickness)))
                inner_shape = translate(inner_shape, (0, 0, -base_rim_thickness))

                holes = []
                for i in range(len(base_wires)):
                    if i not in [inner_index, outer_index]:
                        holes.append(base_wires[i])
                cutout = [*holes, inner_wire]

                shape = cq.Workplane('XY').add(
                    cq.Solid.extrudeLinear(outer_wire, cutout, cq.Vector(0, 0, base_rim_thickness)))
                hole_shapes = []
                for hole in holes:
                    loc = hole.Center()
                    hole_shapes.append(
                        translate(
                            cylinder(screw_cbore_diameter / 2.0, screw_cbore_depth),
                            (loc.x, loc.y, 0)
                            # (loc.x, loc.y, screw_cbore_depth/2)
                        )
                    )
                shape = difference(shape, hole_shapes)
                shape = translate(shape, (0, 0, -base_rim_thickness))
                shape = union([shape, inner_shape])

            return shape
        else:

            shape = union([
                case_walls(side=side),
                *screw_insert_outers(side=side)
            ])

            tool = translate(union(screw_insert_screw_holes(side=side)), [0, 0, -10])
            base = box(1000, 1000, .01)
            shape = shape - tool
            shape = intersect(shape, base)

            shape = translate(shape, [0, 0, -0.001])

            return sl.projection(cut=True)(shape)


    def run():

        mod_r = model_side(side="right")
        export_file(shape=mod_r, fname=path.join(save_path, config_name + r"_right"))

        base = baseplate(side='right')
        export_file(shape=base, fname=path.join(save_path, config_name + r"_right_plate"))
        export_dxf(shape=base, fname=path.join(save_path, config_name + r"_right_plate"))

        # rest = wrist_rest(mod_r, base, side="right")
        #
        # export_file(shape=rest, fname=path.join(save_path, config_name + r"_right_wrist_rest"))

        if symmetry == "asymmetric":

            mod_l = model_side(side="left")
            export_file(shape=mod_l, fname=path.join(save_path, config_name + r"_left"))

            base_l = mirror(baseplate(side='left'), 'YZ')
            export_file(shape=base_l, fname=path.join(save_path, config_name + r"_left_plate"))
            export_dxf(shape=base_l, fname=path.join(save_path, config_name + r"_left_plate"))

        else:
            export_file(shape=mirror(mod_r, 'YZ'), fname=path.join(save_path, config_name + r"_left"))

            lbase = mirror(base, 'YZ')
            export_file(shape=lbase, fname=path.join(save_path, config_name + r"_left_plate"))
            export_dxf(shape=lbase, fname=path.join(save_path, config_name + r"_left_plate"))

        if ENGINE == 'cadquery':
            import freecad_that as freecad
            freecad.generate_freecad_script(path.abspath(save_path), [
                config_name + r"_right",
                config_name + r"_left",
                config_name + r"_right_plate",
                config_name + r"_left_plate"
            ], config_name)

        if oled_mount_type == 'UNDERCUT':
            export_file(shape=oled_undercut_mount_frame()[1],
                        fname=path.join(save_path, config_name + r"_oled_undercut_test"))

        if oled_mount_type == 'SLIDING':
            export_file(shape=oled_sliding_mount_frame()[1],
                        fname=path.join(save_path, config_name + r"_oled_sliding_test"))

        if oled_mount_type == 'CLIP':
            oled_mount_location_xyz = (0.0, 0.0, -oled_mount_depth / 2)
            oled_mount_rotation_xyz = (0.0, 0.0, 0.0)
            export_file(shape=oled_clip(), fname=path.join(save_path, config_name + r"_oled_clip"))
            export_file(shape=oled_clip_mount_frame()[1],
                        fname=path.join(save_path, config_name + r"_oled_clip_test"))
            export_file(shape=union((oled_clip_mount_frame()[1], oled_clip())),
                        fname=path.join(save_path, config_name + r"_oled_clip_assy_test"))

    all_merged = locals().copy()
    for item in globals():
        all_merged[item] = globals()[item]

    def get_cluster(style):
        if style == CarbonfetCluster.name():
            clust = CarbonfetCluster(all_merged)
        elif style == MiniCluster.name():
            clust = MiniCluster(all_merged)
        elif style == MinidoxCluster.name():
            clust = MinidoxCluster(all_merged)
        elif style == TrackballOrbyl.name():
            clust = TrackballOrbyl(all_merged)
        elif style == TrackballWild.name():
            clust = TrackballWild(all_merged)
        elif style == TrackballBTU.name():
            clust = TrackballBTU(all_merged)
        elif style == TrackballCJ.name():
            clust = TrackballCJ(all_merged)
        elif style == CustomCluster.name():
            clust = CustomCluster(all_merged)
        elif style == RenameMeCluster.name():
            clust = RenameMeCluster(all_merged)
        else:
            clust = DefaultCluster(all_merged)

        return clust


    right_cluster = get_cluster(thumb_style)

    if right_cluster.is_tb:
        if ball_side == "both":
            left_cluster = right_cluster
        elif ball_side == "left":
            left_cluster = right_cluster
            right_cluster = get_cluster(other_thumb)
        else:
            left_cluster = get_cluster(other_thumb)
    elif other_thumb != "DEFAULT" and other_thumb != thumb_style:
        left_cluster = get_cluster(other_thumb)
    else:
        left_cluster = right_cluster  # this assumes thumb_style always overrides DEFAULT other_thumb

    run()


#
if __name__ == '__main__':
    make_dactyl()

    # base = baseplate()
    # export_file(shape=base, fname=path.join(save_path, config_name + r"_plate"))

