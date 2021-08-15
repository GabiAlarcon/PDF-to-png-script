# https://likegeeks.com/python-gui-examples-tkinter-tutorial/
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox
# from tkinter.ttk import Combobox, Style
import threading
import cv2
from PIL import ImageTk, Image
from classen.flowcharter import FlowCharter as fc
from classen.shape import Shape


class Verwerker:
    @staticmethod
    def crop_img(image, y, afhoogte):
        # image = Pil image
        # y start of the image
        # bottom = height - afhoogte
        if image is not None:
            width, height = image.size
            # Setting the points for cropped image
            left = 0
            top = int(y)
            right = int(width)
            bottom = int(height - afhoogte)
            return image.crop((left, top, right, bottom))

    @staticmethod
    def crop_cv2_image_absolute(initial_image, y, x, h, w):
        if initial_image is not None:
            img = initial_image.copy()
            cropped_image = img[y:y + h, x:x + w]
            return cropped_image

    @staticmethod
    def crop_cv2_image_by_resting(initial_image, start_y, hoogte, start_x=0, breedte=0):

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

    @staticmethod
    def get_bin_inversion(img_path, binv):
        if img_path is not None:
            img = cv2.imread(img_path)
            cv2_img = fc.st_get_bin_inv_thresh(binv, img)
            # conver cv2 format naar pil
            im_pil = Image.fromarray(cv2_img)
            return im_pil

    @staticmethod
    def cv2_to_pil(cv2_img):
        im_pil = Image.fromarray(cv2_img)
        return im_pil

    @staticmethod
    def resize_keep_ratio(basewidth, image):
        wpercent = (basewidth / float(image.size[0]))
        hsize = int((float(image.size[1]) * float(wpercent)))
        return image.resize((basewidth, hsize), Image.ANTIALIAS)


class ChangeFamilyPopUp:
    def __init__(self, parent, shape):
        self.main = parent  # type: App
        top = self.top = Toplevel(parent)
        top.protocol("WM_DELETE_WINDOW", self.destroy_window)
        top.wm_title('Changing family member!')
        self.family = ['parent', 'big brother', 'brother', 'child', 'None']
        self.shape = shape
        self.__create_widgets()
        self.top.mainloop()

    def __create_widgets(self):
        Label(self.top, text='Which member do you want to change?').grid(column=0, row=0, padx=5, pady=5)
        self.cbx_fml_choise = Combobox(self.top, values=self.family, state='readonly')
        self.cbx_fml_choise.grid(column=1, row=0, padx=5, pady=5)
        self.cbx_fml_choise.current(self.family.index('None'))
        Button(self.top, text='Choose', command=self.destroy_window).grid(column=0, row=1, padx=5, pady=5)

    def destroy_window(self):
        choice = self.cbx_fml_choise.get()
        self.main.change_family_member(choice)
        self.top.destroy()


