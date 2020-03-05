from os.path import join

from IO.data.settings import config
from IO.json_parsers import load_json
from UI.messages import MessageLog
from concepts.game_objects import Region, Storage, Unit, Craft, Item, Currency
from IO.data.paths import mods_dir


def get_game_variables(settings=config, mod="vanilla"):
    message_log = MessageLog(settings['message_x'], settings['message_width'],
                             settings['message_height'])
    
    #TODO of course mod data must be organized here, a difficult task
    mods_dict = load_json(os.path.join(mods_dir, mod + "\\"))
    
    #build regions, starting craft + soldiers + items according to mod description
    
    geoscape = [Region]
    for r in geoscape:
        r.storage = Storage()
        r.storage.inventory.extend([Unit(), Craft(), Item(), Currency()])

    return message_log
