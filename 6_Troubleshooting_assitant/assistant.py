from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tkinter.ttk import Treeview, Combobox, Style
from source.db_helper import DataBase as db
from source.record import RecordClass
import threading
from ttkthemes import ThemedStyle


class KillableThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(KillableThread, self).__init__(*args, **kwargs)
        self._stop = threading.Event()

    # function using _stop function
    def stop(self):
        self._stop.set()


class Helper:
    @staticmethod
    def get_type_machines(machine_type_id, afdeling):
        """
        :param machine_type_id:
        :param afdeling: qualification id
        :return: list[] items: (type_id, description, qualification_id)
        """
        table_machine_type = db('MachineType')
        # kleine sql maken voor type machines
        columns = table_machine_type.tb_data.get('columns')
        # result machine_id 0, description 1, afdeling 2
        type_id = columns["0"]
        description = columns["1"]
        qualif_id = columns["2"]
        clm = [type_id, description, qualif_id]

        options = []
        if not machine_type_id == '':
            option = '{} like \'%{}%\''.format(type_id, machine_type_id)
            options.append(option)
        if not afdeling == '':
            option = '{} like \'%{}%\''.format(qualif_id, afdeling)
            options.append(option)

        table_machine_type.make_get_query(clm)
        table_machine_type.append_options(options)
        table_machine_type.connect_to_database()
        return table_machine_type.execute_query()

    @staticmethod
    def get_machines(types):
        """
        :param types: Type toestelen (mch_type, desc, qualification)
        :return: (0: sn, 1: machinetype, 2: machineID, 3:[CurrentUserID]")
        """
        table_machines = db('Machine')
        columns = table_machines.tb_data.get('columns')
        # return list[(serienummer, machine_type, machineID )]
        # zoek opdracht by machineID - col 9
        # serienummer 1, machine_type 4, machineid = 8
        clm = [columns["0"], columns["4"], columns["8"], columns["2"]]
        table_machines.make_get_query(clm)
        options = []
        for type in types:
            mch_type = type[0]
            option = '{} = \'{}\''.format(columns["4"], mch_type)
            options.append(option)

        table_machines.append_options(options, ' OR ')
        table_machines.connect_to_database()
        resp = table_machines.execute_query()

        # list of machines that are the same type
        return resp

    @staticmethod
    def get_machine_interventions(machines, kernwoorden=None, separator='AND'):
        """
        :param machines: type_machines by id
        :param kernwoorden: keywords to be search in interventions
        :param separator: binder for keywords AND or OR
        :return: list of items: (0:tableinterventionID, 1:remarks, 2:exec_code, 3:MachineID, 4:SerialNumber, 5:InterventionID)
        """
        # get all interventions where de serie_nummer van mashines gelijk is
        # zoekopdracht via (machineid 3)
        # intervertionmachineid 0, Remark 7, ExecutionCode 10,  MachineId 3, serienummer 4, Interventionid 1

        table_inter_machines = db('InterventionMachine')
        columns = table_inter_machines.tb_data.get('columns')
        inter_mach_id, remarks, exec_code, sr_nr = columns["0"], columns["7"], columns["10"], columns["3"]
        serial_nmbr, inter_id = columns["4"], columns["1"]
        clm = [inter_mach_id, remarks, exec_code, sr_nr, serial_nmbr, inter_id]
        table_inter_machines.make_get_query(clm, 100)
        table_inter_machines.connect_to_database()
        resp = []
        for machine in machines:
            mc_id = machine[2]
            options = []
            option1 = '{} = \'{}\''.format(columns["3"], mc_id)

            for woord in kernwoorden:
                option = "{} LIKE '%{}%'".format(remarks, woord)
                options.append(option)

            if separator == 'OR':
                begin = option1 + ' AND '
                options = [begin + x for x in options]
            else:
                options = [option1, *options]

            antword = table_inter_machines.execute_query(options=options, separator=' {} '.format(separator))
            # antwoord geef en list van alle toestellen die dat id heeft
            if not isinstance(antword, list):
                antword = [antword]
            if antword is not None and len(antword) > 0:
                resp.extend(antword)
        return resp

    @staticmethod
    def get_used_art(mach_interventions):
        if mach_interventions is not None and len(mach_interventions) > 0:
            table_inter_article = db('InterventionArticle')
            # zoek opdracht interventionmachineid 2 and machineid  4
            # artNr 5, machineid 4 , magNR 6, intervention machine id 2
            columns = table_inter_article.tb_data.get('columns')
            clm = [columns["5"], columns["4"], columns["6"], columns["2"]]
            table_inter_article.make_get_query(clm)
            table_inter_article.connect_to_database()
            options = []
            # resp = []
            for interventie in mach_interventions:
                # intervertionmachineid 0, Remark 7, ExecutionCode 10,  MachineId 4
                inter_mc_id, machine_id = interventie[0], interventie[3]
                option = "{} = '{}'".format(columns["4"], machine_id)
                option += " AND {} = '{}'".format(columns["2"], inter_mc_id)
                options.append(option)

            table_inter_article.append_options(options, ' OR ')
            resp = table_inter_article.execute_query()
            return resp

    @staticmethod
    def get_article_details(art_nr):
        table_article = db("Article")
        columns = table_article.tb_data.get('columns')
        table_article.connect_to_database()
        nr = columns["0"]
        descrip = columns["1"]
        stock = columns["12"]
        cls = [nr, descrip, stock]
        table_article.make_get_query(cls)
        option = "{} = '{}'".format(nr, art_nr)

        resp = table_article.execute_single_query(option)

        return resp

    @staticmethod
    def get_firstlayer_intervention(match_interventions):
        """
        :param match_interventions: list of matching interventions from machine intervention
        :return: list of items: (0: "[ID]", 1:[DateExec],2:[ClientID],3:[Servicebon], 4:[Remarks])
        """
        table_intervention = db("Intervention")
        columns = table_intervention.tb_data.get('columns')
        # zoektoch by intervention ID mach intervention[5]
        # antword = "0":"[ID]",
        #           "5":"[DateExec]",
        #           "6":"[ClientID]",
        #            "8":"[Servicebon]"

        inter_id, exec_date, client_id, servc = columns["0"], columns["5"], columns["6"], columns["8"]
        remarks = columns["9"]
        cls = [inter_id, exec_date, client_id, servc, remarks]
        table_intervention.make_get_query(cls)

        options = []

        for mach_interventie in match_interventions:
            # id_mach_inter = mach_interventie[5]
            option = "{} = {} ".format(inter_id, mach_interventie[5])
            options.append(option)
        table_intervention.connect_to_database()
        res = table_intervention.execute_query(options, separator=" OR ")
        return res

    @staticmethod
    def get_planned_items(kernworden):
        table_intervention = db("IntervPlan")
        columns = table_intervention.tb_data.get('columns')
        # zoek opdracht via like remark en/ of qualification
        remark = columns["7"]
        qual_id = columns["3"]
        wo, plan_code, client_id, servc_bon = columns["0"], columns["1"], columns["2"], columns["6"]
        cls = [wo, qual_id, plan_code, client_id, servc_bon, remark]
        iscompleted = columns["8"]
        table_intervention.make_get_query(cls, 100)
        options = []
        # remarks
        if kernworden[0] is not None and not kernworden[0] == '':
            option = "{} like '%{}%'".format(remark, kernworden[0])
            options.append(option)
        # qualification id
        if kernworden[1] is not None and not kernworden[1] == '':
            option = "{} like '%{}%'".format(qual_id, kernworden[1])
            options.append(option)
        # plancode
        if kernworden[2] is not None and not kernworden[2] == '':
            option = "{} like '%{}%'".format(plan_code, kernworden[2])
            options.append(option)

        if len(options) > 0:
            option = "{} = 1".format(iscompleted)
            options.append(option)
        table_intervention.connect_to_database()
        resp = table_intervention.execute_query(options)
        # zoek opdracht via remarks 9
        # qualifications
        return resp

    @staticmethod
    def get_mach_intervention_by_planItems(machines, servicebons):
        """
        :param machines:
        :param servicebons:
        :return: inter_mach_id, remarks, exec_code, sr_nr, serial_nmbr, inter_id, werkorder
        """
        # eerste opzoeken in
        table_interventions = db('Intervention')
        columns = table_interventions.tb_data.get("columns")
        intervid, clientid, serv_bon = columns["0"], columns["6"], columns["8"]
        cls = [intervid, clientid, serv_bon]
        table_interventions.make_get_query(cls)
        table_interventions.connect_to_database()
        options = []
        for servicebon in servicebons:
            option = "{} = '{}'".format(serv_bon, servicebon)
            options.append(option)

        completed_interventions = table_interventions.execute_query(options, separator=' OR ')
        # get all interventions where de serie_nummer van mashines gelijk is
        # zoekopdracht via (machineid 3)
        # intervertionmachineid 0, Remark 7, ExecutionCode 10,  MachineId 3, serienummer 4, Interventionid 1
        table_inter_machines = db('InterventionMachine')
        columns = table_inter_machines.tb_data.get('columns')
        inter_mach_id, remarks, exec_code, sr_nr = columns["0"], columns["7"], columns["10"], columns["3"]
        serial_nmbr, inter_id, werkorder = columns["4"], columns["1"], columns["2"]
        clm = [inter_mach_id, remarks, exec_code, sr_nr, serial_nmbr, inter_id, werkorder]
        table_inter_machines.make_get_query(clm)
        table_inter_machines.connect_to_database()
        options = []
        for intervention in completed_interventions:
            option = "{} = '{}'".format(inter_id, intervention[0])
            options.append(option)

        mach_interventions = table_inter_machines.execute_query(options, separator=" OR ")

        sns_machines = [m[0] for m in machines]
        sns_machines = list(set(sns_machines))
        # filter ahcter af by serie nummer machine
        resp = [x for x in mach_interventions if x[4] in sns_machines]

        return resp

    @staticmethod
    def get_voorad_magazijn(magazijn_nummer):
        table_voorad_magazijn = db('voorraad_art_mag')
        columns = table_voorad_magazijn.tb_data['columns']
        # 0 article, 1 magazijncode, 2 stock, 3 datum_laatste_wijz
        article, mag_code, stock, date_last = columns["0"], columns["1"], columns["2"], columns["3"]
        cls = [article, stock, date_last]
        table_voorad_magazijn.make_get_query(cls)

        option = "{} = '{}'".format(mag_code, magazijn_nummer)

        table_voorad_magazijn.connect_to_database()
        resp = table_voorad_magazijn.execute_query([option])
        resp = [(x[0], int(x[1]), x[2]) for x in resp]
        return resp

    @staticmethod
    def get_article_owners(article_num):
        table_voorad_magazijn = db('voorraad_art_mag')
        columns = table_voorad_magazijn.tb_data['columns']
        article, mag_code, stock, date_last = columns["0"], columns["1"], columns["2"], columns["3"]
        cls = [article, mag_code, stock, date_last]
        table_voorad_magazijn.make_get_query(cls)

        options = []
        option = "{} = '{}'".format(article, article_num)
        options.append(option)
        option = "{} >= 1".format(stock)
        options.append(option)
        table_voorad_magazijn.connect_to_database()
        res = table_voorad_magazijn.execute_query(options, " AND ")

        return res


