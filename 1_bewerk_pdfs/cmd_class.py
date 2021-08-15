import shutil
import os
from datetime import datetime as dt
class FoutieveRange(Exception):
    pass
# maak schrijf logs naar file
class CmdUtils:
    # Deze classe bevat methodes om systeem acties uit te voeren
    # deze bevat ook methodes om CMD programas te maken
    @staticmethod
    def ask_int(message):
        while True:
            try:
                nummer = int(input(message))
                return nummer
            except ValueError:
                print('Dat is geen integer!')
                
    @staticmethod            
    def ask_page_range():
        while True:
            try:
                begin = CmdUtils.ask_int('Begin pagina: ')
                eind  = CmdUtils.ask_int('Eind pagina: ')
                if begin < eind:
                    return begin, eind
                elif 0 < eind <= begin:
                    return begin, begin
                else:
                    raise FoutieveRange()
            except FoutieveRange:
                print('Foute ingave')
                
    @staticmethod       
    def ask_sufix():
        while True:
            sufix = input('Wat is de sufix van het bestaand?: ')
            if sufix:
                return '_'+sufix
            else:
                print('De sufix is empty!')
                
    @staticmethod       
    def ask_prefix():
        while True:
            prefix = input('Wat is de prefix van het bestaand?: ')
            if prefix:
                return prefix+'_'
            else:
                print('De prefix is empty!')
                
    @staticmethod            
    def clear():
        cls = os.system('cls')
        
    @staticmethod
    def print_files(files):
        for i,file in enumerate(files):
            print(f'{i+1}-' ,file)

    @staticmethod
    def get_all_files():
        return os.listdir()
    
    @staticmethod
    def get_file_name(file):
        file, extention = os.path.splitext(file)
        return file
    
    @staticmethod
    def choose_file(files, num):
        try:
            index = int(num)
            return files[num]
        except ValueError:
            print('give_file_name: geen index gegeben (ValueError)')

    @staticmethod
    def set_file_in_map(file_name, output_map = ''):
        #output_verwerkte_files(file_name)

        source = os.getcwd() +'\\' +file_name
        print('moving source', source)
        if not output_map:
            output_map = 'bewerkte'
        CmdUtils.mkdir(output_map)
        os.chdir(output_map)
        CmdUtils.move_file(source, os.getcwd())
        os.chdir('..')

    @staticmethod    
    def ask_bevestiging(message):
        print(message)
        while True:
            asw = CmdUtils.ask_int('1- yes, 2- no: ')
            if asw == 1:
                return True
            elif asw == 2:
                return False
            else:
                print('Dat is geen optie!')

    @staticmethod            
    def enkel_pdf_in_list(files):
        file_namen = []
        for i, file in enumerate(files):
            file_name, extention = os.path.splitext(file)
            if extention == '.pdf':
                if CmdUtils.is_file_verwerkt_geweest(file):
                    continue
                else:
                    file_namen.append(file)
                    #print(file, 'wordt verwerkt')
            else:
                continue
        return file_namen

    @staticmethod
    def save_verwerkte_file(file, output = ''):     
        if not output:
            output = 'verwekte_files.txt'
        if not output in os.listdir():
            f = open(output, 'w')
            f.close()
            
        f = open(output, 'a')
        f.write(file+'\n')
        f.close()
        
    @staticmethod
    def write_err_log(message, output = 'err_logs.txt'):
        #write to file
        if not output in os.listdir():
            f = open(output, 'w')
            f.close()
            
        f = open(output, 'a')
        f.write(message+'\n')
        f.close()

    @staticmethod
    def is_file_verwerkt_geweest(file, verwerkte_file ='verwekte_files.txt'):
        if not verwerkte_file in os.listdir():
            f = open(verwerkte_file,'w')
            f.close()
            
        f = open(verwerkte_file, 'r')
        lines = f.readlines()   
        for i, line in enumerate(lines):
            lines[i] = line.rstrip("\n")
            
        if file in lines:
            return True
        else:
            return False

    @staticmethod        
    def mkdir(path):
        """Make director
        Parameters
        ----------
        path : str
        
        """
        if not os.path.exists(path):
            os.makedirs(path)
    
    @staticmethod
    def chdir(path):
        if not os.path.exists(path):
            print('Dat map bestaat niet!')
            return None
        os.chdir(path)
        

    @staticmethod
    def get_files_with_extention(extention, path = ''):
        files = []
        if path:
            os.chdir(path)
        if not '.' in extention:
            extention = f'.{extention}'
            
        for file in os.listdir():
            f, ext = os.path.splitext(file)
            if not ext == extention:
                continue
            files.append(file)

        return files

    @staticmethod
    def move_file(source, destination):
        #beweegt files naar de dest map
        #dit om bewerkte bestaanden op te slaan
        dest = shutil.move(source, destination)

    @staticmethod
    def eliminate_line_feed(str_line):
        str_line = str(str_line)
        n_line = str_line.split("\n")
        return ''.join(n_line)

    @staticmethod
    def eliminate_continue_line(str_line):
        str_line = str(str_line)
        n_line = str_line.split("-\n")
        return ''.join(n_line)

    @staticmethod
    def eliminate_special_char(str_line, char):
        str_line = str(str_line)
        n_line = str_line.split(char)
        return ''.join(n_line)

    @staticmethod
    def process_string(str_line):
        str_line = CmdUtils.eliminate_special_char(str_line,'')
        str_line = CmdUtils.eliminate_continue_line(str_line)
        str_line = CmdUtils.eliminate_line_feed(str_line)
        return str_line

    @staticmethod
    def log(msg, file_name ='', path = ''):
        if not file_name:
            file_name = 'log.txt'
        if path:
            CmdUtils.chdir(path)
            file_name = r'{}\{}'.format(path, file_name)

        now = dt.now()
        today = now.strftime("%d/%m/%Y %H:%M:%S")

        msg =  '{}: {}\n'.format(today, msg)
        f = open(file_name,'a')
        f.write(msg)
        f.close()

    @staticmethod
    def exists(path_to_file):
        return os.path.isfile(path_to_file)

    @staticmethod
    def is_file_empty(path_to_file):
        return os.stat(path_to_file).st_size == 0
