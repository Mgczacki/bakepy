import os
import mimetypes
import requests

from pathlib import Path
from urllib.parse import urlparse

def as_list(i):
    if issubclass(type(i), str) or not isinstance(i, list):
        return [i]
    return i

def get_filename(filepath, extension):
    filepath = Path(filepath)
    if filepath.suffix != f".{extension}":
        return filepath / f".{extension}"
    return filepath

def get_valid_list_idx(original_idx, lst, listname = "list"):        
    idx = original_idx

    try:
        if idx < 0:
            idx = idx + len(lst)
    except:
        raise Exception("Invalid list index provided.")

    if idx >= len(lst) or idx < 0:
        raise Exception(f"Element at index {original_idx} of {listname} does not exist.")

    return idx

def limit_list_insert_idx(idx, lst, overwrite = False):
    delta = 0
    if overwrite:
        delta = 1
    lst_len = len(lst) - delta
    if idx is None:
        idx = lst_len
        
    if idx > lst_len:
        idx = lst_len

    if idx < -lst_len:
        idx = 0
        
    return idx

def check_is_url(s):
    try:
        result = urlparse(s)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_image_data(path):
    #Get image type
    img_type = mimetypes.guess_type(path)[0]

    #Handle remote images.
    if check_is_url(path):
        img_data = requests.get(path).content
    else:
        with open(path, "rb") as file:
            img_data = file.read()

    return img_type, img_data

class Working_Directory():
    def __init__(self, dirpath):
        self.dirpath = dirpath
        self.prevpath = Path.cwd()
    def __enter__(self):
        os.chdir(self.dirpath)
        return self.dirpath
    def __exit__(self, type, value, traceback):
        os.chdir(self.prevpath)