class Details(Frame):
    def __init__(self, container):
        super().__init__(container)
        self.container = container  # type: App
        self.font_bold = ("Courier New", 10, "bold")
        self.font = ("Courier New", 10)
        self.__create_widgets()
        personalise(self)

    def __create_widgets(self):
        Label(self, text="Details", font=("Arial Black", 15)).grid(column=0, row=0, sticky=W)

        # row 1
        r = 1
        Label(self, text="Servicebon").grid(column=0, row=r, sticky=W)
        self.srvbon = StringVar()
        ent_servbon = Entry(self, textvariable=self.srvbon, state="readonly")
        ent_servbon.grid(column=1, row=r, sticky=W + E)

        # row 2
        r += 1
        Label(self, text="SN").grid(column=0, row=r, sticky=W)
        self.sn_tvar = StringVar()
        # self.sn_tvar.set("WIL-52559865PWD")
        ent_serienummer = Entry(self, textvariable=self.sn_tvar, state="readonly")
        ent_serienummer.grid(column=1, row=r, sticky=E + W)

        # row 3
        r += 1
        Label(self, text="Execution code").grid(column=0, row=r, sticky=W)
        self.ex_code_var = StringVar()
        Entry(self, textvariable=self.ex_code_var, state='readonly').grid(column=1, row=r, sticky=W + E)
        # row 4
        r += 1
        Label(self, text="General remarks").grid(column=0, row=r, sticky=W)

        # row 5
        r += 1
        self.txt_gen_remarks = Text(self, width=50, height=3)
        self.txt_gen_remarks.grid(column=0, row=r, columnspan=2, sticky=W + E)
        self.grid(padx=20, pady=20)

        # row 6
        r += 1
        Label(self, text="Intervention remarks").grid(column=0, row=r, sticky=W)

        # row 7
        r += 1
        self.txt_rem_details = Text(self, width=50, height=12, font=self.font)

        self.txt_rem_details.grid(column=0, row=r, columnspan=2, sticky=W + E)
        self.grid(padx=20, pady=20)

        # row 8
        r += 1
        Label(self, text="Articles").grid(column=0, row=r, sticky=W)
        # row 9
        r += 1
        self.lst_intervention_articles = Listbox(self)
        self.lst_intervention_articles.grid(column=0, row=r, columnspan=2, sticky=W + E)

        for widget in self.winfo_children():
            widget.grid(padx=5, pady=5)

    def set_intervention_text(self, text):
        self.txt_rem_details.delete(1.0, "end")
        self.txt_rem_details.insert(1.0, text)

    def set_general_text(self, text):
        self.txt_gen_remarks.delete(1.0, "end")
        self.txt_gen_remarks.insert(1.0, text)

    def fill_details(self, intervention, articles, keywords, data_intervention):
        # intervertionmachineid 1, Remark 7, ExecutionCode 10,  MachineId 3
        # serial_nmbr 4
        # print(data_intervention)
        rem, ex_code = intervention[1], intervention[2]
        serial_number = intervention[4]
        gen_rem = data_intervention[4]
        if gen_rem is None:
            gen_rem = ""
        self.set_general_text(gen_rem)
        self.set_intervention_text(rem)
        self.ex_code_var.set(ex_code)
        self.sn_tvar.set(serial_number)
        self.bold_keywords_text(keywords)
        # dataintervention("0":"[ID]","5":"[DateExec]","6":"[ClientID]", "8":"[Servicebon]")
        self.srvbon.set(data_intervention[3])
        overview = []
        for article in articles:
            line = " MAG {} - ".format(article[2])
            line += "{} : {}".format(article[0], self.container.get_article_description(article))

            overview.append(line)

        self.lst_intervention_articles.config(listvariable=Variable(value=overview))

    def bold_keywords_text(self, keywords):
        # self.txt_rem_details.tag_config("red_tag", foreground="red", underline=1)
        # word length use as offset to get end position for tag
        # search word from first char (1.0) to the end of text (END)
        # bold_font = self.txt_rem_details["font"]+" -weight bold"
        # print(bold_font)
        self.txt_rem_details.tag_configure("BOLD", foreground="red", font=self.font_bold)
        for word in keywords:
            offset = '+%dc' % len(word)  # +5c (5 chars)
            pos_start = self.txt_rem_details.search(word, '1.0', END, nocase=1)

            # check if found the word
            while pos_start:
                # create end position by adding (as string "+5c") number of chars in searched word
                pos_end = pos_start + offset
                # add tag
                self.txt_rem_details.tag_add('BOLD', pos_start, pos_end)
                # search again from pos_end to the end of text (END)
                pos_start = self.txt_rem_details.search(word, pos_end, END, nocase=1)


