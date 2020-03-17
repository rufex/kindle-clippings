#! /Library/Frameworks/Python.framework/Versions/3.8/bin/python3

import codecs, re, datetime, yaml, click
from collections import defaultdict, Counter
from pathlib import Path
from operator import itemgetter

file_path = Path(__file__).parent
paths_yaml = yaml.safe_load(open(Path.joinpath(file_path,"config_kindle_highlights.yml")))

bookshelf = Path(paths_yaml["Paths"]["bookshelf"])
list_books_stored = list(bookshelf.rglob('*.txt')) # List of all TXT already stored

path_kindle = Path.cwd()
os_path_input = path_kindle.joinpath(file_path, paths_yaml["Paths"]["input_folder"])
os_path_output = path_kindle.joinpath(file_path, paths_yaml["Paths"]["output_folder"])
log_list = path_kindle.joinpath(file_path, paths_yaml["Paths"]["log_file"])

new_files_list = os_path_input.glob('*.txt')   # List of TXT files in the input folder

today = datetime.datetime.now().strftime("%Y-%m-%d")

highlight_counter = Counter()                                 # To keep the count of amount of Highlights for each book.
highlight_counter_full = Counter()
dictio_books = defaultdict(list)                          # DefaultDic = {key: [values]}
new_dictio_book = defaultdict(list)                       # DefaultDic for books that don't have previous file
existing_dictio_book = defaultdict(list)                  # DefaultDic for books that have previous file

def get_new_clippings(input_files):
    """Open txt files in the input folder and creates a dictionary with all the books and their highlights
    """
    for file_path in input_files:
        with codecs.open(file_path, 'r', 'utf-8') as f:              # Open file of clippings. Read mode
            txt = f.readlines()                                         
            txt = [item.replace('\ufeff','') for item in txt]        # Codification at the begining of the txt file
            txt = [item.replace('\n','') for item in txt]
            txt = [item.replace('\r','') for item in txt]                     
                                
        list_of_highlights = [txt[i: i + 5:3] for i in range(0, len(txt), 5) if txt[i+3] != ""]  # Unpacking original list into a list of lists
        # Alternative code: list_of_highlights = [i for i in zip(*[iter(txt)]*5)]

        for title, highlight in list_of_highlights:
            title = re.sub(r'[^A-Za-zÀ-ÿ0-9-()\s]','',title)      # Remove special characters from book's name     
            dictio_books[title].append('* ' + highlight)          # DefaultDic: {Title:[Highlights]}
            highlight_counter_full[title] += 1

def separate_clippings_new_old(dictio):
    """Separates the books that already have a file created.
    For those which already a file exists, filtrates only the new highlights.
    Keeps a count of the highlights that could be written to each file.
    """
    for book, highlights in dictio.items():
        if book in str(list_books_stored):
            path_file = [path for path in list_books_stored if path.stem == book]
            path_file = Path(path_file[0])                        # What if more than one file? It will open the first one.
            with codecs.open(path_file, 'r', 'utf-8') as f:       # Open existing file to obtain its content. Read mode.  
                txt_stored = f.read()
            
            for highlight in highlights:                          # Check if the new highlights are already stored in the existing file.
                if highlight not in str(txt_stored):
                    existing_dictio_book[book].append(highlight) 
                    highlight_counter[book] += 1
            
        else:
            for highlight in highlights:
                new_dictio_book[book].append(highlight)
                highlight_counter[book] += 1
              
def append_to_files(dictio):
    for book, highlights in dictio.items():
        path_file = [path for path in list_books_stored if path.stem == book]
        path_file = Path(path_file[0]) 
    
        with codecs.open(path_file, 'a', 'utf-8') as f:   # Open existing file. Append mode.
            f.write(str('\r\n\r\n'))            
            f.write('\r\n\r\n'.join(highlights)) 

        with codecs.open(log_list, 'a', 'utf-8') as log:              # Open log-file. Append mode.
            log_txt = f'[{today}] Added {highlight_counter[book]:.0f} to {path_file.stem}'
            log.write(log_txt)
            print(log_txt)
    
    quit()

def create_files(dictio):
    for book, highlights in dictio.items():
        path_file = os_path_output.joinpath(book+".txt")  # Asign Book's Title as file name 
        with codecs.open(path_file,'w+','utf_8') as f:    # New file. Write mode.
            f.write(str(book))                            # Write Book's Title in txt file
            f.write(str('\r\n\r\n\r\n'))                  # Add spaces between title and highlights
            f.write('\r\n\r\n'.join(highlights))          # Write Highlights in txt file, with whitespaces between them

        with codecs.open(log_list, 'a', 'utf-8') as log:              # Open log-file. Append mode.
            log_txt = f'[{today}] New TXT File. Added {highlight_counter[book]:.0f} to {path_file.stem}'
            log.write(log_txt)
            print(log_txt)
    
    quit()

def counter_of_new_highlights():
    export_list = list()
    for book, count in highlight_counter_full.items():
        if book in existing_dictio_book.keys():
            export_list.append((book,count,highlight_counter[book]))
        elif book in new_dictio_book.keys():
            export_list.append((book,count,highlight_counter_full[book]))
        elif book not in existing_dictio_book.keys() and book not in new_dictio_book.keys():
            export_list.append((book,count,0)) 
    print('\n')
    return export_list

def print_detail_list(list_ready):
    sorted_l = sorted(list_ready, key=itemgetter(2),reverse=True)
    for each in sorted_l:
        print("Total {0[1]} || New {0[2]} || {0[0]}".format(each))

@click.command()
@click.option('--option', type=click.Choice(['append-mode','create-mode','exit']), prompt=True, show_choices=True)
def main_options(option):
    """Options:
    append-mode: it will append only new highlights to existing files, while creating new files in the ouput folder for new books.
    create-mode: it will avoid appending to existing files, creating new files for every book to be exported (new or existing).
    exit: finish de program without making any changes.
    """
    # option = click.prompt('append-mode / create-mode', type=str)
    if option == 'append-mode':
        append_to_files(existing_dictio_book)
        create_files(new_files_list)
    elif option == 'create-mode':
        create_files(dictio_books)
    elif option == 'exit':
        pass
      
    quit()

def main():
    get_new_clippings(new_files_list)
    separate_clippings_new_old(dictio_books)
    list_to_show = counter_of_new_highlights()
    print_detail_list(list_to_show)


if __name__ == "__main__":
    main()
    main_options() # no argument because it's passed via command-line using click module





