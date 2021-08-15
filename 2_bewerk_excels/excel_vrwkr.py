import pandas as pd
import re
from cmd_class import CmdUtils as cmd
#pip install pandas
#pip install openpyxl

# Deze classe bevat alle methodes om een excels te bewerken

class ExcelVerwerker:
    def __init__(self, file_name):
        self.file_name = file_name
        self.data_frame = pd.ExcelFile(file_name)
        

    def merge_sheets(self, begin, eind):
        #begin, eind = pages
        sheet_names = self.data_frame.sheet_names
        frames = []
        
        for sheet in sheet_names:
            page = int(sheet.split('-', 2) [1])
            if begin <= page <= eind:
                sheet_df = self.data_frame.parse(sheet)
                #if not page == begin:
                #    sheet_df = sheet_df.drop(sheet_df.index[[0,1]])
                frames.append(sheet_df)
                
        result = pd.concat(frames)

        return result

    def export_to_xlsx(self, data_frame, name):
        output = f'{name}.xlsx'
        data_frame.to_excel(output, index = False)

    def eliminate_line_feed(self, str_line):
        n_line = str_line.split("\n")
        return ' '.join(n_line)

    def split_by_format(self, txt, formaat, weg_fmt = False):
        '''
        Params:
            txt ->  str (linetekst die verwerkt dient te worden)
            formaat -> volgens regex modules tekst formaat die dient gezocht te worden
            weg_fmt -> splitsen laat de regex achter indien True zal deze weg
                        gefilterd worden
        '''
        
        result = re.split(formaat, txt)

        if weg_fmt:
            try:
                #first element [digit])
                f_el = result[0]
                if f_el:
                    result[0] = f_el.split(')', 1)[1]
            except:
                pass
            eliminate = re.compile(formaat)
            result = [s for s in result if not eliminate.match(s)]
        else:
            #wsch  niet de beste manier maar het werkt... (verdere verberteren)
            #niet verbruikbaar kijken bij volgende gevallen van andere .xlsx's
            if len(result)>1:
                e_code = ''.join(result[0:2]).strip()
                description = result[2]                  
                result = []
                result.append(e_code)
                result.append(description)

            else:
                description = result[0]
                e_code = 'NULL'
                result = []
                result.append(e_code)
                result.append(description)
        return result

    def get_biggest_number(self, teller, n_nummer):
        return max(teller, n_nummer)

    def split_columns_by_formaat(self,data_frame ,col_name, formaat, weg_fmt = False):
        stappen_teller = 0 # mischien is dit niet nodig zie fill_null_elementen
        #aantal_stappen = []
        columns = []
        for index, row in data_frame.iterrows():
            if not str(row[col_name]) == 'nan':
                line = self.eliminate_line_feed(str(row[col_name]))
                line = self.split_by_format(line, formaat, weg_fmt)
                columns.append(line)
                #aantal_stappen.append(len(line))
            else:
                columns.append([])
                #aantal_stappen.append(0)
        columns = self.fill_null_elementen(columns)
        return columns
        

        '''
        error_desc = row['Error Reference and Name']
    
        if not str(error_desc) == 'nan':
            error_desc = eliminate_line_feed(str(error_desc))
            error_desc = split_by_format(error_desc, '(\d\d\)\s)')
        
            if not len(error_desc) > 1:
                ecode.append('NULL')
                description.append(error_desc[0])
            
            else:
                ecode.append(error_desc[0])
                description.append(error_desc[1])
        '''

    def fill_null_elementen(self, bi_dim):
        max_stappen = self.get_max_length(bi_dim)
        for row in bi_dim:
            if len(row) < max_stappen:
                null_spaces = max_stappen - len(row)
                for x in range(null_spaces):
                    row.append('')
        # return is niet nodig aangezien de list een muttable element is
        return bi_dim

    def get_max_length(self, bi_dim):
        max_stappen = 0
        for row in bi_dim:
            max_stappen = max(max_stappen, len(row))
        return max_stappen

    def give_col_steps_names(self, bi_dim, prefix, indexed = True):
        column_namen = []
        max_stappen = self.get_max_length(bi_dim)
        for x in range(max_stappen):
            col_name = f'{prefix}'
            if indexed :
                col_name = col_name + '_'+str(x+1)
            column_namen.append(col_name)

        return column_namen

    def give_length_of_each_row(self, bi_dim):
        col_length = []
        for row in bi_dim:
            teller = 0
            for col in row:
                if col:
                    teller = teller +1
            col_length.append(teller)
        return col_length

    #Static methods
    
    @staticmethod
    def fill_null_elementen(bi_dim):
        max_stappen = ExcelVerwerker.get_max_length(bi_dim)
        for row in bi_dim:
            if len(row) < max_stappen:
                null_spaces = max_stappen - len(row)
                for x in range(null_spaces):
                    row.append('')
        # return is niet nodig aangezien de list een muttable element is
        return bi_dim

    @staticmethod
    def give_length_of_each_row(bi_dim):
        col_length = []
        for row in bi_dim:
            teller = 0
            for col in row:
                if col:
                    teller = teller +1
            col_length.append(teller)
        return col_length
    
    @staticmethod
    def give_col_steps_names(bi_dim, prefix, indexed = True):
        column_namen = []
        max_stappen = ExcelVerwerker.get_max_length(bi_dim)
        for x in range(max_stappen):
            col_name = f'{prefix}'
            if indexed :
                col_name = col_name + '_'+str(x+1)
            column_namen.append(col_name)
        return column_namen
            
    @staticmethod
    def get_max_length(bi_dim):
        max_stappen = 0
        for row in bi_dim:
            max_stappen = max(max_stappen, len(row))
        return max_stappen

    @staticmethod
    def export_to_excel(data_frame, name, dest = ''):
        if dest:
            cmd.mkdir(dest)
            cmd.chdir(dest)
        output = f'{name}.xlsx'
        data_frame.to_excel(output, index = False)

    @staticmethod
    def split_by_format(txt, formaat, weg_fmt = False):
        '''
        Params:
            txt ->  str (linetekst die verwerkt dient te worden)
            formaat -> volgens regex modules tekst formaat die dient gezocht te worden
            weg_fmt -> splitsen laat de regex achter indien True zal deze weg
                        gefilterd worden
        '''
        
        result = re.split(formaat, txt)
        #print('in class', result)
        if weg_fmt:
            try:
                #first element [digit])
                f_el = result[0]
                if f_el:
                    # big bug
                    pass
                    #result[0] = f_el.split(')', 1)[1]
            except:
                pass
            #print('ERROR ', result)
            eliminate = re.compile(formaat)
            result = [s for s in result if not eliminate.match(s)]
        else:
            #wsch  niet de beste manier maar het werkt... (verdere verberteren)
            #niet verbruikbaar kijken bij volgende gevallen van andere .xlsx's
            if len(result)>1:
                e_code = ''.join(result[0:2]).strip()
                description = result[2]                  
                result = []
                result.append(e_code)
                result.append(description)

            else:
                description = result[0]
                e_code = 'NULL'
                result = []
                result.append(e_code)
                result.append(description)
            result = [s for s in result if not s == 'NULL']
        return result
