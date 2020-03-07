#! python3
# -*- coding: utf-8 -*-

import re, os, codecs
from collections import defaultdict

path_kindle = os.path.abspath(os.getcwd())
input_folder = 'input_files'      
output_folder = 'output_files'
os_path_input = os.path.join(path_kindle, input_folder)
os_path_output = os.path.join(path_kindle, output_folder)

files_raw = os.listdir(os_path_input)

files_list = []

for f in files_raw:        # To remove non TXT files and append files full paths
    if ".txt"in f:
        f_path = os.path.join(os_path_input,f)
        files_list.append(f_path)   
       
for file in files_list:
    f = codecs.open(file, 'r', encoding='utf_8')
    txt = f.read() 
    txt = txt.replace('\ufeff','')                                   #Codification at the begining of the txt file  

    regex = re.compile(r'''(
                   (.*)[\r\n|\r|\n]                              # Book Name (Autor Name). Group 1
                   (^-\s[LSHN].*)                                 # S = Subrayado, H = Highlight, N = Note. Group 2
                   [\r\n|\r|\n][\r\n|\r|\n][\r\n|\r|\n]          # Spaces
                   (.*)                                          # Highlight. Group 3
                   )''', re.VERBOSE | re.MULTILINE)

    dictio_books = defaultdict(list)                              # DefaultDic = {key: [values]}

    for groups in regex.findall(txt):
        key = groups[1]                                           # Key = Book
        value = groups[3]                                         # Value = Highlight
        dictio_books[key].append('* ' + value)                    # Adds "* " before each highlight and appends it to the list.
  
    books_d = dict(dictio_books)                                  # Traditional Dictionary
 
    books = []
    clips = []            

    for b, c in books_d.items(): 
        b = b.replace('\r','')                     #Remove \r from book's name
        b = re.sub(r'[^A-Za-zÀ-ÿ0-9-()\s]','',b)      #Remove special characters from book's name             
        books.append(b)                            #List of Books Names
        clips.append("\r\n".join(c))                 #List of Highlights, unified in one string each.
  
    for b,c in zip(books, clips):
        with codecs.open(os_path_output + '/{}.txt'.format(str(b)),'w+','utf_8') as file:    #Asign Book's Title as file name
            file.write(str(b))                                                        # Write Book's Title in txt file
            file.write(str('\r\n\r\n\r\n'))                                           # Add spaces between title and highlights
            file.write(str(c))                                                        # Write Highlights in txt file

    f.close() 