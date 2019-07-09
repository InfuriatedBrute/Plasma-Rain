from utils.enum import enum
from builtins import int, str
from typing import List
from dataclasses import dataclass

# All game objects are Typed, except Global_Storage, which is singleton
# all types are mod-based, such as PLASMA_RIFLE
# UI elements and other stuff that aren't exactly "game objects" are the exception. 
# The non-dataclasses below are not intended to be initialized, only inherited


class Typed:
    type : str


class Coords:
    x : int = None
    y : int = None


class Nameable(Typed):
    name : str


class Quantitied(Typed):
    quantity : int = 1


@dataclass
class Terrain(Typed, Coords):
    lifetime : int    

@dataclass
class Item(Typed, Coords):
    quantity : int = 1


@dataclass 
class Unit(Nameable, Coords):
    inventory : List[Item]
    str, dex, agi, ref, wil, TU, HP, EP, MP, wounds : int

    
class Storage:
    units : List[Unit]
    inventory : List[Item]


@dataclass
class Craft(Nameable, Storage):
    hp, fuel : int


@dataclass
class Structure(Typed):
    hp : int


@dataclass
class Region(Typed, Coords):
    structures : List[Structure]
    crafts : List[Craft]
    score : int
    storage : Storage #may refer to global or planetary storage, modder option