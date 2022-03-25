import argparse
import datetime
import yaml

from pathlib import Path

from src.tools import store_date, get_new_clippings_list, append_to_files, create_files, get_clippings_dictio, separate_clippings_new_old, counter_of_new_highlights, print_detail_list

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
if not last_exported_date:
    last_exported_date = datetime.datetime(2000,1,1)           # Needed and empty datetime object to start with


#### CLI arguments ###

parser = argparse.ArgumentParser(description="Process Kindle Clippings.")
parser.add_argument('mode', choices=['append','create','show-list'], help="Which mode should we use? (append|create|show-list")
parser.add_argument('--filter-date', action='store_true', help='Only look for new clippings, based on the date store in the YAML (last clipping exported in a previous run)')
args = parser.parse_args()


def main_options(option):
    """Options:
    append: it will append only new highlights to existing files, while creating new files in the ouput folder for new books.
    create: it will avoid appending to existing files, creating new files for every book to be exported (new or existing).
    """
    # option = click.prompt('append-mode / create-mode', type=str)
    if option == 'append':
        append_to_files(existing_files_dict, list_books_stored, log_file)
        create_files(new_files_dict)
        store_date(last_exported_date, config_file_path, paths_yaml)
    elif option == 'create':
        create_files(full_dict, output_folder_path, log_file)
        store_date(last_exported_date, config_file_path, paths_yaml)
    else:
        print('Nothing was exported.')
        pass
      
    quit()

if __name__ == "__main__":
    full_list = get_new_clippings_list(clippings_txt)
    full_dict, all_highlights_counter = get_clippings_dictio(full_list, last_exported_date, args.filter_date)
    new_files_dict, existing_files_dict, highlight_counter = separate_clippings_new_old(full_dict, list_books_stored)
    list_to_show = counter_of_new_highlights(new_files_dict, existing_files_dict, all_highlights_counter)
    print_detail_list(list_to_show)
    main_options(args.mode)





