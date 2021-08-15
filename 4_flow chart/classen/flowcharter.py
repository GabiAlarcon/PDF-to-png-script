import cv2
import numpy as np
import pytesseract
from classen.line import Line
from classen.shape import Shape
import re
import copy


class FlowCharter:
    def __init__(self):
        self.lines = []
        self.root = None
        self.shapes = []

    def connect_shapes(self, root, offset):
        # alle shapes die direct met elkaar vebonden zijn zullen zich verbinden
        # via een binary tree en een recursive functie
        # indien er geen andere shape is aan het einde van de line
        # zult die unconnected line ingevuld worden voor verder verwerking
        for connected_line in root.lines:
            try:
                line = connected_line['line']
                direction = connected_line['direction']
                # p = root.get_other_end(line, direction, offset)
                for shape in self.shapes:
                    is_line_touching = shape.is_line_connected(line, offset)
                    if not shape == root and is_line_touching:
                        if direction == 2:
                            # visit neighbour
                            root.neighbour = shape
                            self.connect_shapes(shape, offset)
                        if direction == 1:
                            # visit child
                            root.child = shape
                            self.connect_shapes(shape, offset)
                        if direction == 0:
                            # parent
                            root.parent = shape
                        if direction == 3:
                            # upper_neighbour
                            root.upper_neighbour = shape
                        break
                else:
                    root.unconnected_lines.append(connected_line)
            except Exception as e:
                # todo:/ implement log system
                print(e)

    def get_connected_lines(self, offset):
        con_lines = []
        result = []
        for shape in self.shapes:
            for connected_line in shape.lines:
                line = connected_line['line']
                direction = connected_line['direction']
                if line not in shape.unconnected_lines:
                    con_lines.append(line)

        for line in con_lines:
            counter = 0
            for shape in self.shapes:
                if shape.is_line_connected(line, offset):
                    counter += 1
            if counter > 1 and line not in result:
                result.append(line)
        return result

    def get_one_side_connected_line(self, offset):
        result = []
        for line in self.lines:
            counter = 0
            for shape in self.shapes:
                if shape.is_line_connected(line, offset):
                    counter += 1
            if 1 == counter and line not in result:
                result.append(line)
        return result

    def print_all_shapes(self, root):
        # handig voor testen
        print('ID=', root.id, root.write_shape())
        if root.neighbour is not None:
            print('neighbour')
            self.print_all_shapes(root.neighbour)
        if root.child is not None:
            print('child')
            self.print_all_shapes(root.child)

    def get_shape_by_text(self, text):
        for shape in self.shapes:
            if shape.tekst == text:
                return shape

    def goto_other_end(self, direction, line, offset):
        x00, y00 = line.p1
        x01, y01 = line.p2
        # direction 2 go to boven links
        # direction 1 go to beneden links
        if direction == 2:
            p = (min(x00, x01), min(y00, y01))
        elif direction == 1:
            p = (min(x00, x01), max(y00, y01))  # go to beneden links
        for x in range(5):  ##AANPASSEN
            x0, y0 = p
            for l in self.lines:
                if l.is_point_in_segment(p, offset):
                    x1, y1 = l.p1
                    x2, y2 = l.p2
                    if direction == 2:
                        p = (min(x0, x1, x2), min(y0, y1, y2))
                    elif direction == 1:
                        p = (min(x0, x1, x2), max(y0, y1, y2))  # go to beneden links

        return p

    def give_visualisation(self, image, output_file, off_s):
        # FOR TESTING ONLY
        # off_s = 15
        radius = int(off_s / 2)
        tick = -1
        color = (0, 255, 0)
        visu_imag = np.copy(image) * 0  # creating a blank to draw lines on
        if len(self.shapes) > 0:
            for shape in self.shapes:
                x, y, h, w = shape.rectangle
                ver_l = int(w / 2)
                hor_l = int(h / 2)
                start_point = (x, y)
                end_point = (x + w, y + h)
                color = (255, 255, 255)
                thickness = -1
                visu_imag = cv2.rectangle(visu_imag, start_point, end_point, color, thickness)
                # visu_imag = cv2.line(visu_imag,(x,y+hor_l), (x+w,y+hor_l),(0,0,255), 2)

        if len(self.lines) > 0:
            for line in self.lines:
                cv2.line(visu_imag, line.p1, line.p2, (0, 0, 255), 3)

                for l in self.lines:
                    if line.is_line_over(l, off_s):
                        # and get_direction(line) == get_direction(l):
                        p1 = line.p1
                        p2 = line.p2
                        if l.is_point_in_segment(p1, off_s):
                            visu_imag = cv2.circle(visu_imag, p1, radius, color, tick)
                        if l.is_point_in_segment(p2, off_s):
                            visu_imag = cv2.circle(visu_imag, p2, radius, color, tick)

        cv2.imwrite(output_file, visu_imag)

    def draw_detected_shapes(self, image):
        visu_imag = image.copy()
        # font
        font = cv2.FONT_HERSHEY_SIMPLEX
        # fontScale
        fontScale = 1
        # Line thickness of 2 px
        text_thickness = 5
        color_solid = (255, 0, 0)
        color = (0, 0, 0)

        poly_color = (0, 255, 0)
        poly_tickness = 2

        if len(self.shapes) > 0:
            for shape in self.shapes:
                x, y, h, w = shape.rectangle
                start_point = (x, y)
                end_point = (x + w, y + h)

                thickness = 4
                visu_imag = cv2.rectangle(visu_imag, start_point, end_point, color_solid, thickness)
                visu_imag = cv2.polylines(visu_imag, shape.points, True, poly_color, poly_tickness)
                visu_imag = cv2.putText(visu_imag, shape.vorm, (int(x + 10), int(y + h / 2)), font,
                                        fontScale, color, text_thickness, cv2.LINE_AA)
        return visu_imag

    def draw_shapes(self, image, shapes, color=None):
        visu_imag = image.copy()
        if color is None:
            color = (255, 0, 0)
        thickness = -1
        for shape in shapes:
            x, y, h, w = shape.rectangle
            start_point = (x, y)
            end_point = (x + w, y + h)
            visu_imag = cv2.rectangle(visu_imag, start_point, end_point, color, thickness)
        return visu_imag

    def draw_detected_lines(self, image, lines, o_color=None, off_s=None):
        radius = 0
        if off_s is not None:
            radius = int(off_s / 2)
        tick = -1
        color = (0, 0, 0)
        visu_imag = image.copy()
        line_color = (0, 0, 255)
        if o_color is not None:
            line_color = o_color
        if len(lines) > 0:
            for line in lines:
                visu_imag = cv2.line(visu_imag, line.p1, line.p2, line_color, 3)
                for l in lines:
                    if off_s is not None:
                        if line.is_line_over(l, off_s):
                            # and get_direction(line) == get_direction(l):
                            p1 = line.p1
                            p2 = line.p2
                            if l.is_point_in_segment(p1, off_s):
                                visu_imag = cv2.circle(visu_imag, p1, radius, color, tick)
                            if l.is_point_in_segment(p2, off_s):
                                visu_imag = cv2.circle(visu_imag, p2, radius, color, tick)
        return visu_imag

    def draw_current_shape(self, image, current_shape, color=None):
        visu_imag = image.copy()
        if color is None:
            color = (255, 0, 0)
        thickness = -1
        x, y, h, w = current_shape.rectangle
        start_point = (x, y)
        end_point = (x + w, y + h)
        visu_imag = cv2.rectangle(visu_imag, start_point, end_point, color, thickness)

        return visu_imag

    def crop_image(self, initial_image, start_x=0, start_y=0, hoogte=0, breedte=0):
        # CROP IMAGE
        h = 0
        w = 0
        a = 0
        if len(initial_image.shape) == 2:
            h, w = initial_image.shape
        elif len(initial_image.shape) == 3:
            h, w, a = initial_image.shape
        h -= hoogte
        w -= breedte

        eind_y = h

        eind_x = w
        img = initial_image.copy()

        cropped_image = img[start_y:eind_y, start_x:eind_x]
        return cropped_image

    def ResizeWithAspectRatio(self, image, width=None, height=None, inter=cv2.INTER_AREA):
        dim = None
        (h, w) = image.shape[:2]

        if width is None and height is None:
            return image
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))

        return cv2.resize(image, dim, interpolation=inter)

    def thresh_otsu(self, image, bluring):
        """
        :param image: original image in Gray Scale
        :param bluring: matrix size for the Gaussian blurring
        :return: the otsu background and foreground
        """
        # apply thresholds
        ret, thresh = cv2.threshold(image, 250, 255, cv2.CHAIN_APPROX_NONE)
        gaussian_blured = cv2.GaussianBlur(thresh, (bluring, bluring), 0)
        ret1, thresh_otsu = cv2.threshold(gaussian_blured,
                                          0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return thresh_otsu

    @staticmethod
    def st_thresh_otsu(image, bluring):
        # apply thesholds
        ret, thresh = cv2.threshold(image, 250, 255, cv2.CHAIN_APPROX_NONE)
        gaussian_blured = cv2.GaussianBlur(thresh, (bluring, bluring), 0)
        ret1, thresh_otsu = cv2.threshold(gaussian_blured, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # find contours CHAIN_APPROX_SIMPLE for only points
        return thresh_otsu

    @staticmethod
    def st_get_bin_inv_thresh(bin_thr_inv, image):
        imgGry = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, inv_bin_tresh = cv2.threshold(imgGry, bin_thr_inv, 255, cv2.THRESH_BINARY_INV)
        return inv_bin_tresh

    def get_bin_inv_thresh(self, bin_thr_inv, image):
        """
        :param bin_thr_inv:  threshold value
        :param image: image with normal colors
        :return: binary inverted image
        """
        imgGry = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, inv_bin_tresh = cv2.threshold(imgGry, bin_thr_inv, 255, cv2.THRESH_BINARY_INV)
        return inv_bin_tresh

    def detect_shapes(self, image, bluring, offset, aproximation=0.02):
        # **************************
        self.shapes.clear()
        h, w = image.shape
        # h_big = start_y + h
        # w_big = w

        thresh_otsu = self.thresh_otsu(image, bluring)
        # find contours CHAIN_APPROX_SIMPLE for only points
        contours, hierarchy = cv2.findContours(thresh_otsu, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            approx = cv2.approxPolyDP(contour, aproximation * cv2.arcLength(contour, True), True)
            rec_shape = None
            vorm = ''
            if len(approx) == 3:
                continue
            elif len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                h_big, w_big = image.shape  # first rectangle in image
                if w == w_big and h_big == h:
                    continue

                # de points in de list zullen gebruikt om te vergelijken met de bounding rect
                # indien 2 punten binnen de offset passen is dit een rectangle anders is diamond
                # en offset van 10 px werd gebruikt
                points = []
                for p in range(4):
                    x_apr, y_apr = approx[p][0]
                    points.append((x_apr, y_apr))

                for p in points:
                    p2 = (x, y)
                    if Line.are_points_in_range(p, p2, offset):
                        vorm = "rectangle"
                        break
                else:
                    vorm = "diamont"
                rec_shape = (x, y, h, w)


            elif len(approx) == 5:
                continue
            elif len(approx) == 10:
                continue
            else:
                x, y, w, h = cv2.boundingRect(approx)
                center = [x + w / 2, y + w / 2]
                vorm = "circle"
                rec_shape = (x, y, h, w)

            shape = Shape(vorm, rec_shape)
            shape.points = [approx]
            self.shapes.append(shape)

        # return shapes

    def bind_text_to_shapes(self, image, OCR_config, thickness=5, af_hoogte=5):
        image = image.copy()
        # configuratie OCR
        for index, shape in enumerate(self.shapes):
            x, y, h, w = shape.rectangle
            box = image[y:y + h, x:x + w]

            if not shape.vorm == 'rectangle':
                # hier worden de outside lijnen verstopt
                points = shape.points
                cv2.drawContours(image, points, 0, (255, 255, 255), thickness)

            box = image[y:y + h, x:x + w]
            # Convert BGR to HSV
            hsv = cv2.cvtColor(box, cv2.COLOR_BGR2HSV)

            # define range of black color in HSV
            lower_val = np.array([0, 0, 0])
            upper_val = np.array([179, 100, 130])
            mask = cv2.inRange(hsv, lower_val, upper_val)
            # res = cv2.bitwise_and(box, box, mask=mask)
            res2 = cv2.bitwise_not(mask)
            box_tekst = pytesseract.image_to_string(res2, config=OCR_config)
            box_tekst = box_tekst.replace('', '')
            box_tekst = box_tekst.replace('\n', ' ')

            if len(box_tekst) > 0 and box_tekst[0] == ' ':
                box_tekst = box_tekst[1:-1]
            box_tekst = box_tekst.lower()
            box_tekst = re.sub("[^a-z\s\?]", "", box_tekst, 0, re.IGNORECASE | re.MULTILINE)

            shape.tekst = box_tekst

    def hide_shapes(self, original_image):
        if self.shapes is not None and len(self.shapes) > 0:
            image = None
            for shape in self.shapes:
                x, y, h, w = shape.rectangle
                start_point = (x, y)
                end_point = (x + w, y + h)
                color = (255, 255, 255)
                thickness = -1
                image = cv2.rectangle(original_image, start_point, end_point, color, thickness)
            return image
        else:
            return original_image

    def hide_lines(self, original_image, lines):
        # for l in h_lines:
        #    print(l)
        if len(lines) > 0:
            image = None
            for line in lines:
                image = cv2.line(original_image, line.p1, line.p2, (255, 255, 255), 3)
            return image
        else:
            return original_image

    def detect_lines(self, original_image, threshold, min_line_length, max_line_gap, chain_approx=False, lines=None):
        img_copy = original_image.copy()
        # HARDCODED VALUES **************
        # line recognition parameters
        rho = 1  # distance resolution in pixels of the Hough grid
        theta = np.pi / 180  # angular resolution in radians of the Hough grid
        # threshold = 45          # minimum number of votes (intersections in Hough grid cell) #optimalizatie was 45
        # min_line_length = 5    # minimum number of pixels making up a line #optimalizatie was 5
        # max_line_gap = 20      # maximum gap in pixels between connectable line segments
        kernel_size = 3
        low_threshold = 50  # low values for gray in image
        high_threshold = 150  # high values for gray in image
        # **************

        # verstopt de shapes voor gemakkelijker verwerking
        tmp_image = self.hide_shapes(img_copy)
        # verstopt de lines voor gemakkelijker verwerking
        if lines is not None:
            tmp_image = self.hide_lines(img_copy, lines)

        # Gray scale and CHAIN_APPROX_NONE, #GaussianBlur, #canny treshhold
        imgGry = cv2.cvtColor(tmp_image, cv2.COLOR_BGR2GRAY)
        thresh = imgGry
        # CHAIN_APPROX_NONE filter in image
        if chain_approx:
            ret, thresh = cv2.threshold(imgGry, 250, 255, cv2.CHAIN_APPROX_NONE)
        else:
            thresh = imgGry

        blur_gray = cv2.GaussianBlur(thresh, (kernel_size, kernel_size), 0)
        edges = cv2.Canny(blur_gray, low_threshold, high_threshold)

        # cv2.imshow('canny', edges)
        # Run Hough on edge detected image
        # Output "lines" is an array containing endpoints of detected line segments
        lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                                min_line_length, max_line_gap)

        # er zijn herhaalde lijnen die moeten gefilterd worden

        lines = [x[0] for x in lines]
        for index, l in enumerate(lines):
            x1, y1, x2, y2 = l
            line = Line((x1, y1), (x2, y2))
            lines[index] = line

        return lines
        # self.lines = lines

    def make_new_line(self, line1, line2):
        # make a new line dat merge 2 lines
        # of the same direction and gets the
        # a longer line
        # print("make line:")
        x1, y1 = line1.p1
        x2, y2 = line1.p2
        x3, y3 = line2.p1
        x4, y4 = line2.p2
        direction2 = line1.get_direction()
        direction = line2.get_direction()
        if direction == direction2:
            if direction:  # vertical
                min_y = min(y1, y2, y3, y4)
                max_y = max(y1, y2, y3, y4)
                l = Line((x1, min_y), (x1, max_y))
                # print(l.print_line())
                return l
            else:
                min_x = min(x1, x2, x3, x4)
                max_x = max(x1, x2, x3, x4)
                l = Line((min_x, y1), (max_x, y1))
                # print(l.print_line())
                return l
        else:
            # throu exception
            print('lines hebben niet dezelfde richting')
            pass

    def filter_equal_lines(self, offset, lines):
        changed = False
        for i, line in enumerate(lines):
            for line2 in lines:
                if line == line2 or i > lines.index(line2):
                    continue
                if line.is_line_close(line2, offset):
                    n_line = self.make_new_line(line, line2)
                    lines[i] = n_line
                    lines.remove(line2)
                    changed = True

        return lines, changed

    def eliminate_overlay_lines(self, lines, offset):
        changed = False
        for i, line in enumerate(lines):
            for line2 in lines:
                if line == line2 or i > lines.index(line2):
                    continue
                if not line == line2 and line.is_line_over(line2, offset):
                    n_line = self.make_new_line(line, line2)
                    lines[i] = n_line
                    lines.remove(line2)
                    changed = True
        return lines, changed

    def filter_lines(self, lines, offset):
        # recht zetten van de lijnen
        # en lijnen filteren van de lijst die hetzelfde richting en onder
        # afstand "offset" liggen
        lines = [l.make_stray() for l in lines]
        lines, changed = self.filter_equal_lines(offset, lines)
        while changed:
            lines, changed = self.filter_equal_lines(offset, lines)
        return lines

    def merge_lines(self, lines, offset):
        # lijn die over elkaar zijn in de lijst
        # of lijnen dat over een afstand "offset" liggen
        # verwijderen
        lines, changed = self.eliminate_overlay_lines(lines, offset)
        while changed:
            lines, changed = self.eliminate_overlay_lines(lines, offset)
        return lines

    def bind_lines_to_shapes(self, offset):
        for shape in self.shapes:
            for index, line in enumerate(self.lines):
                shape.set_line(line, offset)
        return self.shapes

    def find_root_of_chart(self, find_by_position=True, find_by_text=False, text=''):
        # get de root shape and tale of the flow chart
        # enkel root is eigenlijk nodig
        root = None
        for shape in self.shapes:
            shape.id = id(shape)
        if find_by_position:
            for shape in self.shapes:
                if not root == None:
                    x, y, h, w = root.rectangle
                    x2, y2, h2, w2 = shape.rectangle
                    if y > y2:
                        root = shape
                else:
                    root = shape
            self.root = root
            return self.root
        elif find_by_text:
            if text:
                root = self.get_shape_by_text(text)
                self.root = root
                return self.root
            else:
                # through exception
                pass

    def bind_unconnected_lines_to_shape(self, offset):
        for shape in self.shapes:
            if shape.has_unconnected_lines():
                for conn_l in shape.unconnected_lines:
                    line = conn_l['line']
                    direction = conn_l['direction']
                    line_direction = line.get_direction()
                    # als linedirection vertical is dan moet de direction van uit shape naar beneden gaan
                    # als line direction horizontaal is dan naar rechts
                    if (line_direction and direction == 1) or (not line_direction and direction == 2):
                        p = shape.get_other_end(line, direction, offset)  # other end of de unconnected line
                        for l in self.lines:
                            l_dir = l.get_direction()
                            if l.is_point_in_segment(p, offset) and not line_direction == l_dir:
                                # verbind shape met shape trough line
                                p2 = self.goto_other_end(direction, l, offset)
                                for sh in self.shapes:
                                    if sh.is_point_touching(p2, offset):
                                        if direction == 0:  # shape is parent
                                            shape.parent = sh
                                        elif direction == 1:  # shape is child
                                            shape.child = sh
                                        elif direction == 2:  # is neighbour
                                            shape.neighbour = sh
                                        elif direction == 3:  # is upper_neighbour
                                            shape.upper_neighbour = sh
        return self.shapes

    def get_line_lenghts(self):
        return [x.get_length() for x in self.lines]

    def eliminate_short_lines(self, lines, length):
        lines = sorted(lines, key=lambda x: x.get_length())
        self.lines = [x for x in lines if x.get_length() > length]

    def get_unvalidated_shape(self):
        unvalidated_shapes = [shape for shape in self.shapes if shape.is_family_invalid()]
        return unvalidated_shapes

    def set_direct_conn(self, offset):
        for line in self.lines:
            for line2 in self.lines:
                if line == line2:
                    continue
                if line.is_connected(line2, offset):
                    line.connected_lines.append(line2)

    def walk_connections(self, root):
        root.visited = True
        connections = copy.deepcopy(root.connected_lines)
        for line in connections:
            if not line.visited:
                connections.extend(self.walk_connections(line))
        return list(set(copy.deepcopy(connections)))

    def set_all_lines_to_non_visited(self):
        for line in self.lines:
            line.visited = False

    def walk_connections_from_list(self, one_siders):
        for line in one_siders:
            connections = self.walk_connections(line)
            line.connected_lines.extend(connections)
            self.set_all_lines_to_non_visited()

    def apply_line_binding(self, one_siders, offset):
        self.set_direct_conn(offset)
        self.walk_connections_from_list(one_siders)
        for line in one_siders:
            partners = line.get_partners(one_siders)
            # all partners zullen hetzelfde partners hebben
            for partner in partners:
                partner.connected_lines.extend(partners)
            # eliminate doubles
            line.connected_lines = list(set(line.connected_lines))

    def print_line_connections(self, one_siders):
        # todo:/ testing and or debugging
        for line in one_siders:
            partners = line.get_partners(one_siders)
            pr_nm = [x.name for x in partners]
            print(line.name, 'has {} connections'.format(len(set(line.connected_lines))))
            print('from where {} are in the given list'.format(len(partners)))
            str_line = 'partners:\n\t'
            str_line += ",".join(pr_nm)
            print(str_line)

    def bind_shapes_to_onesiders(self, one_siders, offset):
        for shape in self.shapes:
            for line in one_siders:
                if shape.is_line_connected(line, offset):
                    shape.one_siders.extend(line.connected_lines)
                # eliminate dubble
            shape.one_siders = list(set(shape.one_siders))

    def get_possible_shapes(self, shape):
        def are_shape_connected(sh1, sh2):
            if len(sh1.one_siders) > 1 and len(sh2.one_siders) > 1:
                for line in sh1.one_siders:
                    if line in sh2.one_siders:
                        return True
            return False

        if len(shape.one_siders) > 1:
            # temporal list of shapes with onesiders
            temp = [sh for sh in self.shapes if len(sh.one_siders) > 1]
            result = []

            for sh in temp:
                if not shape == sh:
                    if are_shape_connected(sh, shape):
                        result.append(sh)
            return result