class CompareMagzijn:
    def __init__(self, parent):
        self.main = parent  # type: App
        top = self.top = Toplevel(parent)
        top.protocol("WM_DELETE_WINDOW", self.destroy_window)
        top.wm_title('Compare magazijn')
        self.exit_flag = False
        self.articles_set = None
        self.pos_articles = None

        self.__thread_zoek_magazijn = KillableThread(target=self.zoek)
        self.__create_widgets()
        personalise(self.top)
        # self.top.mainloop()

    def __create_widgets(self):
        # row = 0
        self.top.columnconfigure(0, weight=0)
        self.top.columnconfigure(1, weight=0)
        self.top.columnconfigure(2, weight=1)
        self.top.columnconfigure(3, weight=1)
        r = 0
        Label(self.top, text="Stock number").grid(column=0, row=r, sticky=W)
        self.magazijn_var = StringVar()
        Entry(self.top, textvariable=self.magazijn_var).grid(column=1, row=r, sticky=W + E)
        Button(self.top, text="Search", style="AccentButton", command=self.run_zoek).grid(column=2, row=r, sticky=W)
        # row = 1
        r += 1
        self.lbl_current_art = Label(self.top)
        self.lbl_current_art.grid(column=0, row=r, columnspan=3, sticky=W + E)
        # row = 2
        r += 1
        Label(self.top, text="Possible  articles").grid(column=0, row=r, sticky=W)
        Label(self.top, text="Owned by:").grid(column=4, row=r, sticky=W)
        # row = 3
        r += 1

        self.te_zoeken_articles_var = Variable()
        self.current_articles = Listbox(self.top, width=100, listvariable=self.te_zoeken_articles_var)
        self.current_articles.grid(column=0, row=r, columnspan=4, sticky=W + E + N + S)
        self.current_articles.bind('<Double-1>', self.show_owners_by_lbx)

        self.magazijn_in_bezit_var = Variable()
        self.lbx_mag_in_bezit = Listbox(self.top, listvariable=self.magazijn_in_bezit_var)
        self.lbx_mag_in_bezit.grid(column=4, row=r, sticky=W)

        # row = 4
        r += 1
        Label(self.top, text="Current set").grid(column=0, row=r, sticky=W)
        # row = 5
        self.tree_set = Treeview(self.top)

        self.tree_set["columns"] = ["#0", "#1", "#2", "#3"]
        self.tree_set.column("#0", width=140, minwidth=20, stretch=NO)
        self.tree_set.column("#1", width=90, minwidth=20, stretch=NO)
        self.tree_set.column("#2", width=300, minwidth=20, stretch=NO)
        self.tree_set.column("#3", width=350, minwidth=20, stretch=YES)
        self.tree_set.heading("#0", text="Article", anchor=W)
        self.tree_set.heading("#1", text="Stock", anchor=W)
        self.tree_set.heading("#2", text="Last changed", anchor=W)
        self.tree_set.heading("#3", text="Description", anchor=W)

        self.tree_set.grid(column=0, row=r, columnspan=6, sticky=W)
        self.tree_set.bind('<Double-1>', self.show_owners_by_tree)

        for widget in self.top.winfo_children():
            widget.grid(padx=5, pady=5)

    def destroy_window(self):
        # fill main?
        # choice = self.cbx_fml_choise.get()
        # self.main.change_family_member(choice)
        self.exit_flag = True
        self.top.destroy()

    def fill_current_articles(self, articles):
        overview = []
        for article in articles:
            line = ""
            # line = " MAG {} - ".format(article[2])
            line += "{} - {}".format(article[0], self.main.get_article_description(article))

            overview.append(line)
        self.te_zoeken_articles_var.set(overview)
        self.pos_articles = [x[0] for x in articles]

    def zoek(self):
        try:
            magazijn_code = self.magazijn_var.get()
            magazijn_code = int(magazijn_code)
            self.articles_set = Helper.get_voorad_magazijn(magazijn_code)
            self.articles_set.sort(key=lambda x: x[1])
            self.fill_tree_articles_set()
        except ValueError:
            messagebox.showinfo("Information", "Magazijn code zijn enkel nummers!")
        finally:
            self.__thread_zoek_magazijn = KillableThread(target=self.zoek)

    def run_zoek(self):
        if not self.__thread_zoek_magazijn.is_alive():
            self.__thread_zoek_magazijn.run()
        else:
            messagebox.showinfo("Information", "Een andere process is bezig...")

    def fill_tree_articles_set(self):
        self.tree_set.delete(*self.tree_set.get_children())
        if self.articles_set is not None and len(self.articles_set) > 0:
            if self.pos_articles is not None and len(self.pos_articles) > 0:
                for article in self.articles_set:
                    if article[0] in self.pos_articles:
                        article = list(article)
                        article.append(self.main.get_article_description(article))

                        self.tree_set.insert("", 'end', text=str(article[0]), values=article[1:])

    def loop(self):
        self.top.mainloop()

    def fill_founded_owners(self, article_nummer):
        res = Helper.get_article_owners(article_nummer)
        # article, mag_code, stock, date_last
        res = ["{} - {}".format(x[1], int(x[2])) for x in res]
        self.magazijn_in_bezit_var.set(res)
        desc = self.main.get_article_description([article_nummer])

        artic_desc = "{} {}".format(article_nummer, desc)
        self.lbl_current_art.config(text=artic_desc)

    def show_owners_by_tree(self, event):
        # def select_article(self, event):
        if self.tree_set.get_children() is not None and len(self.tree_set.get_children()) > 0:
            curItem = self.tree_set.selection()[0]
            item = self.tree_set.item(curItem)
            article_nummer = item["text"]
            self.fill_founded_owners(article_nummer)

    def show_owners_by_lbx(self, event):
        if self.te_zoeken_articles_var.get() is not None and len(self.te_zoeken_articles_var.get()) > 0:
            cs = self.current_articles.curselection()  # type: tuple
            if len(cs) > 0:
                article_nummer = self.current_articles.get([cs[0]]).split(" -")[0]
                # print(article_nummer)
                self.fill_founded_owners(article_nummer)


