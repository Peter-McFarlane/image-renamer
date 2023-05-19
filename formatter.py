# format filename from EXIF data
# YYYY-MM-DD  HH'mm'SS

# INSTRUCTIONS:
# 1. place this file into the directory where your photos are located
# 2. copy the directory and paste it into line 19 of this program
# 3. run the program
# 4. sometimes the program will get stuck on a file;
#    if you get a "no such file or directory error",
#    simply run the program again and it should unstuck itself

import os
import pathlib
from exif import Image

burst_i = 0 # set burst index to 0
last = ''

root_dir = '.' # <-- input root directory here
for path in pathlib.Path(root_dir).iterdir():
    info = path.stat()

    # skip unsupported filetypes
    file_name, file_extension = os.path.splitext(path)
    supported = ['.jpg', '.tif', '.wav', '.png', '.webp']
    if file_extension not in supported:
        continue

    # modify date format to my liking
    # YYYY-MM-DD  HH;mm;SS
    img = Image(path)
    print("Renaming file: ", file_name)
    
    if img.has_exif:
        date_list = list(img.get("datetime_original"))
        date_list[4] = '-'
        date_list[7] = '-'
        date_list[13] = "'"
        date_list[16] = "'"
        temp1 = date_list[0:11]
        temp1.append(" ")
        temp2 = date_list[11:19]
        date_list = temp1 + temp2
        date_and_time = "".join(date_list)
    else:
        continue

    # if two or more images have the same timestamp,
    # we need to append the burst index to the end
    if date_and_time[0:20] == last[0:20]:
        burst_i = burst_i + 1
        new_filename = date_and_time + "__" + str(burst_i) + file_extension
        os.rename(path, new_filename)
    else:
        new_filename = date_and_time + file_extension
        os.rename(path, new_filename)
        last = date_and_time # keep track of the last date/time
        burst_i = 0 # reset the burst index

    # NOTE: for burst photos, must manually append '__0' to first image for continuity