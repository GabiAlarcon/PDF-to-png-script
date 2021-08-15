from cmd_class import CmdUtils as cmd
from pdf_vrwkr import PDFVerwerker as vkr
import sys

def extract_tables(files):
    total_files = len(files)
    for i, file in enumerate(files):
        if not cmd.is_file_verwerkt_geweest(file):
            try:
                print(f'processing {i+1} of {total_files}...')
                print(f'extracting tables of {file}...')
                print('it may take a while... ')
                pdf_verwerker = vkr(file)
                tables = pdf_verwerker.extract_all_tables()
                print(f'exporting {file} to excel...')
                exl_file_name = pdf_verwerker.export_to_excel(tables)
                cmd.set_file_in_map(exl_file_name, output_map)
                cmd.save_verwerkte_file(file)
                cmd.clear()
                print('\nEND PROGRAAM... ')
                sys.exit()
            except Exception as err:
                cmd.write_err_log('unexpected error ocurred')
                sys.exit()


if __name__ == '__main__':
    #ARGUMENTS
    data_source = r'.\Data\Troubleshooting'
    output_map = r'Troubleshooting_Tables'
    cmd.chdir(data_source)
    cmd.mkdir('Troubleshooting_Tables')
    files = cmd.get_files_with_extention('.pdf')
    cmd.print_files(files)
    extract_tables(files)
