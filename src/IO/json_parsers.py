import json
import os

import jsonpickle

from IO.paths import saves_dir

sort_keys = True
indent = 1
jsonpickle.set_encoder_options('simplejson', sort_keys, indent)


def remove_comments(s):
    """
    Parameters:
        s (str) : The string to remove comments from
        
    Returns:
        a string that is s but with all the comments of the form //, /**/, and # removed
    """
    in_comment_single = False
    in_comment_multi = False
    in_string = False

    to_return = []
    length = len(s)

    i = 0
    from_index = 0
    while i < length:
        c = s[i]

        if not in_comment_multi and not in_comment_single:
            if c == '"':
                slashes = 0
                for j in range(i - 1, 0, -1):
                    if s[j] != '\\':
                        break

                    slashes += 1

                if slashes % 2 == 0:
                    in_string = not in_string

            elif not in_string:
                if c == '#':
                    in_comment_single = True
                    to_return.append(s[from_index:i])
                elif c == '/' and i + 1 < length:
                    cn = s[i + 1]
                    if cn == '/':
                        in_comment_single = True
                        to_return.append(s[from_index:i])
                        i += 1
                    elif cn == '*':
                        in_comment_multi = True
                        to_return.append(s[from_index:i])
                        i += 1

        elif in_comment_single and (c == '\n' or c == '\r'):
            in_comment_single = False
            from_index = i

        elif in_comment_multi and c == '*' and i + 1 < length and s[i + 1] == '/':
            in_comment_multi = False
            i += 1
            from_index = i + 1

        i += 1

    if not in_comment_single and not in_comment_multi:
        to_return.append(s[from_index:len(s)])

    return "".join(to_return)


def load_json(path, pickle, encoding='utf8', ignore_comments=True):
    """
    Parameters:
        path (str) : A path pointing to the json file or directory of json files to load
    
    Returns:
        a dictionary containing all json data at the path and its subdirectories with json files at path,
        or None if no such files are found. Comments in json files are not included.
    """
    if ".json" in path:
        with open(path, encoding=encoding) as file:
            data = remove_comments(file.read()) if ignore_comments else file.read()
            return jsonpickle.decode(data) if pickle else json.loads(data, encoding=encoding)
    else:
        to_return = dict()
        for file_name in os.listdir(path):
            file_path = path + "/" + file_name
            if os.path.isdir(file_path):
                dir_dict = load_json(file_path, pickle=pickle)
                if dir_dict is not None:
                    to_return[file_name] = dir_dict
            elif ".json" in file_path:
                to_return[file_name[:-5]] = load_json(file_path, encoding=encoding, pickle=pickle)
        if len(to_return) == 0:
            return None
        return to_return


def save_json(to_save, path, pickle, encoding='utf8'):
    """Saves the to_save dictionary to a json file if the path is a json file,
      or if the path is a directory, saves each top-level dictionary value to a 
      json file with the name of the key. Untested and cannot save multiple
      folders because it can only tell whether a file is meant to be json or folder
      from the path. Will throw an error when trying t    o overwrite a #READONLY file.
      Note that for frequent saving picklers are preferred, json is used when 
      human-readability is prioritized over ease of saving. In practice this means
      persistent settings are json, often read-only, and game-specific data is pickled. """
    if ".json" in path:
        _write_if_not_readonly(to_save, path, pickle, encoding=encoding)
    else:
        for file_name, data in to_save:
            save_json(data, path + "/" + file_name + ".json", pickle=pickle)


def _write_if_not_readonly(to_save, path, pickle, encoding='utf8'):
    if os.path.isfile(path):
        with open(path, 'r') as file:
            if file.readline().strip() == "@READONLY":
                raise RuntimeError("Tried to write to the following read-only file: " + path)
    with open(path, 'w') as file:
        to_write = jsonpickle.encode(to_save) if pickle \
            else json.dumps(to_save, sort_keys=sort_keys, allow_nan=False, indent=indent, separators=(",", ":"),
                            encoding=encoding)
        file.write(to_write)


def save_game(to_save, save_name='1', pickle=True, encoding='utf8'):
    path = saves_dir + save_name + ".save"
    save_json(to_save, path, pickle, encoding=encoding)


def load_game(save_name='1', pickle=True, encoding='utf8'):
    path = saves_dir + save_name + ".save"
    return load_json(path, pickle, encoding=encoding)


def delete_game(save_name='1', pickle=True):
    path = saves_dir + save_name + ".save"
    if not os.path.isfile(path) and not os.path.isdir(path):
        raise FileNotFoundError
    os.remove(path)
