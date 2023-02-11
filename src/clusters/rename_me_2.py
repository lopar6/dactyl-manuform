import json
import os
# TODO change inner curve shape to fix width issues
# TODO change cluster locations

class RenameMeCluster2(object):
    num_keys = 6
    is_tb = False
    thumb_offsets = [
        6,
        -3,
        7
    ]
    thumb_plate_tr_rotation = 0
    thumb_plate_tl_rotation = 0
    thumb_plate_mr_rotation = 0
    thumb_plate_ml_rotation = 0
    thumb_plate_br_rotation = 0
    thumb_plate_bl_rotation = 0

    @staticmethod
    def name():
        return "RENAME_ME_2"


    def get_config(self):
        with open(os.path.join(".", "clusters", "json", "DEFAULT.json"), mode='r') as fid:
            data = json.load(fid)
        for item in data:
            if not hasattr(self, str(item)):
                print(self.name() + ": NO MEMBER VARIABLE FOR " + str(item))
                continue
            setattr(self, str(item), data[item])
        return data

    def __init__(self, parent_locals):
        for item in parent_locals:
            globals()[item] = parent_locals[item]
        self.get_config()
        print(self.name(), " built")

    def thumborigin(self):
        # debugprint('thumborigin()')
        origin = key_position([mount_width / 2, -(mount_height / 2), 0], 1, cornerrow)

        for i in range(len(origin)):
            origin[i] = origin[i] + self.thumb_offsets[i]

        if thumb_style == 'MINIDOX':
            origin[1] = origin[1] - .4 * (trackball_Usize - 1) * sa_length

        return origin

    def bottom_right_place(self, shape):
        shape = rotate(shape, [10, -20, 20])
        shape = translate(shape, self.thumborigin())
        shape = translate(shape, [-16.5, -27, -12])
        return shape

    def top_right_place(self, shape):
        debugprint('ml_place()')
        shape = rotate(shape, [10, -20, 20])
        shape = translate(shape, self.thumborigin())
        shape = translate(shape, [-24, -9, -9])
        return shape

    def bottom_left_place(self, shape):
        debugprint('mr_place()')
        shape = rotate(shape, [10, -10, 20])
        shape = translate(shape, self.thumborigin())
        shape = translate(shape, [-37, -28, -18])
        return shape

    # Top left of the square section
    def top_left_place(self, shape):
        debugprint('br_place()')
        shape = rotate(shape, [10, -10, 20])
        shape = translate(shape, self.thumborigin())
        shape = translate(shape, [-45, -10, -17])
        return shape

    # Farthest left / back (on right side)
    def mid_top_place(self, shape):
        debugprint('bl_place()')
        shape = rotate(shape, [10, -10, 10])
        shape = translate(shape, self.thumborigin())
        shape = translate(shape, [-52, 9, -17])
        return shape

    def top_place(self, shape):
        debugprint('top_place()')
        shape = rotate(shape, [10, -10, 7])
        shape = translate(shape, self.thumborigin())
        shape = translate(shape, [-54.5, 30, -17])
        return shape

    def bottom_structural_node_place(self, shape):
        shape = translate(shape, self.thumborigin())
        shape = translate(shape, [-30, -55, -10])
        return shape

    def bottom_structural_node_place_two(self, shape):
        shape = translate(shape, self.thumborigin())
        shape = translate(shape, [-45, -50, -10])
        return shape

    def thumb_1x_layout(self, shape, cap=False):
        debugprint('thumb_1x_layout()')
        if cap:
            shape_list = [
                self.bottom_left_place(rotate(shape, [0, 0, self.thumb_plate_mr_rotation])),
                self.top_right_place(rotate(shape, [0, 0, self.thumb_plate_ml_rotation])),
                self.top_left_place(rotate(shape, [0, 0, self.thumb_plate_br_rotation])),
                self.mid_top_place(rotate(shape, [0, 0, self.thumb_plate_bl_rotation])),
            ]

            if default_1U_cluster:
                shape_list.append(self.bottom_right_place(rotate(rotate(shape, (0, 0, 90)), [0, 0, self.thumb_plate_tr_rotation])))
                shape_list.append(self.bottom_right_place(rotate(rotate(shape, (0, 0, 90)), [0, 0, self.thumb_plate_tr_rotation])))
                shape_list.append(self.top_place(rotate(shape, [0, 0, self.thumb_plate_tl_rotation])))
            shapes = add(shape_list)

        else:
            shape_list = [
                self.bottom_left_place(rotate(shape, [0, 0, self.thumb_plate_mr_rotation])),
                self.top_right_place(rotate(shape, [0, 0, self.thumb_plate_ml_rotation])),
                self.top_left_place(rotate(shape, [0, 0, self.thumb_plate_br_rotation])),
                self.mid_top_place(rotate(shape, [0, 0, self.thumb_plate_bl_rotation])),
            ]
            if default_1U_cluster:
                shape_list.append(self.bottom_right_place(rotate(rotate(shape, (0, 0, 90)), [0, 0, self.thumb_plate_tr_rotation])))
            shapes = union(shape_list)
        return shapes

    def thumb_15x_layout(self, shape, cap=False):
        debugprint('thumb_15x_layout()')
        if cap:
            shape = rotate(shape, (0, 0, 90))
            shape_list = [
                self.top_place(shape),
            ]
            shape_list.append(self.bottom_right_place(shape))

            return add(shape_list)
        else:
            shape_list = [
                self.top_place(shape),
            ]
            if not default_1U_cluster:
                shape_list.append(self.bottom_right_place(shape))

            return union(shape_list)

    def thumbcaps(self, side='right'):
        t1 = self.thumb_1x_layout(sa_cap(1), cap=True)
        if not default_1U_cluster:
            t1.add(self.thumb_15x_layout(sa_cap(1.5), cap=True))
        return t1

    def thumb(self, side="right"):
        print('thumb()')
        shape = self.thumb_1x_layout(rotate(single_plate(side=side), (0, 0, -90)))
        shape = union([shape, self.thumb_15x_layout(rotate(single_plate(side=side), (0, 0, -90)))])
        shape = union([shape, self.thumb_15x_layout(rotate(single_plate(side=side), (0, 0, -90)))])

        return shape

    def thumb_post_tr(self):
        debugprint('thumb_post_tr()')
        return translate(web_post(),
                         [(mount_width / 2) - post_adj, ((mount_height / 2) + double_plate_height) - post_adj, 0]
                         )

    def thumb_post_tl(self):
        debugprint('thumb_post_tl()')
        return translate(web_post(),
                         [-(mount_width / 2) + post_adj, ((mount_height / 2) + double_plate_height) - post_adj, 0]
                         )

    def thumb_post_bl(self):
        debugprint('thumb_post_bl()')
        return translate(web_post(),
                         [-(mount_width / 2) + post_adj, -((mount_height / 2) + double_plate_height) + post_adj, 0]
                         )

    def thumb_post_br(self):
        debugprint('thumb_post_br()')
        return translate(web_post(),
                         [(mount_width / 2) - post_adj, -((mount_height / 2) + double_plate_height) + post_adj, 0]
                         )

    def thumb_connectors(self, side="right"):
        print('default thumb_connectors()')
        hulls = []

        hulls.append(
            triangle_hulls(
                [
                    self.top_place(self.thumb_post_tr()),
                    self.top_place(web_post_tr()),
                    self.top_place(self.thumb_post_tr()),
                    self.top_place(web_post_br()),
                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    self.top_right_place(web_post_br()),
                    self.top_right_place(web_post_bl()),
                    self.bottom_right_place(web_post_tr()),
                    self.bottom_right_place(web_post_tl()),

                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    self.bottom_right_place(web_post_tl()),
                    self.bottom_right_place(web_post_bl()),
                    self.bottom_left_place(web_post_tr()),
                    self.bottom_left_place(web_post_br()),

                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    self.top_right_place(web_post_bl()),
                    self.top_left_place(web_post_br()),
                    self.bottom_right_place(web_post_tl()),
                    self.bottom_left_place(web_post_tr()),

                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    self.top_left_place(web_post_br()),
                    self.bottom_left_place(web_post_tl()),
                    self.top_left_place(web_post_bl()),
                    self.bottom_left_place(web_post_tr()),
                    self.top_left_place(web_post_br()),
                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    self.mid_top_place(web_post_tr()),
                    self.top_place(web_post_bl()),
                    self.mid_top_place(web_post_tl()),
                    self.top_place(web_post_br()),
                    self.mid_top_place(web_post_tr()),
                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    self.top_left_place(web_post_tr()),
                    self.top_right_place(web_post_bl()),
                    self.top_left_place(web_post_br()),

                    self.top_left_place(web_post_tr()),
                    self.top_right_place(web_post_tl()),
                    self.top_right_place(web_post_bl()),
                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    self.top_left_place(web_post_tl()),
                    self.mid_top_place(web_post_bl()),
                    self.mid_top_place(web_post_br()),

                    self.mid_top_place(web_post_br()),
                    self.top_left_place(web_post_tl()),
                    self.top_left_place(web_post_tr()),
                ]
            )
        )

        return union(hulls)


    def walls(self, side="right"):
        print('thumb_walls()')

        shape = union([wall_brace(self.bottom_right_place, -1, -1, web_post_br(), self.bottom_right_place, -1, -1, web_post_bl())])
        shape = union([shape, wall_brace(self.bottom_right_place, -1, -1,  web_post_bl(), self.bottom_left_place, -1, -1,  web_post_br())])
        shape = union([shape, wall_brace(self.bottom_left_place, -1, -1,  web_post_br(), self.bottom_left_place, -1, -1,  web_post_bl())])
        shape = union([shape, wall_brace(self.bottom_left_place, -1, -1,  web_post_bl(), self.bottom_left_place, -1, -1,  web_post_tl())])
        shape = union([shape, wall_brace(self.bottom_left_place, -1, -1,  web_post_tl(), self.top_left_place, -1, -1,  web_post_bl())])
        shape = union([shape, wall_brace(self.top_left_place, -1, -1,  web_post_bl(), self.top_left_place, -1, -1,  web_post_tl())])
        shape = union([shape, wall_brace(self.top_left_place, -1, -1,  web_post_tl(), self.mid_top_place, -1, -1,  web_post_bl())])
        shape = union([shape, wall_brace(self.mid_top_place, -1, -1,  web_post_bl(), self.mid_top_place, -1, 0, web_post_tl())])
        shape = union([shape, wall_brace(self.mid_top_place, -1, 0, web_post_tl(), self.top_place, -1, 0, web_post_bl())])
        shape = union([shape, wall_brace(self.top_place, -1, 0, web_post_bl(), self.top_place, -1, 0, web_post_tl())])
        shape = union([shape, wall_brace(self.top_place, -2, .35, web_post_tr(), self.top_place, -1, 0, web_post_tl())])

        shape = union([shape, wall_brace(
            key_place, 0, -1, web_post_bl(),
            self.bottom_right_place, -1, 0, web_post_br(),
            place1_extra_args = (3, cornerrow + 1))])
        return shape

    def connection(self, side='right'):
        print('thumb_connection()')
        # TODO lower the connection point on the inside
        hulls = []
        # This is pretty hacky
        right_wall_corner = translate(key_place(web_post_bl(), 3, cornerrow + 1), [5.16, -19, 1.1])
        below_right_wall_corner = translate(right_wall_corner, [0, 0, -8])

        hulls.append(
            triangle_hulls(
                [
                    self.top_place(web_post_br()),
                    self.top_place(web_post_tr()),
                    key_place(web_post_bl(), 0, cornerrow - 1),
                    key_place(web_post_tl(), 0, cornerrow- 1),

                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    self.top_place(web_post_br()),
                    self.mid_top_place(web_post_tr()),
                    key_place(web_post_bl(), 0, cornerrow - 1),
                    key_place(web_post_tl(), 0, cornerrow),
                    self.mid_top_place(web_post_tr()),
                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    self.mid_top_place(web_post_br()),
                    self.mid_top_place(web_post_tr()),
                    key_place(web_post_bl(), 0, cornerrow),
                    key_place(web_post_tl(), 0, cornerrow),

                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    self.mid_top_place(web_post_br()),
                    self.top_left_place(web_post_tr()),
                    key_place(web_post_bl(), 0, cornerrow),
                    self.top_left_place(web_post_tr()),

                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    self.top_left_place(web_post_tr()),
                    self.top_right_place(web_post_tl()),
                    key_place(web_post_bl(), 0, cornerrow),
                    self.top_left_place(web_post_tr()),
                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    self.top_right_place(web_post_tl()),
                    key_place(web_post_bl(), 0, cornerrow),
                    key_place(web_post_br(), 0, cornerrow),
                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    self.top_right_place(web_post_tl()),
                    self.top_right_place(web_post_tr()),
                    key_place(web_post_br(), 0, cornerrow),
                    key_place(web_post_bl(), 1, cornerrow),
                    self.top_right_place(web_post_tr()),
                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    self.top_right_place(web_post_tr()),
                    key_place(web_post_bl(), 1, cornerrow),
                    key_place(web_post_br(), 1, cornerrow),
                ]
            )
        )

        # Tiny triangle
        hulls.append(
            triangle_hulls(
                [
                    key_place(web_post_br(), 1, cornerrow),
                    key_place(web_post_bl(), 2, cornerrow),
                    key_place(web_post_tl(), 2, cornerrow + 1),
                ]
            )
        )

        # Thin triangle
        hulls.append(
            triangle_hulls(
                [
                    key_place(web_post_br(), 1, cornerrow),
                    key_place(web_post_tl(), 2, cornerrow + 1),
                    key_place(web_post_bl(), 2, cornerrow + 1),
                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    key_place(web_post_br(), 1, cornerrow),
                    key_place(web_post_bl(), 2, cornerrow + 1),
                    self.top_right_place(web_post_tr()),
                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    key_place(web_post_bl(), 2, cornerrow + 1),
                    self.top_right_place(web_post_tr()),
                    self.top_right_place(web_post_br()),
                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    key_place(web_post_bl(), 2, cornerrow + 1),
                    self.top_right_place(web_post_br()),
                    self.bottom_right_place(web_post_tr()),
                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    key_place(web_post_bl(), 2, cornerrow + 1),
                    key_place(web_post_br(), 2, cornerrow + 1),
                    key_place(web_post_bl(), 3, cornerrow + 1),
                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    self.bottom_right_place(web_post_tr()),
                    key_place(web_post_bl(), 2, cornerrow + 1),
                    key_place(web_post_bl(), 3, cornerrow + 1),
                ]
            )
        )

        hulls.append(
            triangle_hulls(
                [
                    key_place(web_post_bl(), 3, cornerrow + 1),
                    self.bottom_right_place(web_post_br()),
                    self.bottom_right_place(web_post_tr()),
                ]
            )
        )

        return hulls

    def screw_positions(self):
        position = list(np.array(self.thumborigin()) + np.array([-8, -20, 0]))
        position[2] = self.thumborigin()
        return position

    def get_extras(self, shape, pos):
        return shape

    def has_btus(self):
        return False