class InputFrame(Frame):
    def __init__(self, container, option = None):
        super().__init__(container)
        self["style"] = "Card"
        self.img_path = None
        self.binv_img = None
        self.otsu_img = None
        self.orig_img = None
        self.approximation = None
        self.charter = None
        self.pil_image = None
        self.container = container  # type: App
        self.dtc_shapes_img = None
        self.__create_widgets()
        # self.configure(bg='#a8f0c8')
        self.deactivate_children()
        self.is_image_load = False
        self.is_image_cropped = False
        self.is_binv_ready = False
        self.is_otsu_ready = False
        self.is_shape_detection_ready = False

    def __create_widgets(self):
        Label(self, text='Parameters', font=("Arial Bold", 15)).grid(column=0, row=0)
        Label(self, text='Crop top').grid(column=0, row=1, sticky=W)
        Label(self, text='Crop bottom').grid(column=0, row=2, sticky=W)
        Label(self, text='Binary inversion').grid(column=0, row=4, sticky=W)
        Label(self, text='Otsu kernel size').grid(column=0, row=5, sticky=W)
        Label(self, text='Shape resolution').grid(column=0, row=6, sticky=W)
        Label(self, text='Rectangle distance').grid(column=0, row=8, sticky=W)
        self.spb_y_var = IntVar()
        self.spb_y = Spinbox(self, from_=0, to=1000, textvariable=self.spb_y_var, command=self.crop, increment=10, state='readonly')
        self.spb_y.grid(column=1, row=1)

        self.spb_height_var = IntVar()
        self.spb_height = Spinbox(self, from_=0, to=1000,textvariable=self.spb_height_var ,command=self.crop, increment=10, state='readonly')
        self.spb_height.grid(column=1, row=2)

        self.btn_crop = Button(self, text='Crop', command=self.crop)
        self.btn_crop.grid(column=2, row=1, rowspan=2, sticky=N + W + S + E)


        self.spb_binv_var = IntVar()
        self.spb_binv = Spinbox(self, from_=0, to=254, textvariable=self.spb_binv_var, command=self.apply_bin_inversion, increment=1, state='readonly')
        self.spb_binv.grid(column=1, row=4)

        self.btn_binv = Button(self, text='Apply', command=self.apply_bin_inversion)
        self.btn_binv.grid(column=2, row=4, sticky=N + W + S + E)

        self.spb_otsu_blur_var = IntVar()
        self.spb_otsu_blur = Spinbox(self, from_=29, to=79, textvariable=self.spb_otsu_blur_var, command=self.apply_otsu, increment=2, state='readonly')
        self.spb_otsu_blur.grid(column=1, row=5)

        self.btn_otsu = Button(self, text='Apply', command=self.apply_otsu)
        self.btn_otsu.grid(column=2, row=5, sticky=N + W + S + E)

        self.spb_aprx_var = IntVar()
        self.spb_aprx_var.set(50)
        self.spb_aprx = Spinbox(self, from_=1, to=100,textvariable=self.spb_aprx_var, command=self.aprox_changed, state='readonly')
        self.spb_aprx.grid(column=1, row=6)

        self.btn_detect_shapes = Button(self, text='Detect shapes', command=self.aprox_changed)
        self.btn_detect_shapes.grid(column=2, row=6, sticky=N + W + S + E)

        self.ent_aprx = Entry(self, state="readonly")
        self.ent_aprx.grid(column=0, row=7, columnspan=4, sticky=N + W + S + E)

        self.spb_offset_var = IntVar()
        self.spb_offset_var.set(20)
        self.spb_offset = Spinbox(self, from_=0, to=30, command=self.offset_changed, textvariable=self.spb_offset_var, state='readonly')
        self.spb_offset.grid(column=1, row=8)

        self.btn_rectangle_offset = Button(self, text="Apply", command=self.offset_changed)
        self.btn_rectangle_offset.grid(column=2, row=8, sticky= W + E)
        for widget in self.winfo_children():
            widget.grid(padx=5, pady=5)
            if isinstance(widget, Button):
                widget["style"] = "AccentButton"

    def deactivate_children(self):
        for widget in self.winfo_children():
            if not isinstance(widget, Label):
                widget.config(state=DISABLED)

    def activate_children(self):
        for widget in self.winfo_children():
            if not isinstance(widget, Spinbox):
                widget.config(state=NORMAL)
            # else:
            #     widget.config(state='readonly')

    def activate_crop_section(self):
        # self.spb_y['state'] = 'readonly'
        # self.spb_height['state'] = 'readonly'
        self.spb_y['state'] = NORMAL
        self.spb_height['state'] = NORMAL
        self.btn_crop['state'] = NORMAL

    def activate_mask_section(self):
        # self.spb_binv['state'] = 'readonly'
        self.spb_binv['state'] = NORMAL
        self.btn_binv['state'] = NORMAL

    def activate_otsu_section(self):
        # self.spb_otsu_blur['state'] = 'readonly'
        self.spb_otsu_blur['state'] = NORMAL
        self.btn_otsu['state'] = NORMAL

    def activate_detect_section(self):
        # self.spb_aprx['state'] = 'readonly'
        # self.spb_offset['state'] = 'readonly'
        self.spb_aprx['state'] = NORMAL
        self.spb_offset['state'] = NORMAL
        self.btn_detect_shapes['state'] = NORMAL
        self.btn_rectangle_offset['state'] = NORMAL


    def crop(self):
        if self.img_path is not None:
            image = Image.open(self.img_path)
            self.pil_image = image
            im1 = self.crop_img(image)
            orig_img = cv2.imread(self.img_path)
            start_y = int(self.spb_y_var.get())
            if start_y > 1000:
                start_y = 1000
                self.spb_y_var.set(1000)
            afhoogte = int(self.spb_height_var.get())
            if afhoogte > 1000:
                afhoogte = 1000
                self.spb_height_var.set(1000)
            self.orig_img = Verwerker.crop_cv2_image_by_resting(orig_img, start_y=start_y, hoogte=afhoogte)
            self.is_image_cropped = True
            self.container.manage_program_states()
            self.container.update_image(im1)

    def crop_img(self, image):
        # return a PIL Image
        width, height = image.size
        start_y = int(self.spb_y_var.get())
        if start_y > 1000:
            self.spb_y_var.set(1000)
            start_y = 1000
        afhoogte = int(self.spb_height_var.get())
        if afhoogte > 1000:
            afhoogte = 1000
            self.spb_height_var.set(1000)
        # Setting the points for cropped image
        left = 0
        top = int(start_y)
        right = int(width)
        bottom = int(height - afhoogte)
        return image.crop((left, top, right, bottom))

    def get_bin_inversion(self):
        if self.img_path is not None:
            bin_inversion = int(self.spb_binv_var.get())
            if bin_inversion  > 254:
                bin_inversion = 254
                self.spb_binv_var.set(254)
            cv2_image = fc.st_get_bin_inv_thresh(bin_inversion, self.orig_img)
            self.container.cv2imag = cv2_image
            self.binv_img = cv2_image
            # conver cv2 format naar pil
            im_pil = Image.fromarray(self.container.cv2imag)
            self.is_binv_ready = True
            self.container.manage_program_states()
            return im_pil

    def apply_bin_inversion(self):
        if self.img_path is not None:
            bin_inverted = self.get_bin_inversion()
            self.container.update_image(bin_inverted)
            self.btn_otsu['state'] = NORMAL
            self.spb_otsu_blur['state'] = NORMAL

    def validate_otsu_val(self):
        if int(self.spb_otsu_blur_var.get()) > 79:
            self.spb_otsu_blur_var.set(79)
        if int(self.spb_otsu_blur_var.get()) < 29:
            self.spb_otsu_blur_var.set(29)
        if int(self.spb_otsu_blur_var.get()) % 2 == 0:
            val = int(self.spb_otsu_blur_var.get()) + 1
            self.spb_otsu_blur_var.set(val)

    def apply_otsu(self):
        if self.binv_img is not None and self.img_path is not None:
            self.validate_otsu_val()
            cv2_image = fc.st_thresh_otsu(self.binv_img, int(self.spb_otsu_blur_var.get()))
            self.otsu_img = cv2_image
            self.is_otsu_ready = True
            self.container.manage_program_states()
            self.container.update_image(Verwerker.cv2_to_pil(self.otsu_img))

    def aprox_changed(self):
        minimun = 1
        maximun = 41
        if int(self.spb_aprx_var.get()) > 100:
            self.spb_aprx_var.set(100)
        res = '{:.6f}'.format(float((maximun - minimun) / 100 / 1000))
        self.approximation = float('{:.3f}'.format(float(res) * int(self.spb_aprx_var.get())))
        self.ent_aprx['text'] = self.approximation
        self.detect_shapes()

    def detect_shapes(self, offset=20):
        if not self.binv_img is None and not self.img_path is None:
            self.validate_otsu_val()
            charter = fc()
            charter.detect_shapes(image=self.binv_img, bluring=int(self.spb_otsu_blur_var.get()), offset=offset,
                                  aproximation=self.approximation)
            self.charter = charter

            self.dtc_shapes_img = charter.draw_detected_shapes(self.orig_img)
            im_pil = Verwerker.cv2_to_pil(self.dtc_shapes_img)
            self.container.update_image(im_pil)
            self.is_shape_detection_ready = True
            self.container.manage_program_states()

    def offset_changed(self):
        if int(self.spb_offset_var.get()) > 30:
            self.spb_offset_var.set(30)
        offset = int(self.spb_offset_var.get())
        self.detect_shapes(offset)

    def get_params(self):
        self.validate_otsu_val()
        if int(self.spb_y_var.get()) > 1000:
            self.spb_y_var.set(1000)
        if int(self.spb_height_var.get()) > 1000:
            self.spb_height_var.set(1000)
        data = {'star_y': int(self.spb_y_var.get()), 'height': int(self.spb_height_var.get()),
                'binv': int(self.spb_binv_var.get()), 'otsu_blur': int(self.spb_otsu_blur_var.get()),
                'offset': int(self.spb_offset_var.get()), 'approx': self.approximation, 'img_path': self.img_path,
                'orig_image': self.orig_img, 'charter': self.charter, 'pil_image': self.pil_image}
        # data = self.testing_params()
        return data

    def testing_params(self):
        img_path = r'C:/Users/GA/Documents/automation workshop/python/data/images/1220_1520/1220_1520_pag-186.jpg'

        start_y = 560
        afhoogte = 420
        orig_img = cv2.imread(img_path)
        # cv2.imshow('test', orig_img)
        orig_img = Verwerker.crop_cv2_image_by_resting(orig_img, start_y=start_y, hoogte=afhoogte)

        data = {'star_y': int(560), 'height': int(420), 'binv': int(235),
                'otsu_blur': int(45), 'offset': int(20),
                'approx': 0.021, 'img_path': img_path, 'orig_image': orig_img,
                'charter': self.charter, 'pil_image': self.pil_image}
        return data

    def make_testing_objects(self):
        # todo:/ opm enkel voor testing
        img_path = r'C:/Users/GA/Documents/automation workshop/python/data/images/1220_1520/1220_1520_pag-186.jpg'
        pil_image = Image.open(img_path)
        self.pil_image = pil_image

        start_y = 560
        afhoogte = 420
        orig_img = cv2.imread(img_path)
        orig_img = Verwerker.crop_cv2_image_by_resting(orig_img, start_y=start_y, hoogte=afhoogte)
        self.charter = fc()
        cv2_image = fc.st_get_bin_inv_thresh(235, orig_img)
        self.charter.detect_shapes(image=cv2_image, bluring=int(45), offset=20,
                                   aproximation=0.021)


