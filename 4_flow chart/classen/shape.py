import numpy as np
from classen.line import Line


class Shape:
    def __init__(self, vorm, rectangle, tekst='', points=None):
        self.vorm = vorm
        self.rectangle = rectangle
        if tekst:
            self.tekst = tekst
        else:
            self.tekst = 'nog geen tekst'
        self.lines = []
        self.points = points
        self.conected_shapes = []
        self.child = None
        self.neighbour = None
        self.parent = None
        self.upper_neighbour = None
        self.YES = None
        self.NO = None
        self.unconnected_lines = []
        self.id = -1
        self.one_siders = list()

    def __eq__(self, other):
        if isinstance(other, Shape):
            return self.tekst == other.tekst and self.id == other.id
        return False

    def write_shape(self):
        return '{};{};{}'.format(self.vorm, self.rectangle, self.tekst)

    def set_line(self, line, offset):
        are_conected, direction = Shape.is_line_connected_to_shape(line, self.rectangle, offset)
        if are_conected:
            conected_line = {'line': line, 'direction': direction}
            self.lines.append(conected_line)

    def get_other_end(self, line, direction, offset):
        p1 = line.p1
        p2 = line.p2
        x, y, h, w = self.rectangle
        ver_center = w / 2
        hor_center = h / 2
        p = (0, 0)
        if direction == 0:
            p = (x + ver_center, y)
        elif direction == 1:
            p = (x + ver_center, y + h)
        elif direction == 2:
            p = (x + w, y + hor_center)
        elif direction == 3:
            p = (x, y + hor_center)
        if not Shape.are_points_in_range(p1, p, offset):
            return p1
        elif not Shape.are_points_in_range(p, p2, offset):
            return p2
        else:  # een exception zou hier best passen
            raise Exception('geen point is touching:\n\t offset: {}\n\t direction {}'
                            ' \n\tline (p1:{},p2: {}\n\tlength line {}\n\tline direction {}'
                            .format(offset,
                                    direction,
                                    line.p1,
                                    line.p2,
                                    line.get_length(),
                                    line.get_direction()))

    def is_point_touching(self, p, offset):
        x, y, h, w = self.rectangle
        ver_center = w / 2
        hor_center = h / 2
        up_p = (x + ver_center, y)
        down_p = (x + ver_center, y + h)
        right_p = (x + w, y + hor_center)
        left_p = (x, y + hor_center)
        points = [up_p, down_p, right_p, left_p]
        touching = []
        for point in points:
            connected = Shape.are_points_in_range(point, p, offset)
            touching.append(connected)

        return any(touching)

    def is_point_inside(self, p):
        x, y, h, w = self.rectangle
        xp, yp = p
        return x <= xp <= (x + w) and y <= yp <= (y + h)

    def has_shape_line(self, l):
        for conn_line in self.lines:
            line = conn_line['line']
            direction = conn_line['direction']
            if line == l:
                return True
        else:
            return False

    def has_unconnected_lines(self):
        return len(self.unconnected_lines) > 0

    def count_family(self):
        counter = [self.parent, self.neighbour, self.child, self.upper_neighbour]
        counter = [x for x in counter if x is not None]
        return len(counter)

    def count_upper_family(self):
        counter = [self.parent, self.upper_neighbour]
        counter = [x for x in counter if x is not None]
        return len(counter)

    def count_lower_family(self):
        counter = [self.child, self.neighbour]
        counter = [x for x in counter if x is not None]
        return len(counter)

    def count_options(self):
        counter = [self.YES, self.NO]
        counter = [x for x in counter if x is not None]
        return len(counter)

    def is_family_invalid(self):
        if self.count_family() == 0:
            # elke vorm moet minstens 1 family hebben
            return True
        if self.vorm == 'circle':
            if self.count_family() > 1:
                # circle moet maar 1 family hebben
                return True
        else:
            if self.count_family() < 2:
                return True
        if self.vorm == 'diamont':
            # diamont moeten minstens 2 family leden hebben
            # Yes en no options moeten gekoppeld worden aan iets
            if not self.count_options() > 0:
                return True
        elif self.count_lower_family() > 1:
            # geen diamont en meerdere lower family
            return True
        if self.count_upper_family() > 1:
            # ieder shape mag maar 1 upper family hebben
            return True
        return False

    def write_family(self):
        if self.parent is not None:
            print('\tparent', self.parent.tekst)
        if self.child is not None:
            print('\tchild', self.child.tekst)
        if self.neighbour is not None:
            print('\tneighbour', self.neighbour.tekst)
        if self.upper_neighbour is not None:
            print('\tupper neighbour', self.upper_neighbour.tekst)

    def write_family_ids(self, delimiter):
        result = []
        if self.parent is not None:
            result.append(self.parent.id)
        else:
            result.append('')
        if self.child is not None:
            result.append(self.child.id)
        else:
            result.append('')
        if self.neighbour is not None:
            result.append(self.neighbour.id)
        else:
            result.append('')
        if self.upper_neighbour is not None:
            result.append(self.upper_neighbour.id)
        else:
            result.append('')

        result = [str(x) for x in result]
        return delimiter.join(result)

    def is_line_connected(self, line, offset):
        if self.is_point_touching(line.p1, offset) or self.is_point_touching(line.p2, offset):
            return True
        return False

    @staticmethod
    def are_points_in_range(p1, p2, offset):
        x1, y1 = p1
        x2, y2 = p2
        afstand_x = abs(x1 - x2)
        afstand_y = abs(y1 - y2)
        afstand_pts = np.sqrt((afstand_x ** 2) + (afstand_y ** 2))
        return afstand_pts <= offset

    @staticmethod
    def is_line_connected_to_shape(line, shape, offset):
        p1 = line.p1
        p2 = line.p2
        x, y, h, w = shape
        # line zou altijd ongveer in midden van shape
        ver_center = w / 2
        hor_center = h / 2

        up_p = (x + ver_center, y, 0)
        down_p = (x + ver_center, y + h, 1)
        right_p = (x + w, y + hor_center, 2)
        left_p = (x, y + hor_center, 3)
        l_points = [up_p, down_p, right_p, left_p]

        for point in l_points:
            x1, y1, direction = point
            p = (x1, y1)
            if Shape.are_points_in_range(p1, p, offset) or Shape.are_points_in_range(p2, p, offset):
                x, y, direction = point
                return True, direction
        else:
            return False, None
