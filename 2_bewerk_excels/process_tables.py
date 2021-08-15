from cmd_class import CmdUtils as cmd
from excel_vrwkr import ExcelVerwerker as vkr
import pandas as pd

#https://pythex.org/ for format testing voor splitsing

#ARGUMENTS
data_source = r'Data\only merged'
output_data_dir = r'..\Processed_tables'
machine ='1510_excel'


#CONSTANTE
file = '{}_error_codes.xlsx'.format(machine)
machine_type = machine
col_machine_naam = 'Machine_Type'
col_stap_aantal_naam = 'Aantal Stappen'
col_aantal_causes_naam = 'Aantal Causes'
col_cause_id_naam = 'Cause Nr'
prefix_col_naam = 'Stap'
out_file_naam = f'{machine_type}_error_codes'


head = []
index_nr = '0'
head.append(index_nr)
ecode = 'Ecode'
head.append(ecode)
description ='Description'
head.append(description)
#reason = 'Reason'
#head.append(reason)
pos_cause = 'Possible Cause'
head.append(pos_cause)
rem_action = 'Remedial Actions'
head.append(rem_action)

def process_table(file):
    cmd.chdir(data_source)
    print(file)
    df = pd.read_excel(file)


    laast_error_id = 0
    stappen_2d = []
    col_error_id = []
    col_ecode = []
    col_description = []
    col_reason = []
    col_posible_causes = []
    col_cause_ids = []
    col_aantal_causes = []
    laast_description = ''
    laast_ecode = ''
    split_punt = ''
    #split_punt = '|\.'
    split_format = "(\d\. |\n\d\. |\n\d\d\. |•|\d\) |\d\d\) )"



    df.columns = head
    for index, row in df.iterrows():
        #Rows
        symp_id = int(row[index_nr])
        err_code = row[ecode]
        desc = cmd.process_string(row[description])
        p_caus = cmd.process_string(row[pos_cause])
        causes = vkr.split_by_format(p_caus,split_format ,True)
        causes = [s for s in causes
                  if s]
        r_act = cmd.process_string(row[rem_action])
        actions = vkr.split_by_format(r_act,split_format ,True)
        actions = [s for s in actions if s]
        #zet alles in verschillende colommen

        for p_c in causes:
            col_error_id.append(symp_id)
            col_posible_causes.append(p_c)
            col_ecode.append(err_code)
            col_description.append(desc)
            stappen_2d.append(actions)

    #count possible causes
    # error_list = list(set(col_ecode))
    hoogste_id = max(col_ecode)
    print("hoogste id", hoogste_id)
    f_id_tabel = [0]*hoogste_id

    for eid in col_ecode:
        f_id_tabel[int(eid)-1] += 1

    for iel, el in enumerate(f_id_tabel):
        print(iel+1, el)
        for i in range(el):
            col_cause_ids.append(i+1)
            col_aantal_causes.append(el)

    #nabewerking
    stappen_2d = vkr.fill_null_elementen(stappen_2d)
    col_namen_stappen = vkr.give_col_steps_names(stappen_2d, prefix_col_naam)
    aantal_stappen_per_row = vkr.give_length_of_each_row(stappen_2d)
    col_machine_type = [machine_type]*len(stappen_2d)


    col_namen = []
    col_namen.append(col_machine_naam)
    col_namen.append(ecode)
    col_namen.append(description)
    col_namen.append(col_aantal_causes_naam)
    col_namen.append(col_cause_id_naam)
    col_namen.append(pos_cause)
    col_namen.append(col_stap_aantal_naam)



    values = []
    values.append(col_machine_type)
    values.append(col_ecode)
    values.append(col_description)
    values.append(col_aantal_causes)
    values.append(col_cause_ids)
    values.append(col_posible_causes)
    values.append(aantal_stappen_per_row)


    df = pd.DataFrame(values)
    df = df.transpose()
    df.columns = col_namen
    df1 = pd.DataFrame(stappen_2d, columns = col_namen_stappen)
    df = pd.concat([df,df1], axis=1)
    vkr.export_to_excel(df, out_file_naam, output_data_dir)
    # cmd.set_file_in_map(f'{out_file_naam}.xlsx', output_data_dir)

if __name__ == '__main__':
    process_table(file)