class FlowChartFrame(Frame):
    def __init__(self, container):
        super().__init__(container)
        self["style"] = "Card"
        self.container = container  # type: App
        self.params = None
        # self.configure(bg='#a8f0c8')
        self.charter = None  # type: fc
        self.img = None
        self.is_flow_chart_ready = False
        self.merging_offset = IntVar()
        self.merging_offset.set(15)
        self.thread_detect_lines = threading.Thread(target=self.detect_lines)
        self.thread_connect_shapes = threading.Thread(target=self.bind_text)
        self.columnconfigure(0, weight=1)
        self.__create_widgets()
        self.deactivate_children()

    def __create_widgets(self):
        Label(self, text='Line detection section', font=("Arial Bold", 15)).grid(column=0, row=0)
        Label(self, text='Line to line distance').grid(column=0, row=1, sticky=W)
        Label(self, text='Line to shape distance').grid(column=0, row=2, sticky=W)
        Label(self, text='Line to line merging distance').grid(column=0, row=3, sticky=W)
        # filter_offset = 15
        # offset = 15  # hard coded value
        self.spb_filter_offset_var = IntVar()
        self.spb_filter_offset_var.set(15)
        self.spb_filter_offset = Spinbox(self, from_=1, to=20, textvariable=self.spb_filter_offset_var )
        self.spb_filter_offset.grid(column=1, row=1)

        self.spb_connection_offset_var = IntVar()
        self.spb_connection_offset_var.set(15)
        self.spb_connection_offset = Spinbox(self, from_=1, to=20, textvariable=self.spb_connection_offset_var)
        self.spb_connection_offset.grid(column=1, row=2)

        self.spb_merging_offset_var = IntVar()
        self.spb_merging_offset_var.set(10)
        self.spb_merging_offset = Spinbox(self, from_=1, to=20,
                                          textvariable=self.spb_merging_offset_var)

        self.ent_info_var = StringVar()
        self.ent_info = Entry(self, state="readonly", textvariable=self.ent_info_var)
        self.ent_info.grid(column=0, row=4, columnspan=2, sticky=N + S + W + E)

        self.spb_merging_offset.grid(column=1, row=3)
        self.btn_ocr = Button(self, text='Connect All', command=self.run_connect_shapes)
        self.btn_ocr.grid(column=1, row=5, sticky=S + W + E)

        for widget in self.winfo_children():
            widget.grid(padx=3, pady=3)
            if isinstance(widget, Button):
                widget["style"] = "AccentButton"

    def get_all_params(self):
        data = self.container.get_ini_params()
        if data is not None:
            self.params = data

    def deactivate_children(self):
        for widget in self.winfo_children():
            if not isinstance(widget, Label):
                widget.config(state=DISABLED)

    def activate_children(self):
        for widget in self.winfo_children():
            if isinstance(widget,Entry):
                continue
            widget.config(state=NORMAL)

    def bind_text(self):
        # message to user
        self.ent_info_var.set('finding shapes...')
        self.get_all_params()
        charter = self.charter = self.params['charter']
        img = self.params['orig_image']

        # message to user
        self.ent_info_var.set('binding text to shapes...')
        OCR_config = r'--oem 3 --psm 6'
        tickness = 11
        afhoogte = 8
        charter.bind_text_to_shapes(img, OCR_config, thickness=tickness)

        # message to user
        self.ent_info_var.set('shapes are ready...')
        self.thread_connect_shapes = threading.Thread(target=self.bind_text)
        self.run_detect_lines()

    def run_connect_shapes(self):
        if not self.thread_connect_shapes.is_alive():
            self.thread_connect_shapes.start()
        else:
            self.ent_info['text'] = 'another process is running!...'

    def run_detect_lines(self):
        if not self.thread_detect_lines.is_alive() and not self.thread_connect_shapes.is_alive():
            self.thread_detect_lines.start()
        else:
            self.ent_info['text'] = 'another process is running!...'

    def detect_lines(self):
        # message to user:
        self.ent_info['text'] = 'detecting lines...'
        # HARD CODED VALUES
        # eerste filtering parameter
        treshholding1 = 45
        max_line_gap1 = 20
        chain_aprox1 = False  # voor clean stop was true pg 35 False
        # tweede filtering parameters
        treshholfing2 = 20  # voor clean stop was 27
        max_line_gap2 = 15
        chain_aprox2 = False
        if int(self.spb_filter_offset_var.get()) > 20:
            self.spb_filter_offset_var.set(20)
        if int(self.spb_merging_offset_var.get()) > 20:
            self.spb_merging_offset_var.set(20)
        # offset voor aan te geven dat een lijn dichtbij is
        filter_offset = int(self.spb_filter_offset_var.get())
        merging_offset = int(self.spb_merging_offset_var.get())
        short_line_length = merging_offset

        self.get_all_params()
        charter = self.charter
        img = self.params['orig_image']

        #                   Detecting van lijnen
        lines = charter.detect_lines(img, treshholding1, 5, max_line_gap1, chain_aprox1)
        # Filteren van lijnen
        # Merging lijnen kan niet tegelijker tijd gebeuren met filteren van lijnen er worden lijnen
        # in verkeerde manier kwijt geraakt dus er is een mogelijkheid om kleinere lijnen te hebben.
        f_lines = charter.filter_lines(lines, filter_offset)
        # HIDE bewerkte lijnen and shapes find more lines
        # second detect
        charter.lines = f_lines
        lines = charter.detect_lines(img, treshholfing2, 5, max_line_gap2, chain_aprox2, f_lines)
        # Second Filtering van lijnen
        f_lines2 = charter.filter_lines(lines, filter_offset)

        f_lines = f_lines + f_lines2
        f_lines = charter.filter_lines(f_lines, filter_offset)
        charter.lines = f_lines
        merged_lines = charter.merge_lines(f_lines, merging_offset)
        charter.lines = merged_lines
        charter.eliminate_short_lines(f_lines, short_line_length)
        self.connect_shapes()

        # message to user
        self.ent_info['text'] = 'lines are ready...'
        self.thread_detect_lines = threading.Thread(target=self.detect_lines)

    def connect_shapes(self):
        img = self.params['orig_image']
        if int(self.spb_connection_offset_var.get()) > 20:
            self.spb_connection_offset_var.set(20)
        offset = int(self.spb_connection_offset_var.get())
        root = self.charter.find_root_of_chart()
        self.charter.bind_lines_to_shapes(offset)
        self.charter.connect_shapes(root, offset=offset)
        self.charter.bind_unconnected_lines_to_shape(offset)
        connected_lines = self.charter.get_connected_lines(offset)
        one_siders = self.charter.get_one_side_connected_line(offset)
        self.charter.apply_line_binding(one_siders, offset=offset)
        self.charter.bind_shapes_to_onesiders(one_siders, offset=offset)
        # bind shapes to onesiders

        # self.charter.print_line_connections(one_siders)
        self.container.founded_shapes = self.charter.shapes

        merging_offset = int(self.spb_merging_offset_var.get())
        offset_oeo = merging_offset * 2

        c_color = (255, 255, 0)
        one_sider_color = (255, 0, 0)
        dtc_shapes = self.charter.draw_detected_shapes(img)
        dtc_lines = self.charter.draw_detected_lines(dtc_shapes, self.charter.lines)
        cnn_lines = self.charter.draw_detected_lines(dtc_lines, connected_lines, c_color)
        one_siders_lines = self.charter.draw_detected_lines(cnn_lines, one_siders, one_sider_color)
        self.img = one_siders_lines
        self.is_flow_chart_ready = True
        self.container.manage_program_states()
        img_detected = Verwerker.cv2_to_pil(self.show_invalid_shapes(one_siders_lines))
        self.container.update_image(img_detected)

    def show_invalid_shapes(self, img):
        color = (0, 0, 255)
        image = img.copy()
        for shape in self.charter.get_unvalidated_shape():
            image = self.charter.draw_current_shape(image, shape, color)
        return image


