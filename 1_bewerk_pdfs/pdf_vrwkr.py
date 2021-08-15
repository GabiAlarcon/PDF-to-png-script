import os
import PyPDF2
from PyPDF2 import PdfFileReader, PdfFileWriter
import pikepdf
import fitz
import camelot

# opm install al  dependenties

class PDFVerwerker:
    # deze classe heeft alle methodes om pdf te bewerken
    def __init__(self, file):
        self.file = file
        self.pdf = PdfFileReader(file, "rb")
        if self.pdf.isEncrypted:
            print(f'{file} is encrypted')
            print('extract to encrypted  pdf to non encrypted pdf...')
            self.extract(file)
            
    def split(self, pages, into ='output.pdf'):
        pdf_writer = PdfFileWriter()
        if pages:
            begin, eind = pages
            if eind <= begin:
                #eenkel de eerste pagina
                pdf_writer.addPage(self.pdf.getPage(begin))
            else:
                for page in range(begin-1,eind-1):
                    pdf_writer.addPage(self.pdf.getPage(page))
            with open(into, 'wb') as out:
                pdf_writer.write(out)
            print ("PDF file has been splited")
        else:
            raise Exception('pages are empty')

    def give_bookmarks (self):
        '''
            https://stackoverflow.com/questions/8329748
            /how-to-get-bookmarks-page-number
        '''
        #print('first of give bookmarks')
        bookmarks = []
        outlines = self.pdf.getOutlines()
        try:
            for bookmark in outlines:
                #if isinstance(outline,dict):
                if type(bookmark) == list:
                    #print(bookmark)
                    continue
                
                pg_num = self.pdf.getDestinationPageNumber(bookmark) + 1
                direction = (pg_num,bookmark.get('/Title','NaN'))
                bookmarks.append(direction)
            return bookmarks
        except PyPDF2.utils.PdfReadError as err:
            raise PyPDF2.utils.PdfReadError
    
    def print_bookmarks(self):
        for b in self.give_bookmarks():
            page, bookmark = b
            print(bookmark,"page:", page)

    def get_pages_by_chapter(self, name=''):
        chaters = []
        try:
            chapters = self.give_bookmarks()
            #print(chapters)
            if name:
                for i, bookmark in enumerate(chapters):
                    page, chapter = bookmark
                    if not name in chapter:
                        #print(self.pdf, chapter)
                        continue
                    begin = page
                    eind, v_chapter = chapters[i+1]
                    if not eind:
                        print('geen volgende chapter')
                        length_pdf = len(self.pdf)
                        eind = length_pdf
                    return (begin, eind-1)
        except PyPDF2.utils.PdfReadError as err:
            raise err
        
        
    def extractText(self, file):
        
        #pip install fitz
        #pip install PyMuPDF
        #https://stackoverflow.com/questions/54650830/pdf-file-has-not-been-decrypted-issue-still-persists-in-pypdf2
        doc = fitz.open(file) 
        text = []
        for page in doc: 
            t = page.getText().encode("utf8") 
            text.append(t)
        return text    

    def extract (self, file):
        #extract de encrypted pdf into an unencrypted pdf
        #https://stackoverflow.com/questions/28192977/how-to-unlock-a-secured-read-protected-pdf-in-python
        #pip install pikepdf
        #import pikepdf
        pdf = pikepdf.open(file)
        pdf.save(f'extr_{file}')

    # camelot for extracting tables form a pdf
    def extract_all_tables(self):
        file = self.file
        tables = camelot.read_pdf(file, pages = "1-end")
        return tables

    def export_to_excel(self, tables, output_name = ''):
        if not output_name:
            file_name, extention = self.file.split('.')
            output_name = file_name
        file_name = f'{output_name}.xlsx'
        print('exporting tables to', file_name)
        tables.export(file_name, f="excel")
        return file_name






