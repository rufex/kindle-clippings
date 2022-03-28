import datetime
import sys
import yaml

from pathlib import Path

from src.tools import Book, setArgumentParser, store_date, get_new_clippings_list


if __name__ == "__main__":

    # Paths & Files
    current_folder = Path(__file__).parent
    config_file_path = Path.joinpath(current_folder,"config_kindle_highlights.yml")

    with open(config_file_path, 'r') as f:
        paths_yaml = yaml.safe_load(f)

    bookshelf_path = Path(paths_yaml["Paths"]["bookshelf"])        # Directory where previous TXT files are stored
    list_books_stored = list(bookshelf_path.rglob('*.txt'))        # List of all TXT already stored

    clippings_txt = Path(paths_yaml["Paths"]["clippings_file"]) # Path of the TXT file
    output_folder_path = Path(paths_yaml["Paths"]["output_folder"])
    log_file = Path(paths_yaml["Paths"]["log_file"])
                        
    last_exported_date = paths_yaml["Paths"]["last_date"] or datetime.datetime(2000,1,1)     # To get a datetime object (and use it to compare)

    # CLI arguments 
    args = setArgumentParser()

    # Get list of annotations from the txt
    raw_clippings = get_new_clippings_list(clippings_txt)

    # Process each annotation and classify them in different
    last_exported_date = Book.process_clippings(raw_clippings, last_exported_date, args.filter_date)

    # Append / Create
    if args.mode == 'append':
        for book in Book.exported_books:
            book.establish_existing_path(list_books_stored)
            book.separate_existing_clippings()
            if book.existing_path:
                book.save_to_existing_file(log_file)
            else:
                book.establish_new_path(output_folder_path)
                book.save_to_new_file(log_file)
        store_date(last_exported_date, config_file_path, paths_yaml)
    elif args.mode == 'create':
        for book in Book.exported_books:
            book.establish_new_path(output_folder_path)
            book.save_to_new_file(log_file)
        store_date(last_exported_date, config_file_path, paths_yaml)
    else:
        for book in Book.exported_books:
            book.establish_existing_path(list_books_stored)
            book.separate_existing_clippings()
        print('Nothing has been saved.')

    # Table
    Book.render_table(args.mode)

    # Exit
    sys.exit('End program.')
