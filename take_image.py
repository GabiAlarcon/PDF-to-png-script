from pdf2image import convert_from_path
from cmd_class import CmdUtils as cmd
source_path =r'directory to image locations'
file_name = 'path to file input'

input_file = '{}.pdf'.format(file_name)
data_source = r'{}{}'.format(source_path, input_file)

#data_source = 
first_page = 1
last_page = 1



output_file_sufix = file_name.replace("extr_", '')
output_file_sufix = output_file_sufix.replace("Service Manual_", '')

output_path = r'path to outpur directory'
out_dir = '{}\{}'.format(output_path, output_file_sufix)
cmd.mkdir(out_dir)


# Store Pdf with convert_from_path function
images = convert_from_path(data_source, first_page=first_page, last_page = last_page)
#print(len(images))
images[0].save(output_file, 'JPEG')
for index, image in enumerate(images):
    output_file = r'{}\{}_pag-{}.jpg'.format(out_dir, output_file_sufix, (index+first_page))
    # Save pages as images in the pdf
    image.save(output_file, 'JPEG')