class FilterWindow:
    def __init__(self, parent, action):
        self.parent = parent  # type: ZoekMachineInterventions
        top = self.top = Toplevel(parent)
        top.protocol("WM_DELETE_WINDOW", self.destroy_window)
        top.wm_title('Filters')
        self.action = action
        self.e_codes = [100, 1050, 875, 7050, 750, "all"]
        self.__create_widgets()
        personalise(self.top)

    def __create_widgets(self):
        if self.action == "interventions":
            # row 0
            r = 0
            Label(self.top, text="Search in remarks").grid(column=0, row=r, sticky=W)
            self.remarks_var = StringVar()
            entry_remarks = Entry(self.top, textvariable=self.remarks_var)
            entry_remarks.grid(column=1, row=r, sticky=W + E)
            # row 1
            r += 1
            Label(self.top, text="Execution Code").grid(column=0, row=r, sticky=W)
            # self.excution_var = StringVar()
            self.cbx_exec_code = Combobox(self.top, values=self.e_codes, state='readonly')
            self.cbx_exec_code.grid(column=1, row=r, sticky=W + E)
            self.cbx_exec_code.current(len(self.e_codes) - 1)
            # Entry(self.top, textvariable=self.excution_var).grid(column=1, row=r, sticky=W + E)

            # row 2
            r += 1
            Label(self.top, text="Client Number").grid(column=0, row=r, sticky=W)
            self.client_var = StringVar()
            entry_clientnr = Entry(self.top, textvariable=self.client_var)
            entry_clientnr.grid(column=1, row=r, sticky=W + E)

            # row 3
            r += 1
            Label(self.top, text="Serial Number").grid(column=0, row=r, sticky=W)
            self.sn_machine_var = StringVar()
            entry_sn = Entry(self.top, textvariable=self.sn_machine_var)
            entry_sn.grid(column=1, row=r, sticky=W + E)

            entry_remarks.bind("<Return>", lambda e: self.give_values())
            entry_sn.bind("<Return>", lambda e: self.give_values())
            entry_clientnr.bind("<Return>", lambda e: self.give_values())
            # row 4
            r += 1
            Button(self.top, text="Apply filters", style="AccentButton", command=self.give_values).grid(column=1, row=r, sticky=E)

        elif self.action == "articles":
            # row 0
            r = 0
            Label(self.top, text="Article number").grid(column=0, row=r, sticky=W)
            self.article_num_var = StringVar()
            entry_artnum = Entry(self.top, textvariable=self.article_num_var)
            entry_artnum.grid(column=1, row=r, sticky=W + E)

            # row 1
            r += 1
            Label(self.top, text="Article description").grid(column=0, row=r, sticky=W)
            self.article_des_var = StringVar()
            entry_desc = Entry(self.top, textvariable=self.article_des_var)
            entry_desc.grid(column=1, row=r, sticky=W + E)

            entry_desc.bind("<Return>", lambda e: self.filter_articles())
            entry_artnum.bind("<Return>", lambda e: self.filter_articles())
            r += 1
            Button(self.top, text="Apply filters", style="AccentButton", command=self.filter_articles).grid(column=1, row=r, sticky=E)

        for widget in self.top.winfo_children():
            widget.grid(padx=5, pady=5)

    def give_values(self):
        values = [str(self.remarks_var.get()), str(self.cbx_exec_code.get()), str(self.client_var.get()),
                  str(self.sn_machine_var.get())]
        keys = ["remarks", "ex_code", "client", "sn_machine"]

        res = dict(zip(keys, values))

        # for k,v in res.items():
        #     print(k, v)
        self.parent.filter_callback(**res)
        self.destroy_window()

    def loop(self):
        self.top.mainloop()

    def destroy_window(self):
        # fill main?
        # choice = self.cbx_fml_choise.get()
        # self.main.change_family_member(choice)
        self.exit_flag = True
        self.top.destroy()

    def filter_articles(self):
        number = self.article_num_var.get()
        description = self.article_des_var.get()
        if not number == "":
            # use nummer
            self.parent.filter_articles_callback(("number", number))
            self.destroy_window()
        elif not description == "":
            self.parent.filter_articles_callback(("description", description))
            self.destroy_window()
        #     use description
        # anders doe niets


