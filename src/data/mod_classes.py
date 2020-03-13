from builtins import int
from dataclasses import dataclass

def build_mod(mod : dict):
    def _to_tile_class(item):
        k, v = item
        v.update({'icon' : k})
        return k, Tile_Class(**v)
    return {
        'tiles':
            dict(map(_to_tile_class, mod['tiles'].items()))
    }
    
@dataclass
class Tile_Class:
    icon : str
    mouseover_name : str
    width : int
    depth : int