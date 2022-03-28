import argparse
import codecs
import dateparser
import datetime
import re
import yaml

from collections import Counter
from pathlib import Path
from rich.console import Console
from rich.table import Table


today = datetime.datetime.now().strftime("%Y-%m-%d")


def setArgumentParser():
    """Setting the argument parser"""
    parser = argparse.ArgumentParser(description="Process Kindle Clippings.",formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('mode', choices=['append','create','show-list'], help="""
    Which mode should we use? (append|create|show-list):
        append: look for existing files and only add highlights that were not previously stored. If the file doesn't exist, create a new one in the output folder.
        create: create new files for every book in the output folder.
        show-list: it won't create nor modify any file, just display the overview of generated highlights.
    -------------------------------
    NOTE: Every time a file is create, it will overwrite any existing file in the output folder with the same name.
    """)
    parser.add_argument('--filter-date', action='store_true', help='Only look for new clippings, based on the date store in the YAML (last clipping exported in a previous run)')
    return parser.parse_args()


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


class Book:

    exported_books = []

    def __init__(self, title):
        """Iniatiate new book object."""
        self.title = title
        self.clippings = []
        self.clippings_counter = Counter()
        Book.exported_books.append(self)


    def getBookIndex(target):
        """
        Search if a Book with the desired title was previously created.
        Returns the index where it is store. Otherwise, return -1.
        """
        for index, book in enumerate(Book.exported_books):
            if book.title == target:
                return index
        return -1


    def getBookObjectByIndex(index):
        """
        Search for a specific Book already stored by it's index.
        Returns a reference to the object.
        """
        book = None if index == -1 else Book.exported_books[index]
        return book


    def getBookObjectByTitle(title):
        """
        Search for a specific Book by it's title.
        Returns a reference to the object.
        """
        index = Book.getBookIndex(title)
        return Book.getBookObjectByIndex(index)


    def process_clippings(input_list: list, last_exported_date: datetime.datetime, filter_date=False):
        """Process each exported clipping from the list, and organize them in different Book objects.
        Returns the date of the last clipping made (to be stored in the YAML).
        """
        for title, date_str, _, clipping, _ in input_list:
            date = get_date(date_str)
            append_clipping = False
            title = re.sub(r'[^A-Za-zÀ-ÿ0-9-()\s]','',title)      # Remove special characters from book's name

            if date > last_exported_date:
                last_exported_date = date
                append_clipping = True

            if not filter_date:
                append_clipping = True

            if append_clipping == True:
                book = Book.getBookObjectByTitle(title)
                if not book:
                    book = Book(title)
                if clipping:
                    book.clippings.append(clipping)
                    book.clippings_counter['exported'] += 1
        
        return last_exported_date


    def establish_new_path(self, output_folder_path: Path):
        """Create path for a new file."""
        self.new_path = output_folder_path.joinpath(self.title+".txt")

    def establish_existing_path(self, list_books_stored: list):
        """Check if a file already exists and set also it's path."""
        path_file = [path for path in list_books_stored if path.stem == self.title]
        self.existing_path = Path(path_file[0]) if path_file else None


    def save_to_new_file(self, log_file: Path):
        """Export function for creating a new file in the ouput folder."""
        if self.clippings:
            with codecs.open(self.new_path,'w+','utf_8') as f:
                f.write(str(self.title))
                f.write(str('\r\n\r\n\r\n'))
                f.write('\r\n\r\n'.join(self.clippings))

            with codecs.open(log_file, 'a', 'utf-8') as log:
                exported_count = self.clippings_counter['exported']
                log_txt = f'[{today}] | New TXT File | Added {exported_count:.0f} to: {self.new_path.stem} \n'
                log.write(log_txt)
                print(log_txt)


    def save_to_existing_file(self, log_file: Path):
        """Export function for appending new highlights to an existing file.""" 
        if self.new_clippings:
            with codecs.open(self.existing_path, 'a', 'utf-8') as f:
                f.write(str('\r\n\r\n'))            
                f.write('\r\n\r\n'.join(self.new_clippings)) 

            with codecs.open(log_file, 'a', 'utf-8') as log:
                exported_count = self.clippings_counter['new']              
                log_txt = f'[{today}] | Existing TXT File | Added {exported_count:.0f} to: {self.existing_path.stem} \n'
                log.write(log_txt)
                print(log_txt)


    def separate_existing_clippings(self):
        """Separate the clippings already stored from the new ones."""
        
        self.new_clippings = []
        self.existing_clippings = []

        if self.existing_path:
            with codecs.open(self.existing_path, 'r', 'utf-8') as f:
                txt_stored = f.read()
                
            for clipping in self.clippings:         
                if clipping not in str(txt_stored):   # Check if the new highlights are not already stored in the existing file.
                    self.new_clippings.append(clipping)
                    self.clippings_counter['new'] += 1
                else:
                    self.existing_clippings.append(clipping)
                    self.clippings_counter['existing'] += 1
        else:
            self.clippings_counter['new'] = self.clippings_counter['exported']


    def render_table(mode):
        """Create and render a table with an overview of all the data."""
        table = Table(title="Kindle Clippings")

        table.add_column("Title", justify="left", header_style="bold", style="yellow", no_wrap=True)
        if mode == 'append' or mode == 'show-list':
            table.add_column("Existing", justify="right", header_style="bold")
            table.add_column("New", justify="right", header_style="bold")
        table.add_column("Total", justify="right", header_style="bold")

        for book in Book.exported_books:
            if mode == 'append' or mode == 'show-list':
                table.add_row(
                    book.title, 
                    str(book.clippings_counter['existing']),
                    str(book.clippings_counter['new']),
                    str(book.clippings_counter['exported'])
                )
            else:
                table.add_row(
                    book.title, 
                    str(book.clippings_counter['exported'])
                )

        console = Console()
        console.print(table)