class ZoekPlannedItems:
    def __init__(self, parent):
        self.main = parent  # type: App
        top = self.top = Toplevel(parent)
        top.protocol("WM_DELETE_WINDOW", self.destroy_window)
        top.wm_title('Find in plan items')
        self.planned_interventions = None
        self.font_bold = ("Courier New", 10, "bold")
        self.font = ("Courier New", 10)
        self.exit_flag = False
        self.__thread_zoek_plannend_interventions = KillableThread(target=self.zoek)
        self.__create_widgets()
        # self.top.mainloop()
        personalise(self)

    def __create_widgets(self):
        # row = 1
        r = 0
        Label(self.top, text="Find remarks").grid(column=0, row=r, sticky=W)
        self.kern_woord_var = StringVar()
        ent_kern_woord = Entry(self.top, textvariable=self.kern_woord_var)
        ent_kern_woord.grid(column=1, row=r, sticky=W + E)
        Label(self.top, text="Qualification").grid(column=2, row=r, sticky=W)
        self.qualif_var = StringVar()
        ent_qualification_id = Entry(self.top, textvariable=self.qualif_var)
        ent_qualification_id.grid(column=3, row=r, sticky=W + E)

        Label(self.top, text="Plan code").grid(column=4, row=r, sticky=W)

        self.plan_code_var = StringVar()
        ent_plan_code = Entry(self.top, textvariable=self.plan_code_var)
        ent_plan_code.grid(column=5, row=r, sticky=W + E)
        self.btn_zoek = Button(self.top, text="Search", command=self.run_zoek)
        self.btn_zoek.grid(column=6, row=r, sticky=W + E)
        # row = 2
        r += 1
        self.tree_founded_items = Treeview(self.top)

        self.tree_founded_items["columns"] = ["#0", "#1", "#2", "#3", "#4"]
        self.tree_founded_items.column("#0", width=90, minwidth=20, stretch=NO)
        self.tree_founded_items.column("#1", width=90, minwidth=20, stretch=NO)
        self.tree_founded_items.column("#2", width=90, minwidth=20, stretch=NO)
        self.tree_founded_items.column("#3", width=90, minwidth=20, stretch=NO)
        self.tree_founded_items.column("#4", width=90, minwidth=20, stretch=NO)
        self.tree_founded_items.column("#5", width=300, minwidth=20, stretch=NO)

        self.tree_founded_items.heading("#0", text="WO", anchor=W)
        self.tree_founded_items.heading("#1", text="Qualification", anchor=W)
        self.tree_founded_items.heading("#2", text="Plan Code", anchor=W)
        self.tree_founded_items.heading("#3", text="CustomerID", anchor=W)
        self.tree_founded_items.heading("#4", text="Servicebon", anchor=W)
        self.tree_founded_items.heading("#5", text="Remarks", anchor=W)

        self.tree_founded_items.grid(column=0, row=r, columnspan=7)
        self.tree_founded_items.bind('<Double-1>', self.view_intervention)

        # row = 3
        r += 1
        self.scr_tree_found_items = Scrollbar(self.top, orient="horizontal", command=self.tree_founded_items.xview)
        self.scr_tree_found_items.grid(column=0, row=r, columnspan=7, sticky=W + E)
        self.tree_founded_items.configure(xscrollcommand=self.scr_tree_found_items.set)

        # row = 4
        r += 1
        Label(self.top, text="Remark").grid(column=0, row=r, sticky=W)
        # row = 5
        r += 1
        self.txt_remarks = Text(self.top, height=15, font=self.font)
        self.txt_remarks.grid(column=0, row=r, columnspan=7, sticky=W + E)

        self.scr_txt_rem = Scrollbar(self.top, orient="vertical", command=self.txt_remarks.yview)
        self.scr_txt_rem.grid(column=7, row=r, sticky=N + S)
        self.txt_remarks.configure(yscrollcommand=self.scr_txt_rem.set)

        # row = 6
        r += 1
        self.btn_fill = Button(self.top, text="Fill Main", command=self.fill_main)
        self.btn_fill.grid(column=6, row=r, columnspan=2, sticky=W + E)

        for widget in self.top.winfo_children():
            widget.grid(padx=5, pady=5)

    def destroy_window(self):
        # fill main?
        # choice = self.cbx_fml_choise.get()
        # self.main.change_family_member(choice)
        self.exit_flag = True
        self.top.destroy()

    def zoek(self):
        woord = self.kern_woord_var.get()
        qualification = self.qualif_var.get()
        plan_code = self.plan_code_var.get()
        zoek_opdrachten = [woord, qualification, plan_code]
        if zoek_opdrachten is not None and len(zoek_opdrachten) > 0:
            self.planned_interventions = Helper.get_planned_items(zoek_opdrachten)
            self.fill_founded_items_tree()
        self.__thread_zoek_plannend_interventions = KillableThread(target=self.zoek)

    def fill_founded_items_tree(self):
        self.tree_founded_items.delete(*self.tree_founded_items.get_children())
        if self.planned_interventions is not None and len(self.planned_interventions) > 0:
            for planned_interv in self.planned_interventions:
                self.tree_founded_items.insert("", 'end', text=str(planned_interv[0]), values=planned_interv[1:])

    def set_text(self, text):
        self.txt_remarks.delete(1.0, "end")
        self.txt_remarks.insert(1.0, text)

    def bold_keywords_text(self, keywords):
        # self.txt_rem_details.tag_config("red_tag", foreground="red", underline=1)
        # word length use as offset to get end position for tag
        # search word from first char (1.0) to the end of text (END)
        # bold_font = self.txt_rem_details["font"]+" -weight bold"
        # print(bold_font)
        self.txt_remarks.tag_configure("BOLD", foreground="red", font=self.font_bold)
        for word in keywords:
            offset = '+%dc' % len(word)  # +5c (5 chars)
            pos_start = self.txt_remarks.search(word, '1.0', END, nocase=1)

            # check if found the word
            while pos_start:
                # create end position by adding (as string "+5c") number of chars in searched word
                pos_end = pos_start + offset
                # add tag
                self.txt_remarks.tag_add('BOLD', pos_start, pos_end)
                # search again from pos_end to the end of text (END)
                pos_start = self.txt_remarks.search(word, pos_end, END, nocase=1)

    def view_intervention(self, event):
        if self.tree_founded_items.get_children() is not None and len(self.tree_founded_items.get_children()) > 0:
            curItem = self.tree_founded_items.selection()[0]
            item = self.tree_founded_items.item(curItem)
            remark = item['values'][4]
            if remark is not None and len(remark) > 0:
                self.set_text(remark)
                self.bold_keywords_text([self.kern_woord_var.get()])

    def fill_main(self):
        if self.planned_interventions is not None and len(self.planned_interventions) > 0:
            servicebons = []
            for intervention in self.planned_interventions:
                servicebon = intervention[4]
                if servicebon is not None and not servicebon == "None":
                    servicebons.append(servicebon)
            keyword = self.kern_woord_var.get()
            self.main.search_from_pln_items(servicebons, keyword=keyword)
            self.main.record_actions.add_keywords([self.kern_woord_var.get()], " AND ")

    def run_zoek(self):
        if not self.__thread_zoek_plannend_interventions.is_alive():
            self.__thread_zoek_plannend_interventions.start()
        else:
            messagebox.showinfo("Information", "Een andere process is bezig...")

    def kill_process(self):
        if self.__thread_zoek_plannend_interventions.is_alive():
            self.__thread_zoek_plannend_interventions.stop()
            self.__thread_zoek_plannend_interventions = KillableThread(target=self.zoek)

    def run_main_loop(self):
        self.top.mainloop()


