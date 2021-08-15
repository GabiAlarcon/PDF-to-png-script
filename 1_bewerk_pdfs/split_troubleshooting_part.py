from pdf_vrwkr import PDFVerwerker
import os
import PyPDF2
import shutil

# Deze script zal alle pdfs in een "source_map" 
# die "Service_manual_" in hun naam hebben,
# inlezen een het deel Troublshotting splitsen
# de niuwe pdf zal opgeslagen worden in "destination"

def split_pdf_to_file(file,destination, hoofdstuk='Troubleshooting', sufix_outp_file= '_Troubleshooting.pdf', ):
    filename, file_extension = os.path.splitext(file)
    #print(filename, file_extension)
    if file_extension == '.pdf':
        verwerker = PDFVerwerker(file)
        try:
            output_name = file.split('.pdf')[0]+ sufix_outp_file
            split_into(hoofdstuk, destination,verwerker, output_name)
            return file

        except PyPDF2.utils.PdfReadError as err:
            err_message = f'{err} in file: {file}'
            write_err_log(err_message)
        except Exception as e:
            err_message = f'{e} in file: {file}'
            write_err_log(err_message)
            
def write_err_log(message, out_file = 'err_logs.txt'):
    #move one dir up
    os.chdir('..')
    #write to file
    f = open(out_file, 'a')
    f.write(message+'\n')
    f.close()
    #go back to service manuals
    os.chdir(source_map)

def split_into(hoofstuk,destination, verwerker, output_name):
    #move to correct folder
    try:
        os.chdir(current_map)
        os.chdir(destination)
        # geeft pagina range van een bepaalde hoofdstuk
        pages = verwerker.get_pages_by_chapter(hoofstuk)
        # PDF splisen en
        verwerker.split(pages,output_name)
        print (output_name)
        os.chdir(current_map)
        os.chdir(source_map)
    except Exception as e:
        err_message = f'{e} in file: {file}'
        write_err_log(err_message)

def move_file(source, destination):
    #beweegt files naar de dest map
    #dit om bewerkte bestaanden op te slaan
    dest = shutil.move(source, destination)
    
def only_pdfs_in_list(files):
    for file in files:
        if file.endswith(".pdf"):
            continue
        files.remove(file)
    return files

if __name__ == '__main__':
    current_map = os.getcwd()
    source_map = r'.\Data\Original' # map locatie is relatief gegeven
    destination = r'.\Data\Troubleshooting' # map locatie is relatief gegeven
    # gelezen_pdf = 'gelezen'
    os.chdir(source_map)
    files = only_pdfs_in_list(os.listdir()) # neem enkel pdf bestaanden in een map
    verwerkte_files = []
    """
    split_pdf_to_file: zoekt de pagina-range van een hoofdstuk in een PDF
    vervolgens zal deze pagina-range splitsen en dit opslaan in destination
    Het nieuwe bestand naam zal een sufix hebben nl. '_troubleshooting.pdf' 
    het return de naam van de reeds bewerkte file om en log te kunnen maken
    van de al de bewerkte files en voor debuggen
    """
    for file in files:

        verwerkte_file = split_pdf_to_file(file=file, destination=destination,
                                           hoofdstuk='Troubleshooting',
                                           sufix_outp_file='_troubleshooting.pdf')
        if verwerkte_file:
            verwerkte_files.append(verwerkte_file)


    #gaat naar de juist map voor de verwerkte bestanden te kopieren
    os.chdir(current_map)
    os.chdir(source_map)