class EditShape(Frame):
    def __init__(self, container):
        super().__init__(container)
        self["style"] = "Card"
        self.img_path = None
        self.container = container  # type: App
        # self.configure(bg='#a8f0c8')
        self.shape = None
        self.vormen = ['circle', 'rectangle', 'diamont']
        self.family = ['parent', 'big brother', 'brother', 'child', 'None']
        self.shape_text = StringVar()
        self.shape_vorm = StringVar()
        self.parent_txt = StringVar()
        self.brother_txt = StringVar()
        self.big_brother_txt = StringVar()
        self.child_txt = StringVar()
        self.canvas_width = 300
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.__create_widgets()
        self.reset_values()
        self.changing_family = False
        self.deactivate_children()

    def __create_widgets(self):

        Label(self, text='Edit shapes', font=("Arial Bold", 15)).grid(column=0, row=0)
        Label(self, text='Shape text').grid(column=0, row=1, sticky=W)
        Label(self, text='Shape vorm').grid(column=0, row=2, sticky=W)
        Label(self, text='Family', font=("Arial Bold", 15)).grid(column=0, row=3, sticky=W)
        Label(self, text='Parent').grid(column=0, row=4, sticky=W)
        Label(self, text='Big brother').grid(column=0, row=5, sticky=W)
        Label(self, text='Brother').grid(column=0, row=6, sticky=W)
        Label(self, text='Child').grid(column=0, row=7, sticky=W)
        Label(self, text='Yes').grid(column=0, row=8, sticky=W)
        Label(self, text='No').grid(column=0, row=9, sticky=W)

        self.ent_sh_txt = Entry(self, textvariable=self.shape_text)
        self.ent_sh_txt.grid(column=1, row=1, columnspan=2, sticky=N + W + S + E)

        self.cbx_vorm_text = Combobox(self, values=self.vormen, state='readonly')
        self.cbx_vorm_text.grid(column=1, row=2, columnspan=2, sticky=N + W + S + E)

        self.ent_parent = Entry(self, state='readonly', textvariable=self.parent_txt)
        self.ent_parent.grid(column=1, row=4, sticky=N + W + S + E)

        self.btn_parent_show = Button(self, text='show', command=self.change_to_parent)
        self.btn_parent_show.grid(column=2, row=4)

        self.ent_big_brother = Entry(self, state='readonly', textvariable=self.big_brother_txt)
        self.ent_big_brother.grid(column=1, row=5, sticky=N + W + S + E)

        self.btn_bg_bro_show = Button(self, text='show', command=self.change_to_big_brother)
        self.btn_bg_bro_show.grid(column=2, row=5)

        self.ent_brother = Entry(self, state='readonly', textvariable=self.brother_txt)
        self.ent_brother.grid(column=1, row=6, sticky=N + W + S + E)

        self.btn_bro_show = Button(self, text='show', command=self.change_to_brother)
        self.btn_bro_show.grid(column=2, row=6)

        self.ent_child = Entry(self, state='readonly', textvariable=self.child_txt)
        self.ent_child.grid(column=1, row=7, sticky=N + W + S + E)

        self.btn_child_show = Button(self, text='show', command=self.change_to_child)
        self.btn_child_show.grid(column=2, row=7)

        self.cbx_yes = Combobox(self, values=self.family, state='readonly')
        self.cbx_yes.grid(column=1, row=8, columnspan=2, sticky=N + W + S + E)

        self.cbx_no = Combobox(self, values=self.family, state='readonly')
        self.cbx_no.grid(column=1, row=9, columnspan=2, sticky=N + W + S + E)

        self.cvs = Canvas(self, width=self.canvas_width, height=150, scrollregion=(0,0,200,200))
        self.cvs.grid(column=0, row=10, columnspan=3)
        vbar = Scrollbar(self, orient=VERTICAL)
        vbar.grid(column=2, row=10,sticky=E+N+S)
        vbar.config(command=self.cvs.yview)
        self.cvs.config(yscrollcommand=vbar.set)

        self.btn_change_fmly = Button(self, text='Change family', command=self.change_family)
        self.btn_change_fmly.grid(column=0, row=11, sticky=N + W + S + E)

        self.btn_change = Button(self, text='Save', command=self.save_changes)
        self.btn_change.grid(column=2, row=11, sticky=N + W + S + E)
        for widget in self.winfo_children():
            widget.grid(padx=3, pady=3)
            if isinstance(widget, Button):
                widget["style"] = "AccentButton"

    def return_family_from_string(self, str_fmly):
        # ['parent', 'big brother', 'brother', 'child', 'None']
        if self.shape is not None:
            if str_fmly == self.family[0]:
                return self.shape.parent
            elif str_fmly == self.family[1]:
                return self.shape.upper_neighbour
            elif str_fmly == self.family[2]:
                return self.shape.neighbour
            elif str_fmly == self.family[3]:
                return self.shape.child
            else:
                return None

    def save_changes(self):
        if self.shape is not None:
            shape_text = self.ent_sh_txt.get()
            shape_vorm = self.cbx_vorm_text.get()
            shape_yes = self.cbx_yes.get()
            shape_no = self.cbx_no.get()

            self.shape.tekst = shape_text
            self.shape.vorm = shape_vorm
            if shape_vorm == 'diamont':
                self.shape.YES = self.return_family_from_string(shape_yes)
                self.shape.NO = self.return_family_from_string(shape_no)
            else:
                self.shape.YES = None
                self.shape.NO = None

    def change_family(self):
        if self.shape is not None:
            self.changing_family = True
            pop_up = ChangeFamilyPopUp(self.container, self.shape)
            # self.container.wait_window(pop_up)

    def deactivate_children(self):
        for widget in self.winfo_children():
            if isinstance(widget, Label):
                continue
            if isinstance(widget, Scrollbar):
                continue
            widget.config(state=DISABLED)

    def activate_children(self):
        for widget in self.winfo_children():
            if isinstance(widget, Scrollbar):
                continue
            widget.config(state=NORMAL)

    def return_str_from_family(self, family_member):
        if self.shape is not None and family_member is not None:
            if family_member == self.shape.parent:
                return self.family[0]
            elif family_member == self.shape.upper_neighbour:
                return self.family[1]
            elif family_member == self.shape.neighbour:
                return self.family[2]
            elif family_member == self.shape.child:
                return self.family[3]
            else:
                return self.family[4]
        return self.family[4]

    def fill_values(self, shape):
        self.reset_values()
        app_data = self.get_all_params()
        self.shape = shape  # type: Shape
        x, y, h, w = shape.rectangle
        img = app_data['orig_image']
        cv2_img = Verwerker.crop_cv2_image_absolute(img, y=y, x=x, w=w, h=h)
        pil_img = Verwerker.cv2_to_pil(cv2_img)
        self.update_img(pil_img)
        self.container.visualize_shape(shape)

        parent = shape.parent  # type: Shape
        neigthbour = shape.neighbour  # type: Shape
        upper_neigthbour = shape.upper_neighbour  # type: Shape
        child = shape.child  # type:Shape

        self.shape_text.set(shape.tekst)
        self.cbx_vorm_text.current(self.vormen.index(shape.vorm))

        if parent is not None:
            self.parent_txt.set(parent.tekst)
        if neigthbour is not None:
            self.brother_txt.set(neigthbour.tekst)
        if upper_neigthbour is not None:
            self.big_brother_txt.set(upper_neigthbour.tekst)
        if child is not None:
            self.child_txt.set(child.tekst)

        if not shape.vorm == 'diamont':
            self.cbx_yes['state'] = 'disabled'
            self.cbx_no['state'] = 'disabled'
        else:
            self.cbx_yes['state'] = 'readonly'
            self.cbx_no['state'] = 'readonly'
        yes = self.return_str_from_family(self.shape.YES)
        self.cbx_yes.current(self.family.index(yes))
        no = self.return_str_from_family(self.shape.NO)
        self.cbx_no.current(self.family.index(no))

    def reset_values(self):
        # self.family = ['parent', 'big brother', 'brother', 'child', 'None']
        str_none = self.family[-1]
        self.parent_txt.set(str_none)
        self.big_brother_txt.set(str_none)
        self.brother_txt.set(str_none)
        self.child_txt.set(str_none)
        self.cbx_yes.current(self.family.index(str_none))
        self.cbx_no.current(self.family.index(str_none))
        self.cvs.delete('all')

    def update_img(self, img_pil):
        self.cvs.delete('all')
        img = Verwerker.resize_keep_ratio(self.canvas_width, img_pil)
        img = ImageTk.PhotoImage(img)
        self.container.img = img
        # canvas
        self.cvs.create_image((0, 0), image=img, anchor=NW)

    def get_all_params(self):
        return self.container.get_ini_params()

    def change_to_parent(self):
        if self.shape is not None and self.shape.parent is not None:
            self.save_changes()
            self.fill_values(self.shape.parent)

    def change_to_big_brother(self):
        if self.shape is not None and self.shape.upper_neighbour is not None:
            self.save_changes()
            self.fill_values(self.shape.upper_neighbour)

    def change_to_brother(self):
        if self.shape is not None and self.shape.neighbour is not None:
            self.save_changes()
            self.fill_values(self.shape.neighbour)

    def change_to_child(self):
        if self.shape is not None and self.shape.child is not None:
            self.save_changes()
            self.fill_values(self.shape.child)

    def give_new_family(self, selected_shape, member_name):
        if self.changing_family and member_name is not None:
            index = self.family.index(member_name)
            if index == 0:
                self.shape.parent = selected_shape
            elif index == 1:
                self.shape.upper_neighbour = selected_shape
            elif index == 2:
                self.shape.neighbour = selected_shape
            elif index == 3:
                self.shape.child = selected_shape
            self.fill_values(self.shape)
        self.changing_family = False


