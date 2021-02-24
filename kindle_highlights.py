#! usr/bin/python3
# -*- coding: utf-8 -*-

import codecs
import re
from collections import defaultdict
from pathlib import Path

path_kindle = Path(__file__).parent
input_folder = 'input_files'      
output_folder = 'output_files'
os_path_input = path_kindle.joinpath(input_folder)
os_path_output = path_kindle.joinpath(output_folder)

files_list = os_path_input.glob('*.txt')   # List of TXT files in the input folder
dictio_books = defaultdict(list)                          # DefaultDic = {key: [values]}       

for file_path in files_list:
    with codecs.open(file_path, 'r', 'utf-8') as f:              # Open file
        txt = f.readlines()
        txt = [item.replace('\ufeff','') for item in txt]        # Codification at the begining of the txt file
        txt = [item.replace('\n','') for item in txt]   
        txt = [item.replace('\r','') for item in txt]                       
                              
    list_of_highlights = [txt[i: i + 5:3] for i in range(0, len(txt), 5) if txt[i+3] != ""]  # Unpacking original list into a list of lists
    # Alternative code: list_of_highlights = [i for i in zip(*[iter(txt)]*5)]

    for title, highlight in list_of_highlights:
        title = re.sub(r'[^A-Za-zÀ-ÿ0-9-()\s]','',title)      # Remove special characters from book's name     
        dictio_books[title].append('* ' + highlight)          # DefaultDic: {Title:[Highlights]}

for book, highlights in dictio_books.items():
    file_path = os_path_output.joinpath(book+".txt")     # Asign Book's Title as file name
    with codecs.open(file_path,'w+','utf_8') as file:    
        file.write(str(book))                            # Write Book's Title in txt file
        file.write(str('\r\n\r\n\r\n'))                  # Add spaces between title and highlights
        file.write('\r\n\r\n'.join(highlights))          # Write Highlights in txt file, with whitespaces between them