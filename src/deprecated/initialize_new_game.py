from os.path import join
from IO.json_parsers import load_json

mods_dir = "../../data/mods"

def mod_dict(mod="vanilla"):
    return load_json(os.path.join(mods_dir, mod + "\\"))