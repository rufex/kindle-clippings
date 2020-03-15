### Kindle Clippings Organizer
> Python Script for extracting notes taken in a Kindle and organize them in a separate .txt file for each book or article.

In this directory, there are two variants covering the same idea:

## "Kindle Highlights.py" 
Originaly developed for Kindle Version 4 in Spanish, and afterwards adapted for Kindle Version 10 (also in Spanish). So, it may not work for other Kindle versions or languages and would requiere some small adjustments.

# Changelog:
v1 --> Code was rewritten from scratch, with to goal to make it more flexible and work in more scenarios (languages and device versions). 

# How-to use it:
You would nead two folders called "input_files" and "output_files" in the same directory as the py file. Copy your txt file with the clippings from your Kindle device (generally called "My Clippings.txt" into a folder named "input_files". Run the script, and you would get, saved in the "output_files" folder, one txt file for each book/article.

## "Kindle Highlights append mode.py"
It a variant originated from the previous script. In this case, instead of creating a new file for every book. It first checks in your collection of previously generated files if there is already a file corresponding to the book to be exported, and only append to them the new ones.

# To-Do:
- Create a Virtual Enviroment and a requeriments.txt
- Add command-line interaction:
    - run script
    - show list of new files and files to be appendend.
    - Confirm/Refuse:
        - Append existing ones and create new files.
        - Refuse append. Create files for everyone.
        - Refuse all.
        
click options: --run --append-mode --create-mode --end


