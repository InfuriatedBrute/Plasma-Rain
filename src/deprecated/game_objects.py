from _ast import Str
from builtins import int, str

from numpy import char

from dataclasses import dataclass
from enum import Enum
from random import choice, randint
from utils.decorators import initialize_all_pre


class Bar_Stat_Kind(Enum):
    STR = ("Strength", "Health", "Wounds")
    AGI = ("Agility", "TUs", "RUs")
    REF = ("Reflexes", "Consciousness", "Fatigue")
    FOC = ("Focus", "Accuracy", "Suppression")
    WIL = ("Will", "Morale", "Insanity")
    ARM = ("Armor", "Front Armor", "Rear Armor")
    def base_short(self) : return self.name()
    def base_long(self): return self.value()[0]
    def current(self): return self.value()[1]
    def overlay(self): return self.value()[2]


# note that only current hp and base stats are relevant outside of battle and should not be reset at start
class Bar_Stat:
    base : int
    mod_class : Bar_Stat_Kind
    current, overlay : int = 0


# includes a link to relevant mod data inherent to all similar objects
# not called type or class for naming conflict
class has_mod_class:
    mod_class : mod_class

class Nameable(has_mod_class):
    name : str

class Tile(has_mod_class):
    lifetime : int = None    

@dataclass
class Item(has_mod_class):
    quantity : int = 1

@dataclass
class Currency(Item):
    def getString(self) -> Str:
        return self.mod_class['icon'] if self.mod_class['parent'] is None else (self.parent.getString() + self.mod_class['icon'])  #eg $RB for bio research


@initialize_all_pre
class Unit(Nameable):
    inventory : List[Item] = []
    STR, AGI, REF, FOC, WIL : Bar_Stat 
    def __init__(self, mod_class, name, statRanges):
        assert statRanges.length == 10
        self.STR =  Bar_Stat(mod_class = Bar_Stat_Kind.STR, base = randint(statRanges(0), statRanges(1)))
        self.AGI =  Bar_Stat(mod_class = Bar_Stat_Kind.AGI, base = randint(statRanges(2), statRanges(3)))
        self.REF =  Bar_Stat(mod_class = Bar_Stat_Kind.REF, base = randint(statRanges(4), statRanges(5)))
        self.FOC =  Bar_Stat(mod_class = Bar_Stat_Kind.FOC, base = randint(statRanges(6), statRanges(7)))
        self.WIL =  Bar_Stat(mod_class = Bar_Stat_Kind.WIL, base = randint(statRanges(8), statRanges(9)))
        self.ARM =  Bar_Stat(mod_class = Bar_Stat_Kind.WIL, base = randint(statRanges(9), statRanges(10)))


@dataclass
class Storage:
    units : List[Unit] = [] 
    inventory : List[Item] = [] #should be more complex eventually of course


@dataclass
class Craft(Nameable, Storage):
    pass

@dataclass
class Region(has_mod_class):
    crafts : List[Craft] = []
    score : int = 0
    storage : Storage  # some, if not all, regions may have the same storage