import numpy as np


class Line():
    def __init__(self, p1, p2):
        # p1 = (x1, y1)
        # p2 = (x2, y2)
        self.p1 = p1
        self.p2 = p2
        self.connected_lines = list()
        # todo:/ testing and or debugging
        self.visited = False
        self.name = None

    def __eq__(self, other):
        if isinstance(other, Line):
            return self.p1 == other.p1 and self.p2 == other.p2
        return False

    def __hash__(self):
        return hash('({},{})'.format(self.p1, self.p2))

    def get_length(self):
        x1, y1 = self.p1
        x2, y2 = self.p2
        afstand_x = abs(x1 - x2)
        afstand_y = abs(y1 - y2)
        afstand_pts = np.sqrt((afstand_x ** 2) + (afstand_y ** 2))
        return int(afstand_pts)

    def is_line_connected(self, line, offset):
        true_tabel = []

        true_tabel.append(Line.are_points_in_range(self.p1, line.p1, offset))
        true_tabel.append(Line.are_points_in_range(self.p1, line.p2, offset))
        true_tabel.append(Line.are_points_in_range(self.p2, line.p1, offset))
        true_tabel.append(Line.are_points_in_range(self.p2, line.p2, offset))

        return any(true_tabel)

    def get_direction(self):
        # params self = line (x1,y1,x2,y2)
        # out :
        #    1 vertical
        #    0 horizontal  
        #    -1 no direction bepaald
        afstand = self.get_length()
        x1, y1 = self.p1
        x2, y2 = self.p2
        v_y = abs(y1 - y2) / afstand  # = sin x
        vector = np.arcsin(v_y) / np.pi * 180
        if vector > 45:
            return 1  # vertical
        elif vector < 45:
            return 0  # horizontal
        else:
            # trouw exception
            return -1

    def is_point_in_segment(self, point, offset):

        x1, y1 = self.p1
        x2, y2 = self.p2
        x3, y3 = point
        x41 = min(x1 - offset, x2 - offset)
        x42 = max(x1 + offset, x2 + offset)
        y41 = min(y1 - offset, y2 - offset)
        y42 = max(y1 + offset, y2 + offset)

        return x41 <= x3 <= x42 and y41 <= y3 <= y42

    def is_line_over(self, line, offset):
        # NOG AANPASSEN....
        # is_equal
        if not self == line and self.get_direction() == line.get_direction():

            condition_1 = self.is_point_in_segment(line.p1, offset)
            condition_2 = self.is_point_in_segment(line.p2, offset)

            return condition_1 or condition_2
        else:
            return False

    def is_connected(self, line, offset):
        if not self == line:
            condition1 = self.is_point_in_segment(line.p1, offset)
            condition2 = self.is_point_in_segment(line.p2, offset)
            c = [condition1, condition2]
            return any(c)
        else:
            return False

    def make_stray(self):
        x1, y1 = self.p1
        x2, y2 = self.p2
        direc = self.get_direction()
        if direc:  # vertical
            line = (x1, y1, x1, y2)
            self.p1 = (x1, y1)
            self.p2 = (x1, y2)
        else:  # horizontal
            line = (x1, y1, x2, y1)
            self.p1 = (x1, y1)
            self.p2 = (x2, y1)

        return self

    def is_line_close(self, line, offset):
        x1, y1 = self.p1
        x2, y2 = self.p2
        x3, y3 = line.p1
        x4, y4 = line.p2

        if self.get_direction() == line.get_direction():
            direction = self.get_direction()
            is_connected = self.is_line_connected(line, offset)
            if direction:
                return abs(x1 - x3) <= offset and is_connected
            else:
                return abs(y1 - y3) <= offset and is_connected
        else:
            return False

    def print_line(self):
        return 'point 1: {}, point 2: {}'.format(self.p1, self.p2)

    @staticmethod
    def are_points_in_range(p1, p2, offset):
        x1, y1 = p1
        x2, y2 = p2
        afstand_x = abs(x1 - x2)
        afstand_y = abs(y1 - y2)
        afstand_pts = np.sqrt((afstand_x ** 2) + (afstand_y ** 2))

        return afstand_pts <= offset

    def get_partners(self, one_siders):
        partners = []
        for ln in one_siders:
            if ln in set(self.connected_lines):
                partners.append(ln)
        return partners
