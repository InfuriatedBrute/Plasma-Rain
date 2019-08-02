from builtins import int, str
from dataclasses import dataclass
from typing import List


# All game objects are Typed, except Global_Storage, which is singleton
# all types are mod-based, such as PLASMA_RIFLE
# UI elements and other stuff that arent exactly "game objects" are the exception. 
# The non-dataclasses below are not intended to be initialized, only inherited
# base / current / overlay
# Strength / Health / wounds
# Agility / TUs / RUs
# Reflexes / consciousness / fatigue
# Accuracy / current accuracy / suppression (from near-miss and melee)
# Will / Morale / Insanity (from psi and melee, and occasional failed melee)
class Bar_Stat:
    base, current, overlay : int


class Typed:
    type : str


class Coords:
    x : int = None
    y : int = None


class Nameable(Typed):
    name : str

    
@dataclass
class Structure(Typed):
    hp : int


@dataclass
class Terrain(Typed, Coords):
    lifetime : int    


@dataclass
class Item(Typed, Coords):
    quantity : int = 1


@dataclass 
class Unit(Nameable, Coords):
    inventory : List[Item]
    str, agility, reflexes, accuracy, will : Bar_Stat

    
class Storage:
    units : List[Unit]
    inventory : List[Item]


@dataclass
class Craft(Nameable, Storage):
    hp, fuel : int


@dataclass
class Region(Typed, Coords):
    structures : List[Structure]
    crafts : List[Craft]
    score : int
    storage : Storage  # may refer to global or planetary storage, depends on the region