class App(Frame):
    columns_titles = 'id;vorm;position;tekst;parent;child;neighbour;upper neigbour;YES;NO\n'

    def __init__(self, container):
        super().__init__(container)
        self.cvs = None
        self.input_frame = None  # type: InputFrame
        self.fc_frame = None  # type: FlowChartFrame
        self.founded_shapes = None  # type: list[Shape]
        self.family_member_holder = None
        self.canvas_width = 500
        self.canvas_heigth = 500
        self.container = container
        self.__create_widgets()
        self.__create_menus()

    def __create_menus(self):
        menubar = Menu(self.container)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="export", command=lambda: self.export_to_csv())
        menubar.add_cascade(label="File", menu=file_menu)
        self.container.config(menu=menubar)

    def __create_widgets(self):
        image_frame = Frame(self, style="Card")
        image_frame.grid(column=1, row=0, rowspan=2, sticky=W + E + N +S)
        image_frame.columnconfigure(0, weight=1)
        Label(image_frame, text='Image', font=("Arial Bold", 15)).grid(column=0, row=0, sticky=W + E, pady=5, padx=5)
        btn_load_img = Button(image_frame, text='Load image', style="AccentButton", command=self.load_image)
        btn_load_img.grid(column=1, row=0, pady=5, padx=5, sticky=W + E)
        btn_load_img.focus_set()

        self.cvs = Canvas(image_frame, width=self.canvas_width, height=self.canvas_heigth, scrollregion=(0,0,2,800))
        self.cvs.grid(column=0, row=1, rowspan=2, pady=5, padx=5, columnspan=2)
        self.cvs.bind('<ButtonRelease-1>', self.canvas_click)
        # add a scrollbar
        vbar = Scrollbar(image_frame, orient=VERTICAL)
        vbar.grid(column=1, row=1,rowspan=2, sticky=E + N + S)
        vbar.config(command=self.cvs.yview)
        self.cvs.config(yscrollcommand=vbar.set)



        self.input_frame = InputFrame(self)
        self.input_frame.grid(column=0, row=0, pady=5, padx=5, sticky= W + E+ N + S)

        self.fc_frame = FlowChartFrame(self)
        self.fc_frame.grid(column=0, row=1,pady=5, padx=5, sticky=N + W + E + S)

        self.ed_shape = EditShape(self)
        self.ed_shape.grid(column=2, row=0, rowspan=2,pady=5, padx=5, sticky=N + W + E + S)

        # self.btn_export = Button(self, text='export', state=DISABLED, command=self.export_to_csv,)
        # self.btn_export.grid(column=2, row=8, pady=5, padx=5, sticky=W)

        for widget in self.winfo_children():
            widget.grid(padx=5, pady=5)


    def update_image(self, img):
        self.cvs.delete('all')
        img = Verwerker.resize_keep_ratio(self.canvas_width, img)
        img = ImageTk.PhotoImage(img)
        self.container.img = img
        # canvas
        self.cvs.create_image((0, 0), image=img, anchor=NW)

    def load_image(self):
        filename = filedialog.askopenfilename(title='choose an image', filetypes=[('image files', ('.png', '.jpg'))])
        if filename:
            self.input_frame.img_path = filename
            self.input_frame.is_image_load = True
            self.manage_program_states()
            img = Image.open(filename)
            self.update_image(img)

    def get_ini_params(self):
        return self.input_frame.get_params()

    def canvas_click(self, event):
        p = (event.x, event.y)  # needs transformation
        p = self.transform_point(p)
        selected_shape = None
        if self.founded_shapes is not None and p is not None:
            for shape in self.founded_shapes:
                if shape.is_point_inside(p):
                    selected_shape = shape
                    break

        if selected_shape is not None and not self.ed_shape.changing_family:
            self.visualize_shape(selected_shape)
            self.ed_shape.save_changes()
            self.ed_shape.fill_values(selected_shape)

        elif self.ed_shape.shape is not None and self.ed_shape.changing_family:
            self.ed_shape.give_new_family(selected_shape, self.family_member_holder)

    def change_family_member(self, family):
        self.family_member_holder = family
        # current selected shape
        shape = self.ed_shape.shape
        # toon mogelijke keuzes
        possible_choises = self.fc_frame.charter.get_possible_shapes(shape)
        self.visualize_possible_choices(shape, possible_choises)

    def transform_point(self, p):
        x, y = p
        # PIL image
        # image = self.input_frame.pil_image
        image = self.get_ini_params()['pil_image']
        if image is not None:
            width, height = image.size
            factor = float(width / self.canvas_width)
            y = int(y * factor)
            x = int(x * factor)
            return x, y

    def export_to_csv(self):
        if self.founded_shapes is not None:
            files = [('CSV Document', '*.csv')]
            name = filedialog.asksaveasfile(mode='w', filetypes=files, defaultextension=files)
            if name is not None:
                line = ''
                line += self.columns_titles
                # f.write(columns_titles)
                for shape in reversed(self.founded_shapes):
                    line += '{};{};{}'.format(shape.id, shape.write_shape(), shape.write_family_ids(';'))
                    if shape.vorm == "diamont":
                        if shape.YES is not None:
                            line += ';{}'.format(shape.YES.id)
                        if shape.NO is not None:
                            line += ';{}'.format(shape.NO.id)
                    line += '\n'
                name.write(line)
                name.close()
                messagebox.showinfo('', 'successfully export')

    def visualize_shape(self, shape):
        img = self.fc_frame.show_invalid_shapes(self.fc_frame.img)
        if img is not None and shape is not None:
            data = self.get_ini_params()
            y = data['star_y']
            h = data['height']
            charter = fc()
            image = charter.draw_current_shape(img, shape)

            image = Verwerker.cv2_to_pil(image)
            self.update_image(image)

    def visualize_possible_choices(self, shape, choices):
        img = self.fc_frame.img
        charter = fc()
        if img is not None and shape is not None:
            image = charter.draw_current_shape(img, shape)
            color = (95, 246, 19)
            if choices is not None:
                image = charter.draw_shapes(image, choices, color)
            image = Verwerker.cv2_to_pil(image)
            self.update_image(image)

    def manage_program_states(self):
        if self.input_frame.is_image_load:
            self.input_frame.activate_crop_section()
        if self.input_frame.is_image_cropped:
            self.input_frame.activate_mask_section()
        if self.input_frame.is_binv_ready:
            self.input_frame.activate_otsu_section()
        if self.input_frame.is_otsu_ready:
            self.input_frame.activate_detect_section()
        if self.input_frame.is_shape_detection_ready:
            self.fc_frame.activate_children()
        if self.fc_frame.is_flow_chart_ready:
            self.ed_shape.activate_children()
            # self.btn_export['state'] = NORMAL


def main():
    root = Tk()
    p1 = PhotoImage(file='flow-chart-symbol.png')
    root.iconphoto(False, p1)
    root.title('Flow to CSV')
    root.geometry('1260x650')
    root.call('source', 'themes\\azure-dark.tcl')
    Style().theme_use('azure-dark')
    app = App(root)
    # app.grid(column=0, row=0, padx=20, pady=20)
    app.pack(expand=True, side=TOP)
    root.mainloop()


if __name__ == '__main__':
    main()
