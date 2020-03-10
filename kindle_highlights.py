#! python3
# -*- coding: utf-8 -*-

import os, codecs, re
from collections import defaultdict

path_kindle = os.path.abspath(os.getcwd())
input_folder = 'input_files'      
output_folder = 'output_files'
os_path_input = os.path.join(path_kindle, input_folder)
os_path_output = os.path.join(path_kindle, output_folder)

files_raw = os.listdir(os_path_input)   # List of files in the input folder

files_list = [os.path.join(os_path_input,filename) for filename in files_raw if ".txt" in filename]  # List of TXT files with their paths
        
for file_path in files_list:
    with codecs.open(file_path, 'r', 'utf-8') as f:              # Open file
        txt = f.readlines()
        txt = [item.replace('\ufeff','') for item in txt]        #Codification at the begining of the txt file
                              
                              
    list_of_highlights = [txt[i: i + 5] for i in range(0, len(txt), 5)]  # Unpacking original list into a list of lists
    # Alternative code: list_of_highlights = [i for i in zip(*[iter(txt)]*5)]

    dictio_books = defaultdict(list)           # DefaultDic = {key: [values]}

    for title, __, __, highlight, __ in list_of_highlights:
        dictio_books[title].append('* ' + highlight)
  
books_d = dict(dictio_books)                   # Traditional Dictionary
 
books = []
clips = []            

for b, c in books_d.items(): 
    b = b.replace('\r\n','')                      #Remove \r from book's name
    b = re.sub(r'[^A-Za-zÀ-ÿ0-9-()\s]','',b)    #Remove special characters from book's name             
    books.append(b)                             #List of Books Names
    clips.append("\r\n".join(c))                #List of Highlights, unified in one string each.
  
for b,c in zip(books, clips):
    with codecs.open(os_path_output + '/{}.txt'.format(str(b)),'w+','utf_8') as file:    #Asign Book's Title as file name
        file.write(str(b))                                                        # Write Book's Title in txt file
        file.write(str('\r\n\r\n\r\n'))                                           # Add spaces between title and highlights
        file.write(str(c))                                                        # Write Highlights in txt file