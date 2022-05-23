# Kindle Clippings Organizer

>Python Script for extracting notes taken in a Kindle and organize them in a separate .txt files for each book or article.

First checks in your collection of previously generated files if there is already a file corresponding to the book to be exported, and only append to them the new ones.


### Setting it up

1. Install the needed dependencies
1. Create a YAML file called "config_kindle_highlights.yml", with the following structure:

```YAML
Paths:
  bookshelf: { absolute path to the directory where you are storing your generated TXTs }
  clippings_file: { absolute path to the txt where the clippings are stored by your Kindle }
  output_folder: { absolute path to a directory where you want to store your new TXTs }
  log_file: { absolute path to your log file }
  last_date: 2000-01-01 
```

### How to use it

1. Make sure your YAML contains all the needed information.
1. Run your script from the your terminal, passing the needed arguments.

```python
python kindle_clippings.py [-h] [--filter-date] {append,create,show-list}
```

- `mode` (required) 
  - `append`: look for existing files and only add highlights that were not previously stored. If the file doesn't exist, create a new one in the output folder.
  - `create`: create new files for every book in the output folder.
  - `show-list`: it won't create nor modify any file, just display the overview of generated highlights.
- `filter-date` (optional): Only look for new clippings, based on the date store in the YAML (last clipping exported in a previous run)
