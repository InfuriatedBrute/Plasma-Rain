from os.path import curdir

from utils.json_parsers import load_json
  
edit_dir = curdir + "\\edit\\"
config = load_json(edit_dir + "config.json")
colors = load_json(edit_dir + "colors.json")
items = load_json(edit_dir + "items.json")
enchantments = load_json(edit_dir + "enchantments.json")
item_prefixes = load_json(edit_dir + "item_prefixes.json")
