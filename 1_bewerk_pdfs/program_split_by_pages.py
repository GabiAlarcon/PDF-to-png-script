import os
from cmd_class import CmdUtils as cmd
from pdf_vrwkr import PDFVerwerker as vkr
import PyPDF2

# deze is een command programma
# die toelaat een meer manuele handeling om pages te splitsen

def split_pdf_to_file(file, output_name, dest_map='Troubleshooting'):
    verwerker = vkr(file)
    print(file)
    try:
        split_into(dest_map, verwerker, output_name)
        cmd.save_verwerkte_file(file)

    except PyPDF2.utils.PdfReadError as err:
        err_message = f'{err} in file: {file}'
        write_err_log(err_message)
    except Exception as e:
        err_message = f'{e} in file: {file}'
        cmd.write_err_log(err_message)

def split_into(dest_map, verwerker, output_name):
    try:
        cmd.mkdir(dest_map)
        pages = verwerker.get_pages_by_chapter(dest_map)
        verwerker.split(pages,output_name)
        print (output_name)
        cmd.move_file(output_name,dest_map)
    except Exception as e:
        err_message = f'{e} in file: {output_name}'
        cmd.write_err_log(err_message)

def split_pages(file, output, pages):
    verwerker = vkr(file)
    verwerker.split(pages, output)
    
#ARGUMENTS
data_source = r'.\Data\Original'
cmd.chdir(data_source)
files = cmd.get_files_with_extention('pdf')
dest_map = r'.\Data\Troubleshooting'
sufix = 'Troubleshooting'
cmd.clear()
sub_prog = cmd.ask_int('Kies het subprogramma\n1. Splitten door pages\noptie: ')
#sub_prog = cmd.ask_int('Kies het subprogramma\n1. Splitten door chapters\n2. Splitten door pages\noptie: ')
#subprogrammas
if sub_prog == -1:
    #splitssen door chapters
    while True:
        cmd.print_files(files)
        num = cmd.ask_int('welke bestand wilt je splitsen?: ')
        num -= 1
        if num <len(files):
            
            pdf_file = cmd.choose_file(files, num)
            if not cmd.is_file_verwerkt_geweest(pdf_file):
                #sufix = cmd.ask_sufix()
                out_file_name = cmd.get_file_name(pdf_file)+'_'+sufix+'.pdf'
                print('input file:', pdf_file)
                print('output file:', out_file_name)
                if cmd.ask_bevestiging('zijn gegevens juist?'):
                    split_pdf_to_file(pdf_file, out_file_name , dest_map)
                if cmd.ask_bevestiging('wil je stoppen?'):
                    break
                cmd.clear()
            else:
                print('file {} is al bewerkt!'.format(pdf_file))
                if cmd.ask_bevestiging('wil je stoppen?'):
                    break
                else:
                   cmd.clear() 
        else:
            print("niet mogelijk!")
            break
elif sub_prog == 1:
    #splitseen door pages
    while True:
        cmd.print_files(files)
        num = cmd.ask_int('welke bestand wilt je splitsen in pages?: ')
        num -= 1
        if num <len(files):
            pages = cmd.ask_page_range()
            pdf_file = cmd.choose_file(files, num)
            suf = cmd.ask_sufix()
            out_file_name = cmd.get_file_name(pdf_file)+'_'+suf+'.pdf'
            print('input file:', pdf_file)
            print('output file:', out_file_name)
            if cmd.ask_bevestiging('zijn gegevens juist?'):
                split_pages(pdf_file, out_file_name , pages)
            if cmd.ask_bevestiging('wil je stoppen?'):
                break
            else:
                cmd.clear()
        else:
            print("niet mogelijk!")
            break
else:
    print('dat optie is niet mogelijk!...')
