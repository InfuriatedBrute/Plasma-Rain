import os

from IO.json_parsers import load_json
from IO.data.paths import mods_dir, settings_dir

config = load_json(os.path.join(settings_dir, ("config.json")))
colors = load_json(os.path.join(settings_dir, ("colors.json")))