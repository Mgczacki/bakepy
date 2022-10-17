from urllib.parse import urlparse

def as_list(i):
    if issubclass(type(i), str) or not isinstance(i, list):
        return [i]
    return i

def get_filename(filepath, extension):
    if not filepath.endswith(f".{extension}"):
        return filepath+f".{extension}"
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
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except:
        return False