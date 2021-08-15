from datetime import datetime
import json
import os
import os.path


class RecordClass:
    def __init__(self):
        self.log = dict()
        self.log["articles"] = []  # list of tuples (articlenr, freq)
        self.log["type_machines"] = []
        self.log["keywords"] = []
        self.log["keyword_bind"] = ""
        self.log["method_search"] = ""
        self.log["compare_used"] = False
        self.log["datetime"] = ""
        self.log["service_bons"] = []  # all verschillende servicebons

    def add_type_machines(self, type_machines):
        self.log["type_machines"]= type_machines

    def add_keywords(self, keywords, binding_woord):
        self.log["keywords"].extend(keywords)
        self.log["keyword_bind"] = binding_woord

    def add_method_search(self, search_method):
        self.log["method_search"] = search_method

    def add_is_compare_used(self, is_used):
        self.log["compare_used"] = is_used

    def add_results(self, results):
        # print("service bons is added")
        # print(results)
        self.log["service_bons"] = results.copy()

    def add_used_articles(self, articles):
        """
        :param articles: list[] of (article_number, frequency)
        :return: None
        """
        articles = [{"art": x[0], "freq": x[1]} for x in articles]
        # print("used articles is added")
        # print(articles)
        self.log["articles"] = articles.copy()

    def add_datetime(self):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        self.log["datetime"] = dt_string

    def save_records(self, f_name):
        with open('{}.json'.format(f_name), 'w') as fp:
            json.dump(self.log, fp, indent=4)
            fp.close()

    def export_log(self):
        """
        name is datetime only if there is data to export
        :return: ->export alle data to file_name after reset worden alle values gereset
        """
        if self.log["datetime"] is not None and not self.log["datetime"] == "":
            logs_dir = ''
            user = 'default'
            program_data = 'data\program_data.json5'
            with open(program_data) as f:
                config = json.load(f)
                logs_dir = config.get("logs_records_path", "")
                user = config.get("user", "default")
            file_name = user+" "+self.log["datetime"].replace("/", "")
            file_name = file_name.replace(" ", "_")
            file_name = file_name.replace(":", "")
            cwd = os.getcwd()
            if not logs_dir == "" and os.path.exists(logs_dir):
                if not user in os.listdir(logs_dir):
                    os.makedirs(os.path.join(logs_dir, user))
                logs_dir = os.path.join(logs_dir, user)
                file_name = os.path.join(logs_dir, file_name)
                self.save_records(file_name)
            elif "logs" in os.listdir(cwd):
                folder = os.path.join(cwd, "logs")
                file_name = os.path.join(folder, file_name)
                self.save_records(file_name)
        self.reset_values()

    def reset_values(self):
        self.log["articles"].clear()  # list of tuples (articlenr, freq)
        self.log["type_machines"].clear()
        self.log["keywords"].clear()
        self.log["keyword_bind"] = ""
        self.log["method_search"] = ""
        self.log["compare_used"] = False
        self.log["datetime"] = ""
        self.log["service_bons"].clear()  # all verschillende servicebons


