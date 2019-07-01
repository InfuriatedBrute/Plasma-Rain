from json import loads, dumps
import os


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


def load_json(path):
    """
    Parameters:
        path (str) : A path pointing to the json file or directory of json files to load
    
    Returns:
        a dictionary containing all json data and directories with json files at path, or None if no such files are found.
        Comments in json files are not included.
    """
     
    if(".json") in path:
        with open(path) as file:
            return loads(remove_comments(file.read()))
    else:
        toReturn = dict()
        for file_name in os.listdir(path):
            file_path = path + "/" + file_name
            if(os.path.isdir(file_path)):
                dir_dict = load_json(file_path)
                if dir_dict != None:
                    toReturn[file_name] = dir_dict
            elif(file_path.contains(".json")):
                toReturn[file_name[:-5]] = load_json(file_path)
        if(toReturn.len() == 0):
            return None 
        return toReturn


# unused, picklers preferred so far. It is fairly difficult to save json without deleting comments.
#
# def save_json(to_save, path, sort_keys=False, indent=2):
#     """Saves the to_save dictionary to a json file if the path is a json file,
#      or if the path is a directory, saves each top-level dictionary value to a 
#      json file with the name of the key. Untested and cannot save multiple
#      folders because it can only tell whether a file is meant to be json or folder
#      from the path. Will throw an error when trying to overwrite a #READONLY file.
#      Note that for frequent saving data_shelvers are preferred, json is used when 
#      human-readability is prioritized over ease of saving. In practice this means
#      persistent settings are json, often read-only, and game-specific data is shelved. """
#     if(".json" in path):
#         _write_if_not_readonly(to_save, path, sort_keys, indent)
#     else:
#         for file_name, data in to_save:
#             save_json(data, path + "/" + file_name + ".json", sort_keys, indent)

            
def _write_if_not_readonly(to_save, path, sort_keys, indent):            
        if os.path.isfile(path):
            with open(path, 'r') as file: 
                if file.readline().strip() == "#READONLY":
                    raise RuntimeError("Tried to write to the following read-only file: " + path)
        with open(path, 'w') as file:
            file.write(dumps(to_save, sort_keys=sort_keys, indent=indent, allow_nan=False, separators=(",", ":")))