class ZoekMachineInterventions(Frame):
    FILTER_BY_ARTICLES = "filter by articles"
    FILTER_BY_DESCRIPTION = "filter by description"

    def __init__(self, container):
        super().__init__(container)
        self.container = container  # type: App
        self.e_codes = [100, 1050, 875, 7050, 750, "all"]
        self.keys_options = ["AND", "OR"]
        self.kernwoorden = []
        self.matching_intervention = []
        self.used_articles = []
        self.gevonden_articles = []
        self.machines = None
        self.machine_interventions = None
        self.interventions = None
        self._thread_zoek_intervention = KillableThread(target=self.search)
        self.__create_widgets()
        personalise(self)

    def __create_widgets(self):
        Label(self, text="Search interventions", font=("Arial Black", 15)).grid(column=0, row=0, sticky=W)
        self.entry_woorden = Entry(self)
        self.entry_woorden.grid(column=0, row=1, sticky=W + E)
        self.entry_woorden.bind("<Return>", lambda e: self.insert_words())

        self.btn_insert = Button(self, text="Search", style="AccentButton", command=self.run_search)
        self.btn_insert.grid(column=1, row=1, sticky=W + E)

        Label(self, text="Keywords").grid(column=0, row=2, sticky=W)

        self.cbx_keys_options = Combobox(self, values=self.keys_options, state='readonly')
        self.cbx_keys_options.grid(column=1, row=2, sticky=W+E)
        self.cbx_keys_options.current(0)

        self.var_kernwoorden = Variable()
        self.lst_kernwoorden = Listbox(self, listvariable=self.var_kernwoorden, height=5)
        self.lst_kernwoorden.grid(column=0, row=3, columnspan=2, sticky=W+E)

        self.lst_kernwoorden.bind('<Double-1>', self.delete_from_list)

        Label(self, text="Founded interventions").grid(column=0, row=4, sticky=W)
        Label(self, text="Execution code").grid(column=0, row=4, sticky=E)
        self.cbx_exec_code = Combobox(self, values=self.e_codes, state='readonly')
        self.cbx_exec_code.bind("<<ComboboxSelected>>", self.filter_ecodes)
        self.cbx_exec_code.grid(column=1, row=4, sticky=W + E)
        self.var_matching_intr = Variable()
        self.lst_matching_intr = Listbox(self, listvariable=self.var_matching_intr)
        self.lst_matching_intr.grid(column=0, row=6, columnspan=2, sticky=W + E)
        self.lst_matching_intr.bind('<Double-1>', self.select_intervention)
        self.lst_matching_intr.bind("<Button-3>", lambda x: self.do_popup(x, "interventions"))

        Label(self, text="Used articles").grid(column=0, row=8, sticky=W)

        self.tree_used_article = Treeview(self, height=8)
        self.tree_used_article["columns"] = ["#1", "#2"]
        self.tree_used_article.column("#0", width=100, minwidth=20, stretch=NO)
        self.tree_used_article.column("#1", width=300, minwidth=20, stretch=YES)
        self.tree_used_article.column("#2", width=90, minwidth=20, stretch=NO)

        self.tree_used_article.heading("#0", text="Article NR", anchor=W)
        self.tree_used_article.heading("#1", text="Description", anchor=W)
        self.tree_used_article.heading("#2", text="Frequency", anchor=W)
        self.tree_used_article.bind('<Double-1>', self.select_article)
        self.tree_used_article.bind("<Button-3>", lambda x: self.do_popup(x, "articles"))

        self.tree_used_article.grid(column=0, row=9, columnspan=2, sticky=W + E)
        self.scr_tree_articles = Scrollbar(self, orient="horizontal", command=self.tree_used_article.xview)
        self.scr_tree_articles.grid(column=0, row=9, columnspan=2, sticky=W + E+ S)
        self.tree_used_article.configure(xscrollcommand=self.scr_tree_articles.set)

        self.grid(padx=20, pady=20)
        for widget in self.winfo_children():
            widget.grid(padx=3, pady=3)

    def do_popup(self, event, action):
        popup = Menu(self.container, tearoff=0)
        if action == "interventions":
            if self.matching_intervention is not None and len(self.matching_intervention) > 0:
                popup.add_command(label="Add filter",
                                  command=lambda: FilterWindow(self, action).loop())
                popup.add_command(label="Reset filter", command=lambda: self.reset_intervention_filters())
                popup.tk_popup(event.x_root, event.y_root)
        if action == "articles":
            if self.used_articles is not None and len(self.used_articles) > 0:
                popup.add_command(label="Add filter",
                                  command=lambda: FilterWindow(self, action).loop())
                popup.add_command(label="Reset filter",
                                  command=lambda: self.get_articles_for_tree())
                popup.tk_popup(event.x_root, event.y_root)

    def reset_intervention_filters(self):
        self.cbx_exec_code.set(self.e_codes[-1])
        self.filter_ecodes(event=None)

    def filter_callback(self, **kwargs):
        # print("this is a callback")
        if self.machine_interventions is not None and len(self.machine_interventions) > 0:
            self.matching_intervention.clear()  # intervention list
            excode = kwargs.get("ex_code", "")
            mach_rem = kwargs.get("remarks", "")
            client = kwargs.get("client", "")
            serial_number = kwargs.get("sn_machine", "")
            # filter by ex_code
            for intervention in self.machine_interventions:
                remarks, exec_code = intervention[1], intervention[2]  # [1:2]
                if not excode == "all":
                    if str(exec_code) == str(excode):
                        self.matching_intervention.append(remarks)
                else:
                    self.matching_intervention.append(remarks)
            # filter by remark
            if mach_rem is not None and not mach_rem == "":
                self.matching_intervention = [x for x in self.matching_intervention if mach_rem in x]
            # filter by serial number
            if serial_number is not None and not serial_number == "":
                # search intervention with serial number
                # vergelijk remarks met overeenkomstige intervention
                interventions = [x[1] for x in self.machine_interventions if serial_number in x[4]]
                self.matching_intervention = [x for x in self.matching_intervention if x in interventions]
            # filter by current user id
            if client is not None and not client == "":
                # get all sn van self.machines waar client overeenstem
                # met de sn get al machine intervention remarks
                # vergelijk remarks
                if self.machines is not None and len(self.machines) > 0:
                    client_machines = [x[0] for x in self.machines if str(x[3]) == client]
                    interventions = [x[1] for x in self.machine_interventions if x[4] in client_machines]
                    self.matching_intervention = [x for x in self.matching_intervention if x in interventions]

            self.var_matching_intr.set(self.matching_intervention)
            self.get_articles_for_tree()
        # pass

    def filter_articles_callback(self, value):
        """
        :param value: (name value, value)
        :return: None
        """
        # implementatie filter
        if value[0] == "number":
            article_number = value[1]
            self.get_articles_for_tree(self.FILTER_BY_ARTICLES, article_number)
        elif value[0] == "description":
            article_description = value[1]
            self.get_articles_for_tree(self.FILTER_BY_DESCRIPTION, article_description)

    def insert_words(self, keyword=None):
        woorden = self.entry_woorden.get()
        woorden = list(set(woorden.split()))
        self.entry_woorden.delete(0, 'end')
        if keyword is not None:
            self.kernwoorden.append(keyword)
        self.kernwoorden.extend(woorden)
        self.kernwoorden = list(set(self.kernwoorden))
        self.var_kernwoorden.set(self.kernwoorden)
        # self.run_search()

    def search_in_machine_interventions(self):
        self.matching_intervention.clear()
        self.machine_interventions = [x for x in self.machine_interventions if x is not None]
        self.used_articles = Helper.get_used_art(self.machine_interventions)
        # (0: "[ID]", 1:[DateExec],2:[ClientID],3:[Servicebon])
        self.interventions = Helper.get_firstlayer_intervention(self.machine_interventions)

        for intervention in self.machine_interventions:
            remarks = intervention[1]
            # remarks = remarks.replace('\n', ' ')
            self.matching_intervention.append(remarks)
        self.var_matching_intr.set(self.matching_intervention)

        # record findings
        servicebons = [x[3] for x in self.interventions]
        self.container.record_actions.add_results(servicebons)
        self.fill_tree_view()
        messagebox.showinfo("Information", "Data is ready!")

    def search(self):
        types = self.container.get_types()
        # type_id, description, qualification_id
        if types is not None and len(types) > 0 and len(self.kernwoorden) > 0:
            # get all machines of in types
            self.machines = Helper.get_machines(types)
            separator = self.cbx_keys_options.get()
            # get all intervention of machines that has a keyword
            self.machine_interventions = Helper.get_machine_interventions(self.machines, self.kernwoorden, separator)
            self.search_in_machine_interventions()

            # record findings exporting only bij de zoek opdrachten
            # self.container.record_actions.export_log()
            # self.container.record_actions.reset_values()
            self.container.record_actions.add_datetime()
            self.container.record_actions.add_type_machines([x[0] for x in types])
            self.container.record_actions.add_keywords(self.kernwoorden, separator)
            self.container.record_actions.add_method_search("interventions")
        else:
            messagebox.showinfo("Information", "No machine type is selected")

        # self.kill_process()
        self._thread_zoek_intervention = KillableThread(target=self.search)

    @staticmethod
    def is_article_in_interventions(article, list_curr_inter):
        # article
        # artNr 5, machineid 4 , magNR 6, intervention machine id 2
        # intervention
        # intervertionmachineid 0, Remark 7, ExecutionCode 10,  MachineId 3
        for intervention in list_curr_inter:
            if article == intervention[0]:
                return True
        return False

    @staticmethod
    def get_art_descrip(article, lis_gevond_art):
        for art in lis_gevond_art:
            if article in art[0]:
                return art[1]

    def fill_tree_curr_intervention(self, temp):
        self.tree_used_article.delete(*self.tree_used_article.get_children())
        if temp is not None and len(temp) > 0:
            for t in temp:
                artnr, description, count = t
                self.tree_used_article.insert("", 'end', text=str(artnr), values=t[1:])

    def get_articles_for_tree(self, action=None, value=None):
        showed_interv = [self.get_inter_by_str(x) for x in self.matching_intervention]
        if self.matching_intervention is not None and len(self.matching_intervention) > 0:
            articles = [x[0] for x in self.used_articles if self.is_article_in_interventions(x[3], showed_interv)]
            artcls = list(set(articles))
            temp = []
            for artnr in artcls:
                count = articles.count(artnr)
                description = self.get_art_descrip(artnr, self.gevonden_articles)
                t = (artnr, description, count)
                temp.append(t)
            temp.sort(key=lambda x: x[2], reverse=True)
            if action == self.FILTER_BY_ARTICLES:
                temp = [t for t in temp if value in t[0]]
            elif action == self.FILTER_BY_DESCRIPTION:
                temp = [t for t in temp if value.lower() in t[1].lower()]
            self.fill_tree_curr_intervention(temp)

    def fill_tree_view(self):
        self.tree_used_article.delete(*self.tree_used_article.get_children())
        if self.used_articles is not None:
            articles = [x[0] for x in self.used_articles]
            artcls = list(set(articles))

            temp = []

            for artnr in artcls:
                count = articles.count(artnr)
                description = ""
                resp = Helper.get_article_details(artnr)
                if resp is not None and len(resp) == 1:
                    nr, desc, stock = resp[0]
                    description = desc

                t = (artnr, description, count)
                temp.append(t)

            temp.sort(key=lambda x: x[2], reverse=True)
            if temp is not None and len(temp) > 0:
                for t in temp:
                    artnr, description, count = t
                    self.tree_used_article.insert("", 'end', text=str(artnr), values=(description, count))

            # record findings
            self.container.record_actions.add_used_articles([(x[0], x[2]) for x in temp])
            self.gevonden_articles = temp

    def delete_from_list(self, event):
        cs = self.lst_kernwoorden.curselection()
        if len(cs) > 0:
            if len(self.kernwoorden) > 0:
                del self.kernwoorden[cs[0]]
                self.var_kernwoorden.set(self.kernwoorden)

    def select_article(self, event):
        if self.tree_used_article.get_children() is not None and len(self.tree_used_article.get_children()) > 0:
            curItem = self.tree_used_article.selection()[0]
            item = self.tree_used_article.item(curItem)
            article_number = item["text"]

            if self.used_articles is not None and len(self.used_articles) > 0:
                intervention_articles = [x for x in self.used_articles if x[0] == article_number]
                intervention_machine = []
                for intervention in self.machine_interventions:
                    intervention_id = intervention[0]
                    machine_id = intervention[3]

                    for article in intervention_articles:
                        if intervention_id == article[3] and machine_id == article[1]:
                            intervention_machine.append(intervention)

                # show filterd intervention
                self.matching_intervention = [x[1] for x in intervention_machine]
                self.var_matching_intr.set(self.matching_intervention)
                self.get_articles_for_tree()

    # print("deze item is geselecteerd ", item['text'])

    def get_inter_by_str(self, inter_str, place=None):
        if inter_str is not None and not inter_str == 'None':
            intervention = [x for x in self.machine_interventions if x[1] == inter_str]
            if intervention is not None and len(intervention) > 0:
                if len(intervention) > 1:
                    if place is not None:
                        #  make value tabel
                        value_tabel = {}
                        id_counter = 0
                        n_counter = 0
                        for remark in self.matching_intervention:
                            if remark == inter_str:
                                el = (id_counter, n_counter)
                                value_tabel[id_counter] = n_counter
                                id_counter += 1
                        # get de right intervention
                        return intervention[value_tabel[place]]
                else:
                    return intervention[0]
        else:
            return ('None', 'None', 'None', 'None')

    def select_intervention(self, event):
        cs = self.lst_matching_intr.curselection()
        if len(cs) > 0 and self.machine_interventions is not None:
            # get intervention by remark
            remark = self.matching_intervention[cs[0]]
            machine_intervention = self.get_inter_by_str(remark, cs[0])
            # intervertionmachineid 0, Remark 7, ExecutionCode 10,  MachineId 3, serienummer 4, Interventionid 1
            articles = []
            for inter_article in self.used_articles:
                # intervention = (intervertionmachineid 0, Remark 7, ExecutionCode 10,  MachineId 3)
                # inter_art = (artNr 5, machineid 4 , magNR 6, intervention machine id 2)
                if inter_article[3] == machine_intervention[0]:
                    articles.append(inter_article)

            data_intervention = None
            for intervention in self.interventions:
                if machine_intervention[5] == intervention[0]:
                    data_intervention = intervention
                    break
            self.container.fill_details(machine_intervention, articles, self.kernwoorden, data_intervention)

    def run_search(self):
        self.insert_words()
        if not self._thread_zoek_intervention.is_alive():
            self._thread_zoek_intervention.start()
        else:
            messagebox.showinfo("Information", "Een andere process is bezig...")

    def kill_process(self):
        if self._thread_zoek_intervention.is_alive():
            self._thread_zoek_intervention.stop()
            self._thread_zoek_intervention = KillableThread(target=self.search)

    def filter_ecodes(self, event):
        if self.machine_interventions is not None and len(self.machine_interventions) > 0:
            self.matching_intervention.clear()
            excode = self.cbx_exec_code.get()
            for intervention in self.machine_interventions:
                remarks, exec_code = intervention[1], intervention[2]  # [1:2]
                if not excode == "all":
                    if str(exec_code) == str(excode):
                        self.matching_intervention.append(remarks)
                else:
                    self.matching_intervention.append(remarks)
            self.var_matching_intr.set(self.matching_intervention)
            self.get_articles_for_tree()


