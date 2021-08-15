import pyodbc
import json


class DataBase:
    driver = 'ODBC Driver 17 for SQL Server'
    program_data = '.\data\program_data.json5'
    server = ""
    username = ""
    password = ""
    db_name = ""
    def __init__(self, table_name):
        self.table_name = table_name

        def get_table_data(t_name):
            table_data = r'.\data\tables.json5'
            with open(table_data) as f:
                config = json.load(f)
                for table in config["tables"]:
                    if table.get('name') == t_name:
                        return table

        
        with open(self.program_data) as f:
            config = json.load(f)
            self.username = config.get("db_username", "")
            self.password = config.get("db_password", "")
            self.server = config.get("db_server", "")
            self.db_name = config.get("db_name", "")

        self.tb_data = get_table_data(table_name)
        self.connection = None
        self.cursor = None
        self.query = ''

    def connect_to_database(self):
        if self.connection is None:
            self.connection = pyodbc.connect('DRIVER={' + self.driver +
                                             '};SERVER=' + self.server +
                                             ';UID=' + self.username +
                                             ';PWD=' + self.password)
            self.cursor = self.connection.cursor()

    def execute_query(self, options=None, separator=''):
        # extra check to not make a mistake
        if self.connection is not None:
            if not 'DELETE FROM'.lower() in str(self.query).lower():
                if self.connection is not None and self.cursor is not None:
                    query = str(self.query+self.get_query_from_options(options, separator))
                    # print(query)
                    self.cursor.execute(query)
                    rows = self.cursor.fetchall()
                    return rows
        else:
            return ['not connected to database {}'.format(self.table_name)]

    @staticmethod
    def get_query_from_options(options, separator=''):
        result = ''
        if separator == '':
            separator = ' AND '
        if options is not None and len(options) > 0:
            # result += self.query
            result += ' WHERE '
            result += separator.join(options)
        return result


    def make_get_query(self, columns, n_rows=0):
        basis_query = "SELECT {} {} " \
                      "FROM ["+self.db_name+"].[dbo].[{}]"
        rows = ''
        if not n_rows == 0:
            rows = 'TOP ({})'.format(int(n_rows))

        self.query = basis_query.format(rows, ','.join(columns), self.table_name)

    def append_options(self, options, separator=''):
        result = ''
        if separator == '':
            separator = ' AND '
        if len(self.query) > 0 and len(options) > 0:
            # result += self.query
            result += ' WHERE '
            result += separator.join(options)
            self.query += result

    def execute_single_query(self, option=''):
        if self.connection is not None:
            query = "{}".format(self.query)
            if not option == '':
                query = "{} where {}".format(query, option)
            # print(query)
            self.cursor.execute(str(query))
            rows = self.cursor.fetchall()
            return rows
        else:
            return ['not connected to database {}'.format(self.table_name)]
