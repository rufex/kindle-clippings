import codecs
import dateparser
import datetime
import re
import yaml

from collections import defaultdict, Counter
from operator import itemgetter
from pathlib import Path
from terminaltables import AsciiTable

today = datetime.datetime.now().strftime("%Y-%m-%d")
global highlight_counter


def get_date(input: str) -> datetime.datetime:
    """Get a datetime object from the date stored together with the kindle clippings.
    Parameter
    ---------
    input: str
        Has the following structure: "- {text} | {text}, 1 of January of 2019 23:13:08"
    """
    try:
        date_str = input.split(', ')[1]
        return dateparser.parse(date_str)

    except Exception:
        print("Date was not identified.")
        return None


def store_date(date: datetime.datetime, file_path: Path, info: dict) -> None:
    """Store the date established as the last highlight exported in the YAML file."""
    try:
        if date > info["Paths"]["last_date"]:
            info["Paths"]["last_date"] = date

            with open(file_path, 'w') as f:
                yaml.dump(info, f)
            print(F"New date store in YAML: {date}")
            
    except Exception:
        print("Date was not stored in the YAML file.")
        pass


def get_new_clippings_list(input_file: Path) -> list:
    """Open clippings txt file and creates a list with all the books and their highlights."""
    with codecs.open(input_file, 'r', 'utf-8') as f:          # Open file of clippings. Read mode
        txt = f.readlines()                                   # List with all the lines from the input txt file
        txt = [item.replace('\ufeff','') for item in txt]     # Codification at the begining of the txt file
        txt = [item.replace('\n','') for item in txt]            
        txt = [item.replace('\r','') for item in txt]
                            
    list_of_highlights = [i for i in zip(*[iter(txt)]*5)] # Result: list of tuples => [ (Title 1, Date 1, not-relevant, Highlight 1, not-relevant), (...)]
    return list_of_highlights


def get_clippings_dictio(input_list: list, last_exported_date: datetime.datetime, check_date=False):
    """Get a list of clippings and order them in a DefaultDict.
    Parameters
    ----------
    input_list: list
    last_exported_date
    check_date: boolean (default = False)    
        if true, it will only consider highlights that are after the date stored in the config file (date from the last export run)
    """
    dictio_books = defaultdict(list)                          # DefaultDic = {key: [values]}
    highlight_counter_full = Counter()
    
    for title, date_str, _ , highlight, _  in input_list:
        date = get_date(date_str)
        if check_date:
            if date > last_exported_date:                         # Only append newer clippings
                append_clipping = True
                last_exported_date = date                      # Store the last date to be exported to the YAML file
            else:
                append_clipping = False
        else:
            append_clipping = True

        if append_clipping == True:
            title = re.sub(r'[^A-Za-zÀ-ÿ0-9-()\s]','',title)      # Remove special characters from book's name     
            dictio_books[title].append('* ' + highlight)          # DefaultDic: {Title:[Highlights]}
            highlight_counter_full[title] += 1
    
    return dictio_books, highlight_counter_full, last_exported_date


def separate_clippings_new_old(dictio: dict, list_books_stored: list):
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


def append_to_files(dictio: dict, list_books_stored: list, log_file: Path, highlight_counter):
    """Export function for appending new highlights to existing files."""
    for book, highlights in dictio.items():
        path_file = [path for path in list_books_stored if path.stem == book]
        path_file = Path(path_file[0]) 
    
        with codecs.open(path_file, 'a', 'utf-8') as f:   # Open existing file. Append mode.
            f.write(str('\r\n\r\n'))            
            f.write('\r\n\r\n'.join(highlights)) 

        with codecs.open(log_file, 'a', 'utf-8') as log:              # Open log-file. Append mode.
            log_txt = f'[{today}] Added {highlight_counter[book]:.0f} to existing file: {path_file.stem} \n'
            log.write(log_txt)
            print(log_txt)


def create_files(dictio: dict, output_folder_path: Path, log_file: Path, highlight_counter):
    """Export function for creating new files in the ouput folder."""
    for book, highlights in dictio.items():
        path_file = output_folder_path.joinpath(book+".txt")  # Asign Book's Title as file name 
        with codecs.open(path_file,'w+','utf_8') as f:    # New file. Write mode.
            f.write(str(book))                            # Write Book's Title in txt file
            f.write(str('\r\n\r\n\r\n'))                  # Add spaces between title and highlights
            f.write('\r\n\r\n'.join(highlights))          # Write Highlights in txt file, with whitespaces between them

        with codecs.open(log_file, 'a', 'utf-8') as log:              # Open log-file. Append mode.
            log_txt = f'[{today}] New TXT File. Added {highlight_counter[book]:.0f} to new file: {path_file.stem} \n'
            log.write(log_txt)
            print(log_txt)


def counter_of_new_highlights(new_dictio_book, existing_dictio_book, highlight_counter_full, highlight_counter):
    """Make a list of books with their counts of total and new highlights.
    Format: ['Book/Article Name', 'File Exists/Doesn't Exists', Total, New]
    """
    export_list = list()
    for book, total_count in highlight_counter_full.items():
        if len(book) > 70:
            book = book[:67]+'...'
        if book in existing_dictio_book.keys():
            export_list.append((book,'Yes', total_count-highlight_counter[book], highlight_counter[book], total_count))
        elif book in new_dictio_book.keys():
            export_list.append((book,'No', 0, highlight_counter_full[book], total_count))
        elif book not in existing_dictio_book.keys() and book not in new_dictio_book.keys():
            export_list.append((book,'Yes', total_count, 0, total_count)) 
    return export_list


def print_detail_list(list_ready):
    """Print the count list in a formatted ASCII table"""
    sorted_l = sorted(list_ready, key=itemgetter(1),reverse=True)
    table_data = []
    table_data.append(['Book/Article', 'File already exists?', 'Existing (stored)','New (not stored yet)', 'Total exported (now)'])
    for each in sorted_l:
        table_data.append(each)
    table = AsciiTable(table_data)
    table.title = 'Highlights overview'
    print('')
    print(table.table)
