import os

import json
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
    inCommentSingle = False
    inCommentMulti = False
    inString = False

    toReturn = []
    l = len(s)

    i = 0
    fromIndex = 0
    while i < l:
        c = s[i]

        if not inCommentMulti and not inCommentSingle:
            if c == '"':
                slashes = 0
                for j in range(i - 1, 0, -1):
                    if s[j] != '\\':
                        break

                    slashes += 1

                if slashes % 2 == 0:
                    inString = not inString

            elif not inString:
                if c == '#':
                    inCommentSingle = True
                    toReturn.append(s[fromIndex:i])
                elif c == '/' and i + 1 < l:
                    cn = s[i + 1]
                    if cn == '/':
                        inCommentSingle = True
                        toReturn.append(s[fromIndex:i])
                        i += 1
                    elif cn == '*':
                        inCommentMulti = True
                        toReturn.append(s[fromIndex:i])
                        i += 1

        elif inCommentSingle and (c == '\n' or c == '\r'):
            inCommentSingle = False
            fromIndex = i

        elif inCommentMulti and c == '*' and i + 1 < l and s[i + 1] == '/':
            inCommentMulti = False
            i += 1
            fromIndex = i + 1

        i += 1

    if not inCommentSingle and not inCommentMulti:
        toReturn.append(s[fromIndex:len(s)])

    return "".join(toReturn)


def load_json(path, pickle, encoding = 'utf8', ignore_comments = True):
    """
    Parameters:
        path (str) : A path pointing to the json file or directory of json files to load
    
    Returns:
        a dictionary containing all json data at the path and its subdirectories with json files at path,
        or None if no such files are found. Comments in json files are not included.
    """
    if(".json" in path):
        with open(path, encoding = encoding) as file:
            data = remove_comments(file.read()) if ignore_comments else file.read()
            return jsonpickle.decode(data) if pickle else json.loads(data, encoding = encoding)
    else:
        toReturn = dict()
        for file_name in os.listdir(path):
            file_path = path + "/" + file_name
            if(os.path.isdir(file_path)):
                dir_dict = load_json(file_path)
                if dir_dict != None:
                    toReturn[file_name] = dir_dict
            elif(".json" in file_path):
                toReturn[file_name[:-5]] = load_json(file_path, encoding = encoding, pickle = pickle)
        if(len(toReturn) == 0):
            return None 
        return toReturn


def save_json(to_save, path, pickle, encoding = 'utf8'):
    """Saves the to_save dictionary to a json file if the path is a json file,
      or if the path is a directory, saves each top-level dictionary value to a 
      json file with the name of the key. Untested and cannot save multiple
      folders because it can only tell whether a file is meant to be json or folder
      from the path. Will throw an error when trying t    o overwrite a #READONLY file.
      Note that for frequent saving picklers are preferred, json is used when 
      human-readability is prioritized over ease of saving. In practice this means
      persistent settings are json, often read-only, and game-specific data is pickled. """
    if(".json" in path):
        _write_if_not_readonly(to_save, path, pickle, encoding = encoding)
    else:
        for file_name, data in to_save:
            save_json(data, path + "/" + file_name + ".json") 

            
def _write_if_not_readonly(to_save, path, pickle, encoding = 'utf8'):            
        if os.path.isfile(path):
            with open(path, 'r') as file: 
                if file.readline().strip() == "@READONLY":
                    raise RuntimeError("Tried to write to the following read-only file: " + path)
        with open(path, 'w') as file:
            to_write = jsonpickle.encode(to_save) if pickle \
                else json.dumps(to_save, sort_keys=sort_keys, allow_nan=False, indent=indent, separators=(",", ":"), encoding = encoding)
            file.write(to_write)

        
def save_game(to_save, saveName='1', pickle = True, encoding = 'utf8'):
    path = saves_dir + saveName + ".save"
    save_json(to_save, path, pickle, encoding = encoding)


def load_game(saveName='1', pickle = True, encoding = 'utf8'):
    path = saves_dir + saveName + ".save"
    return load_json(path, pickle, encoding = encoding)


def delete_game(saveName='1', pickle=True):
    path = saves_dir + saveName + ".save"
    if not os.path.isfile(path) and not os.path.isdir(path):
        raise FileNotFoundError
    os.remove(path)
