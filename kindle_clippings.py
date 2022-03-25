import codecs
import re
import datetime
import yaml
import dateparser
import argparse

from collections import defaultdict, Counter
from pathlib import Path
from operator import itemgetter
from terminaltables import AsciiTable

from src.tools import get_date, store_date

### Paths & Files ### 

current_folder = Path(__file__).parent
config_file_path = Path.joinpath(current_folder,"config_kindle_highlights.yml")

with open(config_file_path, 'r') as f:
    paths_yaml = yaml.safe_load(f)

bookshelf = Path(paths_yaml["Paths"]["bookshelf"])        # Directory where previous TXT files are stored
list_books_stored = list(bookshelf.rglob('*.txt'))        # List of all TXT already stored

clippings_txt = Path(paths_yaml["Paths"]["clippings_file"]) # Path of the TXT file
output_folder_path = Path(paths_yaml["Paths"]["output_folder"])
log_file = Path(paths_yaml["Paths"]["log_file"])
                    

last_exported_date = paths_yaml["Paths"]["last_date"]     # To get a datetime object (and use it to compare)
today = datetime.datetime.now().strftime("%Y-%m-%d")
current_last_date = datetime.datetime(2000,1,1)           # Needed and empty datetime object to start with


#### CLI arguments ###

parser = argparse.ArgumentParser(description="Process Kindle Clippings.")
parser.add_argument('mode', choices=['append','create','show-list'], help="Which mode should we use? (append|create|show-list")
parser.add_argument('--filter-date', action='store_true', help='Only look for new clippings, based on the date store in the YAML (last clipping exported in a previous run)')
args = parser.parse_args()


def get_new_clippings_list(input_file):
    """Open txt file in the input folder and creates a list with all the books and their highlights."""
    with codecs.open(input_file, 'r', 'utf-8') as f:              # Open file of clippings. Read mode
        txt = f.readlines()                                      # List with all the lines from the input txt file
        txt = [item.replace('\ufeff','') for item in txt]        # Codification at the begining of the txt file
        txt = [item.replace('\n','') for item in txt]            
        txt = [item.replace('\r','') for item in txt]
                            
        #list_of_highlights = [txt[i: i + 5:3] for i in range(0, len(txt), 5) if txt[i+3] != ""]  # Result => [[Title 1, Highlight 1],[Title 2, Highlight 2]]...
        list_of_highlights = [i for i in zip(*[iter(txt)]*5)]     # Result => [ (Title 1, Date 1, not-relevant, Highlight 1, not-relevant), (...)]
        return list_of_highlights


def get_clippings_dictio(input_list, check_date=True):
    """Get a list of clippings and order them in a DefaultDict.
    Parameters
    ----------
    input_list: list
    check_date: boolean (default = true)    
        if true, it will only consider highlights that are after the date stored in the config file (date from the last export run)
    """
    dictio_books = defaultdict(list)                          # DefaultDic = {key: [values]}
    highlight_counter_full = Counter()
    global current_last_date

    for title, date_str, _ , highlight, _  in input_list:
        date = get_date(date_str)
        if check_date:
            if date > last_exported_date:                         # Only append newer clippings
                append_clipping = True
                if date > current_last_date:
                    current_last_date = date                      # Store the last date to be exported to the YAML file
            else:
                append_clipping = False
        else:
            append_clipping = True

        if append_clipping == True:
            title = re.sub(r'[^A-Za-zÀ-ÿ0-9-()\s]','',title)      # Remove special characters from book's name     
            dictio_books[title].append('* ' + highlight)          # DefaultDic: {Title:[Highlights]}
            highlight_counter_full[title] += 1
    
    return dictio_books, highlight_counter_full


def separate_clippings_new_old(dictio):
    """Separates the books that already have a file created.
    For those which already a file exists, filtrates only the new highlights.
    Keeps a count of the highlights that could be written to each file.
    """
    new_dictio_book = defaultdict(list)                       # DefaultDic for books that don't have previous file
    existing_dictio_book = defaultdict(list)                  # DefaultDic for books that have previous file
    highlight_counter = Counter()                             # To keep the count of amount of Highlights for each book.
    
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

    return new_dictio_book, existing_dictio_book, highlight_counter


