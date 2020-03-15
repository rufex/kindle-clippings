#! python3
# -*- coding: utf-8 -*-

import codecs, re, datetime, yaml
from collections import defaultdict, Counter
from pathlib import Path

paths_yaml = yaml.safe_load(open("config_kindle_highlights.yml"))

bookshelf = Path(paths_yaml["Paths"]["bookshelf"])
list_books_stored = list(bookshelf.rglob('*.txt')) # List of all TXT already stored

path_kindle = Path.cwd()
os_path_input = path_kindle.joinpath(paths_yaml["Paths"]["input_folder"])
os_path_output = path_kindle.joinpath(paths_yaml["Paths"]["output_folder"])
log_list = path_kindle.joinpath(paths_yaml["Paths"]["log_file"])

files_list = os_path_input.glob('*.txt')   # List of TXT files in the input folder

now = datetime.datetime.now()
today = now.strftime("%Y-%m-%d")

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

highlight_counter = Counter()                                 # To keep the count of amount of Highlights for each book.

for book, highlights in dictio_books.items():
    if book in str(list_books_stored):
        path_file = [path for path in list_books_stored if path.stem == book]
        path_file = Path(path_file[0])
        with codecs.open(path_file, 'r', 'utf-8') as f:     # What if more than one file?
            txt_stored = f.read()
        
        clean_list = list()

        for highlight in highlights:
            if highlight not in str(txt_stored):
                clean_list.append(highlight)
                highlight_counter[book] += 1

        with codecs.open(path_file, 'a', 'utf-8') as f:
            f.write(str('\r\n\r\n'))            
            f.write('\r\n\r\n'.join(clean_list)) 

        with codecs.open(log_list, 'a', 'utf-8') as log:              # Open file
            log.write(f'[{today}] Added {highlight_counter[book]:.0f} to {path_file.stem}')

    else:
        for highlight in highlights:
            highlight_counter[book] += 1

        file_path = os_path_output.joinpath(book+".txt")     # Asign Book's Title as file name
            
        with codecs.open(file_path,'w+','utf_8') as f:    
            f.write(str(book))                            # Write Book's Title in txt file
            f.write(str('\r\n\r\n\r\n'))                  # Add spaces between title and highlights
            f.write('\r\n\r\n'.join(highlights))          # Write Highlights in txt file, with whitespaces between them
             









