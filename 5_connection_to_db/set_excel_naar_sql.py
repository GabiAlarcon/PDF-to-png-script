import pyodbc
import pandas as pd
from cmd_class import CmdUtils as cmd

#https://datatofish.com/import-csv-sql-server-python/
#https://datatofish.com/how-to-connect-python-to-sql-server-using-pyodbc/

'''
OPM : om errors te voorkomen en de database geen 2 keer invullen
zijn de  lijnen van code weg gekomenteerd
met de volgende key : [BEVEILIG]

informatie over de database van Getra zijn hier weggewerkt.! (senscitive data)

'''
def make_insert_query(argumenten):
    tabel_name = "TABEL NAAM"
    aantal_stappen = int(argumenten[6])
    stappen_labels = []
    for x in range(aantal_stappen):
        stappen_labels.append('Stap_{}'.format(x+1))
        
    stappen_labels = ', '.join(stappen_labels)
    stappen_labels = ', '+ stappen_labels
    
    # indien stappen leeg moeten zijn
    if aantal_stappen == 0:
        stappen_labels = ''

    query = ('INSERT INTO {} '.format(tabel_name) +
             '(Machine_Type, Ecode, Description, Aantal_Causes, Cause_Nr, Possible_Cause, Aantal_stappen{}) '
             'VALUES ({})'.format(stappen_labels,', '.join(argumenten)))


    return query
def make_string(arg):
    return '\'{}\''.format(arg)

def insert_to_db():
    driver = 'ODBC Driver 17 for SQL Server'
    server = 'SERVER locatie van de DATABASE'
    username = 'USERNAME' 
    password = 'PASSWOORD'
    database = ';Database=DATABASENAAM;'

    # cnxn = pyodbc.connect('DRIVER={'+driver+'};SERVER='+server+database+';UID='+username+';PWD='+ password) # [BEVEILIG]
    # cursor = cnxn.cursor() # [BEVEILIG]

    data_source = r'.\Data\All toestellen'
    cmd.chdir(data_source)
    file = 'All_toestellen Versie3.xlsx'
    df = pd.read_excel(file, sheet_name = 'Sheet1')

    for index, row in df.iterrows():
        args = []
        machine_type = make_string(row['Machine_Type'])
        ecode = make_string(row['Ecode'])
        #eliminate { ' } van de string in description
        description = make_string(' '.join(row['Description'].split('\'')))
        aantal_cause = row['Aantal Causes']
        cause_nr = row['Cause Nr']
        possible_cause = make_string(row['Possible Cause'])
        aantal_stappen = row['Aantal Stappen']

        args.append(machine_type)
        args.append(ecode)
        args.append(description)
        args.append(str(aantal_cause))
        args.append(str(cause_nr))
        args.append(possible_cause)
        args.append(str(aantal_stappen))
        
        stp_prfx = 'Stap_'
        
        for x in range(aantal_stappen):
            stap_label = '{}{}'.format(stp_prfx,x+1)
            stap = make_string(row[stap_label])
            args.append(stap)


        cursor.execute(make_insert_query(args))
        cmd.log('{} machine: {} ecode: {}'.format(index,machine_type,ecode))
        


    cnxn.commit()
    cmd.log('[INFO] insersting to Database successful')


if __name__ == '__main__':
    insert_to_db()
