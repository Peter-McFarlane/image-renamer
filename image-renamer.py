import os
import webbrowser
import tkinter as tk
from exif import Image
from tkinter import ttk
from pathlib import Path
from natsort import natsorted
from datetime import datetime


# ======= FUNCTIONS =======

# redirect to README.md
def callback(url):
    webbrowser.open_new_tab(url)

# clear GUI messages
def cleartext():
    error.set(" ")
    status_label.config(text=" ")
    num_renamed_label.config(text=" ")
    num_skipped_label.config(text=" ")
    root.update()

# handle path from entry
def get_path():
    pathname = entry.get()
    if os.path.exists(pathname):
        if (pathname[len(pathname) - 1] != '/'):
            pathname += '/'
        cleartext()
        run(pathname)
    else:
        error.set("Error: that is not a valid pathname")

# convert unix timestamp to proper datetime format
def unix_to_datetime(unix):
    return datetime.utcfromtimestamp(unix).strftime("%Y-%m-%d [%H∶%M∶%S]")

# rename files that do not have exif data according to created/modified time
def rename_non_jpeg(path):
    created = path.stat().st_ctime
    modified = path.stat().st_mtime

    if created <= modified:
        date_and_time = unix_to_datetime(created)
    else:
        date_and_time = unix_to_datetime(modified)

    return date_and_time

# rename the files
def run(root_dir):
    button.config(state="disabled")
    num_renamed = 0
    num_skipped = 0
    burst_i = 0 # keep burst index at 0 by default
    last = '' # previous timestamp

    # sort images by name so that burst photos don't get overwritten
    image_list = Path(root_dir).glob('*')
    image_list = natsorted(image_list, key=str)

    # main loop; runs through list of images
    for path in image_list:

        file_name, file_extension = os.path.splitext(path)

        # supported file extensions
        jpeg_extns = ['.jpg', '.jpeg']
        other_media_extns = ['.mpeg', '.wmv', '.avi', '.mov', 
                             '.mkv', '.png', '.gif', '.tiff']

        # rename non-jpeg files
        if file_extension.lower() in other_media_extns:

            # update counter and status
            num_renamed += 1
            status_label.config(text="Renaming: " + str(file_name), fg="purple")
            root.update()

            # rename non-jpeg file
            date_and_time = rename_non_jpeg(path)
            new_filename = date_and_time + file_extension
            new_filename = os.path.join(os.path.dirname(root_dir), new_filename)
            os.rename(path, new_filename)
        
        # rename jpeg images
        elif file_extension.lower() in jpeg_extns:

            img = Image(path)

            # modify date and time format to my liking
            # YYYY-mm-DD [HH∶MM∶SS]
            if img.has_exif and img.get("datetime_original") != "0000:00:00 00:00:00" and img.get("datetime_orignal") != None:

                # update counter and status
                num_renamed += 1
                status_label.config(text="Renaming: " + str(file_name), fg="purple")
                root.update()

                # format date and time
                date_list = list(img.get("datetime_original"))
                date_list[4] = '-'
                date_list[7] = '-'
                date_list[13] = "∶" # NOTE: this is not a colon, as they are not allowed to be used in
                date_list[16] = "∶" # filenames on Mac. Rather, this is a ratio symbol (U+2236)
                temp1 = date_list[0:11]
                temp1.append("[")
                temp2 = date_list[11:19]
                temp2.append("]")
                date_list = temp1 + temp2
                date_and_time = "".join(date_list)

            # if there's no/bad exif data...
            else:

                # ...just skip it and update counter and status
                num_skipped += 1
                status_label.config(text="Skipping: " + str(file_name), fg="purple")
                root.update()
                continue

            # if two or more images have the exact same timestamp...
            if date_and_time[0:20] == last[0:20]:

                # ...create filename with burst index appended to the end
                burst_i = burst_i + 1
                new_filename = date_and_time + "~" + str(burst_i) + file_extension

            # otherwise...
            else:

                # ...create filename from formatted date and time and reset burst index
                new_filename = date_and_time + file_extension
                last = date_and_time 
                burst_i = 0 
            
            # rename the image with the new filename
            new_filename = os.path.join(os.path.dirname(root_dir), new_filename)
            os.rename(path, new_filename)

    status_label.config(text="Done!", fg="green")
    num_renamed_label.config(text="Renamed " + str(num_renamed) + " files", fg="purple")
    num_skipped_label.config(text="Skipped " + str(num_skipped) + " files", fg="purple")
    button.config(state="normal")


# ======= GUI =======

root = tk.Tk()
root.title("Image Renamer")
root.geometry("700x500")

# Readme label
readme_label = tk.Label(root, text="Please read the README before running this program", font=("Tahoma"))
readme_label.pack(pady=10)

# Readme link
readme_link = tk.Label(root, text="Click here to read the README.md", font=("Tahoma"), fg="blue", cursor="hand2")
readme_link.pack(pady=10)
readme_link.bind("<Button-1>", lambda e:
callback("https://github.com/Peter-McFarlane/image-renamer/blob/main/README.md"))

# Seperator
separator = ttk.Separator(root, orient='horizontal')
separator.pack(fill='x', pady=10)

# Path label
path_label = tk.Label(root, text="Enter path where images are located:", font=("Tahoma"), anchor="w")
path_label.pack(pady=10)

# Path entry
entry = tk.Entry(root, width=50)
entry.pack(pady=10)

# Error label
error = tk.StringVar()
error_label = tk.Label(root, textvariable=error, font=("Courier"), fg="red")
error_label.pack(pady=10)

# Run button
button = tk.Button(root, text="  Run it  ", font=("Tahoma"), command=get_path, cursor="hand2")
button.pack(pady=10)

# Status label
status_label = tk.Label(root, text=" ", font=("Courier"), fg="purple")
status_label.pack(pady=10)

# Results label
num_renamed_label = tk.Label(root, text=" ", font=("Courier"), fg="purple", anchor="w")
num_skipped_label = tk.Label(root, text=" ", font=("Courier"), fg="purple", anchor="w")
num_renamed_label.pack(pady=5)
num_skipped_label.pack(pady=5)

# Run the GUI
root.mainloop()
