unit_types, craft_types, item_types, structure_types = None

def set_mod(mod_name):
    specific_mod_dir = os.path.join(mods_dir, _mod_name)
    unit_types = load_json(os.path.join(specific_mod_dir, "unit_types.json"))
    craft_types = load_json(os.path.join(specific_mod_dir, "craft_types.json"))
    item_types = load_json(os.path.join(specific_mod_dir, "item_types.json"))
    structure_types = load_json(os.path.join(specific_mod_dir, "structure_types.json"))
    # Mission and region types...? 