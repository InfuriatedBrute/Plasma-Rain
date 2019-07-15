from os.path import curdir

from IO.json_parsers import load_json
  
edit_dir = curdir + "\\non-python\\edit\\"
config = load_json(edit_dir + "config.json")
colors = load_json(edit_dir + "colors.json")

unit_types = load_json(edit_dir + "unit_types.json")
craft_types = load_json(edit_dir + "unit_types.json")
item_types = load_json(edit_dir + "unit_types.json")
structure_types = load_json(edit_dir + "structure_types.json")
#Mission and region types...? 