def append_to_files(dictio):
    """Export function for appending new highlights to existing files."""
    for book, highlights in dictio.items():
        path_file = [path for path in list_books_stored if path.stem == book]
        path_file = Path(path_file[0]) 
    
        with codecs.open(path_file, 'a', 'utf-8') as f:   # Open existing file. Append mode.
            f.write(str('\r\n\r\n'))            
            f.write('\r\n\r\n'.join(highlights)) 

        with codecs.open(log_file, 'a', 'utf-8') as log:              # Open log-file. Append mode.
            log_txt = f'[{today}] Added {highlight_counter[book]:.0f} to {path_file.stem} \n'
            log.write(log_txt)
            print(log_txt)


def create_files(dictio):
    """Export function for creating new files in the ouput folder."""
    for book, highlights in dictio.items():
        path_file = output_folder_path.joinpath(book+".txt")  # Asign Book's Title as file name 
        with codecs.open(path_file,'w+','utf_8') as f:    # New file. Write mode.
            f.write(str(book))                            # Write Book's Title in txt file
            f.write(str('\r\n\r\n\r\n'))                  # Add spaces between title and highlights
            f.write('\r\n\r\n'.join(highlights))          # Write Highlights in txt file, with whitespaces between them

        with codecs.open(log_file, 'a', 'utf-8') as log:              # Open log-file. Append mode.
            log_txt = f'[{today}] New TXT File. Added {highlight_counter[book]:.0f} to {path_file.stem} \n'
            log.write(log_txt)
            print(log_txt)


def counter_of_new_highlights(new_dictio_book, existing_dictio_book, highlight_counter_full):
    """Make a list of books with their counts of total and new highlights.
    Format: ['Book/Article Name', 'File Exists/Doesn't Exists', Total, New]
    """

    export_list = list()
    for book, count in highlight_counter_full.items():
        if len(book) > 70:
            book = book[:67]+'...'
        if book in existing_dictio_book.keys():
            export_list.append((book,'Yes', count,highlight_counter[book]))
        elif book in new_dictio_book.keys():
            export_list.append((book,'No', count,highlight_counter_full[book]))
        elif book not in existing_dictio_book.keys() and book not in new_dictio_book.keys():
            export_list.append((book,'Yes', count,0)) 
    return export_list


def print_detail_list(list_ready):
    """Print the count list in a formatted ASCII table"""
    sorted_l = sorted(list_ready, key=itemgetter(1),reverse=True)
    table_data = []
    table_data.append(['Book/Article', 'File already exists?','Total exported (now)','New (not stored yet)'])
    for each in sorted_l:
        table_data.append(each)
    table = AsciiTable(table_data)
    table.title = 'Highlights overview'
    print('')
    print(table.table)


def main_options(option):
    """Options:
    append: it will append only new highlights to existing files, while creating new files in the ouput folder for new books.
    create: it will avoid appending to existing files, creating new files for every book to be exported (new or existing).
    """
    # option = click.prompt('append-mode / create-mode', type=str)
    if option == 'append':
        append_to_files(existing_files_dict)
        create_files(new_files_dict)
        store_date(current_last_date, config_file_path, paths_yaml)
    elif option == 'create':
        create_files(full_dict)
        store_date(current_last_date, config_file_path, paths_yaml)
    else:
        print('Nothing was exported.')
        pass
      
    quit()

if __name__ == "__main__":
    full_list = get_new_clippings_list(clippings_txt)
    full_dict, all_highlights_counter = get_clippings_dictio(full_list, args.filter_date)
    new_files_dict, existing_files_dict, highlight_counter = separate_clippings_new_old(full_dict)
    list_to_show = counter_of_new_highlights(new_files_dict, existing_files_dict, all_highlights_counter)
    print_detail_list(list_to_show)
    main_options(args.mode)





