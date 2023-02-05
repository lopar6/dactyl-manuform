import json
import os


class RenameMeCluster(object):
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
        return "RENAME_ME"


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

    # Very top
    def top_place(self, shape):
        debugprint('top_place()')
        shape = rotate(shape, [2.5, -80, 12])
        shape = translate(shape, self.thumborigin())
        shape = translate(shape, [-10, -4, 32])
        return shape

    # Farthest inside (right side on right keyboard)
    def far_inside_place(self, shape):
        debugprint('far_inside_place()')
        shape = rotate(shape, [20, -50, 40])
        shape = translate(shape, self.thumborigin())
        shape = translate(shape, [5, -35, 8])
        return shape

    # Middle of 3 on wrapping section
    def middle_of_three_place(self, shape):
        debugprint('mr_place()')
        shape = rotate(shape, [10, -60, 20])
        shape = translate(shape, self.thumborigin())
        shape = translate(shape, [-10, -22, 10])
        return shape

    # Very middle
    def true_middle_place(self, shape):
        debugprint('ml_place()')
        shape = rotate(shape, [2.5, -60, 12])
        shape = translate(shape, self.thumborigin())
        shape = translate(shape, [-17, -5, 10])
        return shape

    # Below true middle
    def below_t_middle_place(self, shape):
        debugprint('br_place()')
        shape = rotate(shape, [5, 20, 12])
        shape = translate(shape, self.thumborigin())
        shape = translate(shape, [-50, -10, -2])
        return shape

    # Farthest left / back (on right side)
    def far_back_place(self, shape):
        debugprint('bl_place()')
        shape = rotate(shape, [10, 20, 12])
        shape = translate(shape, self.thumborigin())
        shape = translate(shape, [-55, 8, 2])
        return shape

    def top_structural_node_place(self, shape):
        shape = translate(shape, self.thumborigin())
        shape = translate(shape, [-14, -28, 38])
        return shape

    def top_structural_node_place_inside(self, shape):
        shape = translate(shape, self.thumborigin())
        shape = translate(shape, [-19, -10, 38])
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
                self.middle_of_three_place(rotate(shape, [0, 0, self.thumb_plate_mr_rotation])),
                self.true_middle_place(rotate(shape, [0, 0, self.thumb_plate_ml_rotation])),
                self.below_t_middle_place(rotate(shape, [0, 0, self.thumb_plate_br_rotation])),
                self.far_back_place(rotate(shape, [0, 0, self.thumb_plate_bl_rotation])),
            ]

            if default_1U_cluster:
                shape_list.append(self.far_inside_place(rotate(rotate(shape, (0, 0, 90)), [0, 0, self.thumb_plate_tr_rotation])))
                shape_list.append(self.far_inside_place(rotate(rotate(shape, (0, 0, 90)), [0, 0, self.thumb_plate_tr_rotation])))
                shape_list.append(self.top_place(rotate(shape, [0, 0, self.thumb_plate_tl_rotation])))
            shapes = add(shape_list)

        else:
            shape_list = [
                self.middle_of_three_place(rotate(shape, [0, 0, self.thumb_plate_mr_rotation])),
                self.true_middle_place(rotate(shape, [0, 0, self.thumb_plate_ml_rotation])),
                self.below_t_middle_place(rotate(shape, [0, 0, self.thumb_plate_br_rotation])),
                self.far_back_place(rotate(shape, [0, 0, self.thumb_plate_bl_rotation])),
            ]
            if default_1U_cluster:
                shape_list.append(self.far_inside_place(rotate(rotate(shape, (0, 0, 90)), [0, 0, self.thumb_plate_tr_rotation])))
            shapes = union(shape_list)
        return shapes

    def thumb_15x_layout(self, shape, cap=False):
        debugprint('thumb_15x_layout()')
        if cap:
            shape = rotate(shape, (0, 0, 90))
            shape_list = [
                self.top_place(shape),
            ]
            shape_list.append(self.far_inside_place(shape))

            return add(shape_list)
        else:
            shape_list = [
                self.top_place(shape),
            ]
            if not default_1U_cluster:
                shape_list.append(self.far_inside_place(shape))

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

        # Very top of all sides to middle points
        hulls.append(
            triangle_hulls(
                [
                    self.top_structural_node_place_inside(self.thumb_post_tr()),
                    self.top_place(web_post_tr()),
                    self.top_structural_node_place(self.thumb_post_tr()),
                    self.top_place(web_post_br()),
                ]
            )
        )
        # Top to true middle
        hulls.append(
            triangle_hulls(
                [
                    self.true_middle_place(web_post_tr()),
                    self.top_place(web_post_bl()),
                    self.true_middle_place(web_post_br()),
                    # tiny triangle
                    self.middle_of_three_place(web_post_tr()),

                    self.true_middle_place(web_post_tr()),
                    self.top_place(web_post_tl()),
                    self.top_place(web_post_bl()),

                    self.top_place(web_post_bl()),
                    self.middle_of_three_place(web_post_tr()),
                    self.top_structural_node_place(self.thumb_post_tr()),
                ]
            )
        )

        # True middle to middle of 3
        hulls.append(
            triangle_hulls(
                [
                    self.middle_of_three_place(web_post_tl()),
                    self.true_middle_place(web_post_bl()),
                    self.true_middle_place(web_post_br()),

                    self.true_middle_place(web_post_br()),
                    self.middle_of_three_place(web_post_tl()),
                    self.middle_of_three_place(web_post_tr()),
                ]
            )
        )

        # Middle of 3 to farthest inside
        hulls.append(
            triangle_hulls(
                [
                    self.far_inside_place(web_post_tl()),
                    self.middle_of_three_place(web_post_bl()),
                    self.middle_of_three_place(web_post_br()),

                    self.middle_of_three_place(web_post_br()),
                    self.far_inside_place(web_post_tl()),
                    self.far_inside_place(web_post_tr()),
                ]
            )
        )

        # True middle of 3 to below true middle
        hulls.append(
            triangle_hulls(
                [
                    self.below_t_middle_place(web_post_tr()),
                    self.true_middle_place(web_post_bl()),
                    self.below_t_middle_place(web_post_br()),

                    self.below_t_middle_place(web_post_tr()),
                    self.true_middle_place(web_post_tl()),
                    self.true_middle_place(web_post_bl()),
                ]
            )
        )

        # Below true middle to farthest back
        hulls.append(
            triangle_hulls(
                [
                    # self.far_back_place(web_post_tl()),
                    # self.below_t_middle_place(web_post_bl()),
                    # self.below_t_middle_place(web_post_br()),

                    # self.below_t_middle_place(web_post_br()),
                    # self.far_back_place(web_post_tl()),
                    # self.far_back_place(web_post_tr()),
                    self.below_t_middle_place(web_post_tl()),
                    self.far_back_place(web_post_bl()),
                    self.far_back_place(web_post_br()),

                    self.far_back_place(web_post_br()),
                    self.below_t_middle_place(web_post_tl()),
                    self.below_t_middle_place(web_post_tr()),
                ]
            )
        )

        return union(hulls)


    def walls(self, side="right"):
        print('thumb_walls()')

        shape = union([wall_brace(self.far_inside_place, -1, -1, web_post_br(), self.far_inside_place, -1.5, -1, web_post_bl())])
        shape = union([shape, wall_brace(self.far_inside_place, -1.5, -1, web_post_bl(), self.far_inside_place, -1.5, -1, web_post_tl())])
        shape = union([shape, wall_brace(self.far_inside_place, -1.5, -1, web_post_tl(), self.middle_of_three_place, -1.5, -1, web_post_bl())])
        shape = union([shape, wall_brace(self.middle_of_three_place, -1.5, -1, web_post_bl(), self.middle_of_three_place, -1.5, -1, web_post_tl())])
        shape = union([shape, wall_brace(self.middle_of_three_place, -1.5, -1, web_post_tl(), self.true_middle_place, 0, -1, web_post_bl())])
        shape = union([shape, wall_brace(self.true_middle_place, 0, -1, web_post_bl(), self.below_t_middle_place, 0, -1, web_post_br())])
        shape = union([shape, wall_brace(self.below_t_middle_place, 0, -1, web_post_br(), self.below_t_middle_place, 0, -1, web_post_bl())])

        shape = union([shape, wall_brace(self.below_t_middle_place, 0, -1, web_post_bl(), self.below_t_middle_place, -1, 0, web_post_tl())])
        shape = union([shape, wall_brace(self.below_t_middle_place, -1, 0, web_post_tl(), self.far_back_place, -1, 0, web_post_bl())])
        shape = union([shape, wall_brace(self.far_back_place, -1, 0, web_post_bl(), self.far_back_place, -1, 0, web_post_tl())])
        shape = union([shape, wall_brace(self.far_back_place, -1.5, .35, web_post_tr(), self.far_back_place, -1, 0, web_post_tl())])

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
                    self.far_back_place(web_post_br()),
                    self.far_back_place(web_post_tr()),
                    # Corner of main board
                    key_place(web_post_bl(), 0, cornerrow),
                    key_place(web_post_tl(), 0, cornerrow),

                ]
            )
        )
        hulls.append(
            triangle_hulls(
                [
                    self.below_t_middle_place(web_post_tr()),
                    self.far_back_place(web_post_br()),
                    key_place(web_post_bl(), 0, cornerrow),
                    self.true_middle_place(web_post_tl()),
                ]
            )
        )
        hulls.append(
            triangle_hulls(
                [
                    key_place(web_post_br(), 1, cornerrow),
                    key_place(web_post_bl(), 2, cornerrow),
                    key_place(web_post_bl(), 2, cornerrow + 1),
                ]
            )
        )
        hulls.append(
            triangle_hulls(
                [
                    self.true_middle_place(web_post_tl()),
                    self.true_middle_place(web_post_tr()),
                    key_place(web_post_br(), 0, cornerrow),
                    key_place(web_post_br(), 1, cornerrow),
                    self.top_structural_node_place_inside(self.thumb_post_tr()),

                    self.top_place(web_post_tl()),
                    self.top_place(web_post_tr()),
                ]
            )
        )
        hulls.append(
            triangle_hulls(
                [
                    self.top_structural_node_place_inside(self.thumb_post_tr()),
                    self.top_structural_node_place(self.thumb_post_tr()),

                    key_place(web_post_br(), 1, cornerrow),
                    key_place(web_post_bl(), 2, cornerrow + 1),
                ]
            )
        )
        hulls.append(
            triangle_hulls(
                [
                    self.top_structural_node_place(self.thumb_post_tr()),
                    self.middle_of_three_place(web_post_tr()),
                    key_place(web_post_bl(), 2, cornerrow + 1),
                ]
            )
        )
        hulls.append(
            triangle_hulls(
                [
                    self.middle_of_three_place(web_post_tr()),
                    self.middle_of_three_place(web_post_br()),
                    key_place(web_post_bl(), 2, cornerrow + 1),
                    key_place(web_post_br(), 2, cornerrow + 1),


                ]
            )
        )
        hulls.append(
            triangle_hulls(
                [
                    self.far_inside_place(web_post_tr()),
                    self.middle_of_three_place(web_post_br()),
                    key_place(web_post_br(), 2, cornerrow + 1),

                    self.far_inside_place(web_post_tr()),
                    key_place(web_post_br(), 2, cornerrow + 1),
                    key_place(web_post_bl(), 3, cornerrow + 1),
                ]
            )
        )
        hulls.append(
            triangle_hulls(
                [
                    key_place(web_post_bl(), 3, cornerrow + 1),
                    self.far_inside_place(web_post_br()),
                    self.far_inside_place(web_post_tr()),
                ]
            )
        )
        hulls.append(
            triangle_hulls(
                [
                    key_place(web_post_bl(), 3, cornerrow + 1),
                    self.far_inside_place(web_post_br()),
                    right_wall_corner,
                ]
            )
        )
        hulls.append(
            triangle_hulls(
                [
                    key_place(web_post_bl(), 3, cornerrow + 1),
                    right_wall_corner,
                    below_right_wall_corner,
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
