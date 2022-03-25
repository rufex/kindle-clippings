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
1. Run your script from the your terminal.
1. Choose if you want to filter the highlights based on the previous run of the script you made or not.
1. You will see an overview of all the files that can be generated.
1. Enter one option to proceed. 'Append-mode' will append the text to the existing file if there is one, otherwise it will create a new one. 'Create-mode' will create a new txt file for each book, independently if you already have one created or not. 'Exit' to end the script without generating any changes or new files.