class ZoekTypeToestel(Frame):
    def __init__(self, container):
        super().__init__(container, style="Card")
        # self.lst_gevonden = None  # type: Listbox
        # self.lst_selected = None  # type: Listbox
        self.response = []
        self.container = container  # type: App
        self._thread_zoek = KillableThread(target=self.search)
        self.selected_values = []
        self.__create_widgets()
        personalise(self)

    def __create_widgets(self):
        Label(self, text="Search type", font=("Arial Black", 15)).grid(column=0, row=0, columnspan=5, sticky=W)
        Label(self, text="Machine Type").grid(column=0, row=1, sticky=W)
        self.ent_type_toestel = Entry(self)
        self.ent_type_toestel.grid(column=1, row=1, sticky=W + N + S + E)
        self.ent_type_toestel.bind("<Return>", lambda e: self.run_zoek())

        Label(self, text="Department").grid(column=2, row=1, sticky=W)
        self.ent_afdeling = Entry(self)
        self.ent_afdeling.grid(column=3, row=1, sticky=W + N + S + E)
        self.ent_afdeling.bind("<Return>", lambda e: self.run_zoek())

        btn_zoek = Button(self, text="Search", style='AccentButton',command=self.run_zoek)
        btn_zoek.grid(column=4, row=1, sticky=W + N + S + E)

        Label(self, text='Founded types').grid(column=0, row=4, columnspan=2, sticky=W)

        btn_select_all = Button(self, text="Select all", command=self.set_all)
        btn_select_all.grid(column=3, row=4, sticky=E + W, columnspan=2)

        # values = []
        # for value in range(100):
        #     values.append(value)
        self.gevonden_values = Variable()

        self.lst_gevonden = Listbox(self, listvariable=self.gevonden_values)
        self.lst_gevonden.bind('<Double-1>', self.select)
        self.lst_gevonden.grid(column=0, row=5, columnspan=5, sticky=W + N + S + E)

        Label(self, text='Selected types').grid(column=0, row=6, columnspan=2, sticky=W)
        btn_empty_list = Button(self, text="Empty list", command=self.delete_all)
        btn_empty_list.grid(column=3, row=6, sticky=E + W, columnspan=2)

        self.var_selected_values = Variable()
        self.lst_selected = Listbox(self, listvariable=self.var_selected_values)
        self.lst_selected.bind('<Double-1>', self.unselect)
        self.lst_selected.grid(column=0, row=7, columnspan=5, sticky=W + N + S + E)

        self.grid(padx=20, pady=20)
        for widget in self.winfo_children():
            widget.grid(padx=3, pady=3)

    def search(self):
        # self.container.record_actions.export_log()
        # self.container.record_actions.reset_values()
        type_toestel = self.ent_type_toestel.get()
        afdeling = self.ent_afdeling.get()

        type_machines = Helper.get_type_machines(type_toestel, afdeling)
        # type_id, description, afdeling

        self.response = type_machines
        lines = []
        for toestel_type in type_machines:
            lines.append(self.get_line_for_list(toestel_type))
        # self.selected_values.clear()
        # self.var_selected_values.set(self.selected_values)
        self.gevonden_values.set(lines)
        messagebox.showinfo("Information", "Data is ready!")
        self._thread_zoek = KillableThread(target=self.search)

    def get_line_for_list(self, toestel_type):
        type_id, description, qual_id = toestel_type
        line = "{} - {}: {} ".format(qual_id[:3], description, type_id)
        return line

    def select(self, event):
        cs = self.lst_gevonden.curselection()
        if len(cs) > 0:
            line = self.get_line_for_list(self.response[cs[0]])
            self.selected_values.append(line)
            self.selected_values = sorted(set(self.selected_values))
            self.var_selected_values.set(self.selected_values)

    def unselect(self, event):
        cs = self.lst_selected.curselection()  # type: tuple
        if len(cs) > 0:
            del self.selected_values[cs[0]]
            self.var_selected_values.set(self.selected_values)

    def set_all(self):
        elements = self.gevonden_values.get()
        self.selected_values.extend(elements)
        self.selected_values = sorted(set(self.selected_values))
        self.var_selected_values.set(self.selected_values)

    def delete_all(self):
        # if self.empty_list.get() == 1:
        self.selected_values.clear()
        self.var_selected_values.set(self.selected_values)

    def get_selected_values(self):
        res = []
        for type_machine in self.response:
            # make every toestel only een keer tonene:
            values = list(set(self.selected_values))
            if self.get_line_for_list(type_machine) in values:
                res.append(type_machine)
        return res

    def run_zoek(self):
        if not self._thread_zoek.is_alive():
            self._thread_zoek.start()

    def kill_process(self):
        if self._thread_zoek.is_alive():
            self._thread_zoek.stop()

            self._thread_zoek = KillableThread(target=self.search)


