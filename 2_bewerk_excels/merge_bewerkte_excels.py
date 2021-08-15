import pandas as pd
from cmd_class import CmdUtils as cmd
from excel_vrwkr import ExcelVerwerker as vkr

# cmd is a hulp classe voor systeem bewerkingen
# vkr is a hulp classe voor excels bewerkingen
data_source = r'PATH TO DIRECTORY'
cmd.chdir(data_source)
# get files gebruikt os.listdir()
files = cmd.get_files_with_extention('.xlsx')

#merging routine
all_files =[]
for file in files:
    # pd (pandas) opennen en lezen van alle tabellen
    df = pd.read_excel(file)
    all_files.append(df)

# mergen van alle objecten, concat -> concatenation
result = pd.concat(all_files)
vkr.export_to_excel(result,'All_toestellen')


