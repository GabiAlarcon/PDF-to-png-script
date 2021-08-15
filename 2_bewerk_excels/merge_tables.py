from excel_vrwkr import ExcelVerwerker as e_vkr
import pandas as pd
import os
from cmd_class import CmdUtils as cmd

#ARGUMENTS
data_source = r'C:\Users\GA\Documents\automation workshop\python\Share\2_bewerk excels\Data\original'
machine_type = '1510_excel'
deel = ''
file = 'Service Manual_{}_Troubleshooting{}.xlsx'.format(machine_type,deel)

pages_to_merge = (8,34)
# machine_type += 'deel 1'

#CONSTANTS
machine_col_naam = 'Machine_Type'
stap_aantal_col_naam = 'Aantal Stappen'
prefix_col_naam = 'Stap'
out_file_naam = f'{machine_type}_error_codes'

def merge_tables():
    os.chdir(data_source)
    #class maken (opm: dit class zou eigenlijk maar statische methodes hebben)
    verwerker = e_vkr(file)
    #MERGE PAGES
    merged_df = verwerker.merge_sheets(*pages_to_merge)
    #DROP DUPLICATES
    merged_df = merged_df.drop_duplicates(keep='first')
    #GET EN SET DE FIRST ROW A KEYS
    new_keys = merged_df.iloc[0]
    merged_df.columns = new_keys
    merged_df = merged_df.drop([0])
    df = merged_df
    df.drop(columns=["Reason"])
    # print("new_col", merged_df.columns)
    laast_fault = None
    sympt_id = 0
    i = 1
    index_counter = []
    error_descriptions = []
    sympt_ids = []
    for index, row in df.iterrows():

        index_counter.append(i)
        fault_description = row["Fault"]
        # print(fault_description)
        if not laast_fault:
            laast_fault = fault_description
        if not str(fault_description) == 'nan':
            laast_fault = fault_description
            sympt_id += 1

        error_descriptions.append(laast_fault)
        sympt_ids.append(sympt_id)
        i += 1

    df = pd.DataFrame([index_counter, sympt_ids,error_descriptions, merged_df["Causes"].tolist(), merged_df["Action"].tolist()])
    df = df.transpose()
    df.columns = ["0","Ecode","Description", "Causes","Remedial Actions"]
    # print(error_descriptions)
    if not cmd.is_file_verwerkt_geweest(file):
        verwerker.export_to_xlsx(df, out_file_naam)
        file_name = '{}.xlsx'.format(out_file_naam)
        cmd.set_file_in_map(file_name, r'..\only merged')
    else:
        print('file is al bewerkt geweest')

if __name__ == '__main__':
    merge_tables()
