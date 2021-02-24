# Kindle Clippings Organizer

>Python Script for extracting notes taken in a Kindle and organize them in a separate .txt files for each book or article.

In this directory, there are two variants covering the same idea:

---

## "Kindle Highlights.py"

Originaly developed for Kindle Version 4 in Spanish, and afterwards adapted to Kindle Version 10 (also in Spanish). So, it may not work for other Kindle versions or languages and could requiere some small adjustments.

### Changelog

v1 --> Code was rewritten from scratch, with to goal to make it more flexible and work in more scenarios (languages and device versions).

### How-to use it

1. You will nead two folders called "input_files" and "output_files" in the same directory as the py file.
1. Copy your txt file with the clippings from your Kindle device (generally called "My Clippings.txt" into the folder named "input_files".
1. Run the script from the terminal. You should get, saved in the "output_files" folder, one txt file for each book/article.

---

## "Kindle Clippings.py"

It a variant originated from the previous script. In this case, instead of creating a new file for every book. It first checks in your collection of previously generated files if there is already a file corresponding to the book to be exported, and only append to them the new ones.

### How to use it

You will need a YAML file called "config_kindle_highlights.yml", with the following structure:

```
Paths:
  bookshelf: { full path to directory where you are storing your generated TXTs }
  input_folder: { relative folder path }
  output_folder: { relative folder path }
  log_file: { relative log file path }
  last_date: { datetime object } 
```

1. Place your TXT exported from your Kindle in the input folder.
1. Run your script from the your terminal.
1. Choose if you want to filter the highlights based on the previous run of the script you made or not.
1. You will see an overview of all the files that can be generated.
1. Enter one option to proceed. 'Append-mode' will append the text to the existing file if there is one, otherwise it will create a new one. 'Create-mode' will create a new txt file for each book, independently if you already have one created or not. 'Exit' to end the script without generating any changes or new files.

### Changelog

v1 --> Code refactored. Most importantly, added the possibility to keep track of the date of the last highlight exported. That way, we can use it next time to filter which highlights needs to be consider or not from the original 'My clippings' file.
