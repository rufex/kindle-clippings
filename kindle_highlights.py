#! python3
# -*- coding: utf-8 -*-

# Kindle Highlights py - Developed for Kindle Version 4 in Spanish. It may not work for other Kindle versions or languages.

import re, codecs
from collections import defaultdict

f = codecs.open('.\\input\\Mis recortes.txt', 'r', 'utf-8')
txt = f.read() 
txt = txt.replace('\ufeff','')                                   #Codification at the begining of the txt file  

regex = re.compile(r'''(
                   (.*)[\r\n|\r|\n]                              # Book Name (Autor Name). Group 1
                   (^-\s[SHN].*)                                 # S = Subrayado, H = Highlight, N = Note. Group 2
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
    b = re.sub(r'[^A-Za-z0-9-()\s]','',b)      #Remove special characters from book's name             
    books.append(b)                            #List of Books Names
    clips.append("\n\r\n".join(c))             #List of Highlights, unified in one string each. Space between each higlight.
  
for b,c in zip(books, clips):
    with codecs.open('.\\output\\{}.txt'.format(str(b)),'w+','utf-8') as file:    #Asign Book's Title as file name
        file.write(str(b))                                                        # Write Book's Title in txt file
        file.write(str('\r\n\r\n\r\n'))                                           # Add spaces between title and highlights
        file.write(str(c))                                                        # Write Highlights in txt file

#TODO Al eliminar caracteres titulo, se eliminan letras con tilde.
        #ver libreria unicode data y normalize. Podría ser la solucion.