# todo:/
#  *opvolgen toestel = history (volgende update)


class App(Frame):
    def __init__(self, container):
        """
        :param container: tk window
        """
        super().__init__(container)
        self.container = container
        self.record_actions = RecordClass()
        self.plan_item_zoekers = []
        self.__create_menu_bar()
        self.__create_widgets()

    def __create_menu_bar(self):
        menubar = Menu(self.container)

        action_menu = Menu(menubar, tearoff=0)
        action_menu.add_command(label="Kill process", command=lambda: self.kll_processes())
        action_menu.add_command(label="Record search", command=lambda: self.record_actions.export_log())

        search_menu = Menu(menubar, tearoff=0)
        search_menu.add_command(label="In plan items", command=lambda: self.zoek_plan_items())
        search_menu.add_command(label="In stock", command=lambda: self.compare_mag())

        menubar.add_cascade(label="Action", menu=action_menu)
        menubar.add_cascade(label="Search", menu=search_menu)

        self.container.config(menu=menubar)

    def __create_widgets(self):
        # self.btn_kll_processes = Button(self, text="kill processes", command=self.kll_processes)
        # self.btn_kll_processes.grid(column=0, row=0, sticky=W)
        #
        # self.btn_zoek_in_planning = Button(self, text="In plan items", command=self.zoek_plan_items)
        # self.btn_zoek_in_planning.grid(column=1, row=0, sticky=W)

        self.zoek_type_frm = ZoekTypeToestel(self)
        self.zoek_type_frm.grid(column=0, row=1, sticky=W + N)
        self.zoek_machine_intervention_frm = ZoekMachineInterventions(self)
        self.zoek_machine_intervention_frm.grid(column=1, row=1, sticky=W + N)
        self.details_frm = Details(self)
        self.details_frm.grid(column=2, row=1, sticky=W + N)
        # self.btn_compare_mag = Button(self, text="Compare", command=self.compare_mag)
        # self.btn_compare_mag.grid(column=2, row=0, sticky=W + N)

        for widget in self.winfo_children():
            # if not widget == self.btn_kll_processes:
            widget.grid(padx=3, pady=3)

    def get_types(self):
        res = self.zoek_type_frm.get_selected_values()
        return res

    def fill_details(self, intervention, articles, keywords, extras=None):
        # inter_id, rem, ex_code, mach_id = intervention
        self.details_frm.fill_details(intervention, articles, keywords, extras)

    def get_article_description(self, article):
        for art in self.zoek_machine_intervention_frm.gevonden_articles:
            # art[0] partnummer
            # article[0] partnummer
            if art[0] == article[0]:
                # art[1] article description
                return art[1]

    def kll_processes(self):
        self.zoek_machine_intervention_frm.kill_process()
        self.zoek_type_frm.kill_process()
        # eliminate exit window
        self.plan_item_zoekers = [x for x in self.plan_item_zoekers if not x.exit_flag]
        for plan_zoeker in self.plan_item_zoekers:
            plan_zoeker.kill_process()

    def zoek_plan_items(self):
        if self.zoek_type_frm.get_selected_values() is not None and len(self.zoek_type_frm.get_selected_values()) > 0:
            # self.record_actions.export_log()
            # self.record_actions.reset_values()
            self.record_actions.add_datetime()
            self.record_actions.add_method_search("Planned Items")
            plan_item_zoeker = ZoekPlannedItems(self)
            self.plan_item_zoekers.append(plan_item_zoeker)
            plan_item_zoeker.run_main_loop()
        else:
            messagebox.showinfo("Information", "No machine type selected!")

    def search_from_pln_items(self, service_bons, keyword):
        # print(service_bons)
        if service_bons is not None and len(service_bons) > 0:
            types = self.zoek_type_frm.get_selected_values()
            if types is not None and len(types) > 0:
                self.record_actions.add_type_machines([x[0] for x in types])
                machines = Helper.get_machines(types)
                # print(machines)
                if machines is not None and len(machines) > 0:
                    intervention = Helper.get_mach_intervention_by_planItems(machines, service_bons)
                    if intervention is not None and len(intervention) > 0:
                        # print(intervention)
                        # self.record_actions.add_results(service_bons)
                        self.zoek_machine_intervention_frm.machine_interventions = intervention
                        self.zoek_machine_intervention_frm.insert_words(keyword)
                        self.zoek_machine_intervention_frm.search_in_machine_interventions()

    def compare_mag(self):
        if self.zoek_type_frm.get_selected_values() is not None and len(self.zoek_type_frm.get_selected_values()) > 0:
            self.record_actions.add_is_compare_used(True)
            wd_compare_magazijn = CompareMagzijn(self)
            wd_compare_magazijn.fill_current_articles(self.zoek_machine_intervention_frm.gevonden_articles)
            wd_compare_magazijn.loop()
        else:
            messagebox.showinfo("Information", "No machine type selected!")


def personalise(tkobjt):
    pass

def main():
    root = Tk()
    # root.call('source', 'themes\\azure-dark.tcl')
    # Style().theme_use('azure-dark')
    root.call('source', 'themes\\azure.tcl')
    Style().theme_use('azure')
    root.title("Assistant")
    root.geometry("1200x600")
    app = App(root)
    # app.grid(column=0, row=0, padx=10, pady=10)
    app.pack(side=TOP, fill=BOTH, expand=YES)
    root.mainloop()
    # app.record_actions.export_log()


if __name__ == '__main__':
    main()
    exit()
