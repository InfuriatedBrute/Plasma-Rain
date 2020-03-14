from builtins import int
from dataclasses import dataclass
import inspect

superclass_names = ['tile']

def build_blueprints(x : dict):
    '''
    Returns all blueprints for a mod, where x is the blueprints folder in dictionary form.
    All blueprints are stored inside a json file with the same name as their superclass (no plurals).
    A blueprint is an instance of a superclass. All objects in this module have a reference to a blueprint.
    '''
    def all_to_blueprint(super_name : str):
        def to_blueprint(bp_name : str):
            init = globals()[super_name.title() + "_Superclass"]
            init_args = inspect.getfullargspec(init).args
            
            bp_dict = x[super_name][bp_name].copy()
            if 'icon' in init_args:
                bp_dict.update({'icon' : bp_name})
                
            bp = init(**bp_dict)
            return (bp_name, bp)
        
        super_blueprints = map(to_blueprint, x[super_name])
        return (super_name, dict(super_blueprints))

    all_blueprints = map(all_to_blueprint, superclass_names)
    return dict(all_blueprints)
    
@dataclass
class Tile_Superclass:
    icon : str
    mouseover_name : str
    width : int
    depth : int
    
@dataclass
class Tile:
    blueprint : Tile_Superclass