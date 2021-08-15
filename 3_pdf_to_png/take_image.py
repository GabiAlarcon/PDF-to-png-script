from pdf2image import convert_from_path
from cmd_class import CmdUtils as cmd


# INPUT FILE NAME
file_name = 'Service Manual_1210_1510_Troubleshooting'

# pagina range
first_page = 37
last_page = 40

source_path = r'Data'
input_file = '{}.pdf'.format(file_name)
data_source = r'{}\{}'.format(source_path, input_file)


output_file_sufix = file_name.replace("Service Manual_", '')
output_file_sufix = output_file_sufix.replace('_Troubleshooting', '')
output_path = r'Data\Images'
out_dir = '{}\{}'.format(output_path, output_file_sufix)
cmd.mkdir(out_dir)
# Store Pdf with convert_from_path function
images = convert_from_path(data_source, first_page=first_page, last_page= last_page)
for index, image in enumerate(images):
    output_file = r'{}\{}_pag-{}.png'.format(out_dir, output_file_sufix, (index+first_page))
    # Save pages as images of the pdf page
    image.save(output_file, 'PNG')


