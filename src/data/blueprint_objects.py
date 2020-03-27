import inspect
from builtins import int
from dataclasses import dataclass

blueprint_class_name_list = ['tile']


def build_blueprints(x: dict):
    """
    Returns all blueprints for a mod, where x is the blueprints folder in dictionary form.
    All blueprints are stored inside a json file with the same name as their superclass (no plurals).
    """
    def all_to_blueprint(class_name: str):
        def to_blueprint(bp_name: str):
            init = globals()[class_name.title() + "Blueprint"]
            init_args = inspect.getfullargspec(init).args

            # BEGIN conversion code, for fixing some of the quirks in json format

            bp_dict = x[class_name][bp_name].copy()
            assert 'name' in init_args
            bp_dict.update({'name': bp_name})

            for key, value in x[class_name][bp_name].items():
                if value is [(int, int)]:  # assume it is a range
                    bp_dict.update(map((lambda start, end: range(start, end)), value))

            # END conversion code, for fixing some of the quirks in json format

            bp = init(**bp_dict)
            return bp_name, bp

        blueprint_class = map(to_blueprint, x[class_name])
        return class_name, dict(blueprint_class)

    all_blueprints = map(all_to_blueprint, blueprint_class_name_list)
    return dict(all_blueprints)


@dataclass
class TileBlueprint:
    name: str
    icon: str
    width: int
    depth: int


@dataclass
class Tile:
    blueprint: TileBlueprint = TileBlueprint(" ", "Empty", 0, 0)


# Armor only has a Blueprint, since all armors of a type are identical
@dataclass
class ArmorBlueprint:
    name: str
    width: int
    depth: int
    stat_mods: (int,)*5


@dataclass
class UnitBlueprint:
    name: str
    icon: str
    start_stats: [range]*5
    potential_stats: [range]*5
    allowed_armors: [str]


@dataclass
class Unit:
    blueprint: UnitBlueprint
    current_stats: [int]*5
    overlay_stats: [int]*5
