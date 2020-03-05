from _ast import Str
from builtins import int, str

from numpy import char

from dataclasses import dataclass
from enum import Enum
from random import choice, randint


class Bar_Stat_Kind(Enum):
    #TODO adjust
    STR = ("Strength", "Health", "Wounds")
    AGI = ("Agility", "TUs", "RUs")
    REF = ("Reflexes", "Consciousness", "Fatigue")
    FOC = ("Focus", "Accuracy", "Suppression")
    WIL = ("Will", "Morale", "Insanity")
    def base_short(self) : return self.name()
    def base_long(self): return self.value()[0]
    def current(self): return self.value()[1]
    def overlay(self): return self.value()[2]


# note that only current hp and base stats are relevant outside of battle and should not be reset at start
class Bar_Stat:
    base : int
    kind : Bar_Stat_Kind
    current, overlay : int = 0


# all kinds are mod-based, such as PLASMA_RIFLE
# not called type or class for warning reasons
class Kinds:
    kind : str


class Coords:
    x : int = None
    y : int = None


class Nameable(Kinds):
    name : str



class Terrain(Kinds, Coords):
    lifetime : int = None    


@dataclass
class Item(Kinds, Coords):
    quantity : int = 1
    visible : bool = True #for example alien nests are invisible items

@dataclass
class Currency(Item):
    parent : Currency = None
    icon : char
    def getString(self) -> Str:
        return self.icon if self.parent is None else (self.parent.getString() + self.icon)  #eg $RB for bio research



class Unit(Nameable, Coords):
    inventory : List[Item] = []
    STR, AGI, REF, FOC, WIL : Bar_Stat 
    def __init__(self, kind, name, statRanges):
        self.kind = kind
        self.name = name
        assert statRanges.length == 10
        self.STR =  Bar_Stat(kind = Bar_Stat_Kind.STR, base = randint(statRanges(0), statRanges(1)))
        self.AGI =  Bar_Stat(kind = Bar_Stat_Kind.AGI, base = randint(statRanges(2), statRanges(3)))
        self.REF =  Bar_Stat(kind = Bar_Stat_Kind.REF, base = randint(statRanges(4), statRanges(5)))
        self.FOC =  Bar_Stat(kind = Bar_Stat_Kind.FOC, base = randint(statRanges(6), statRanges(7)))
        self.WIL =  Bar_Stat(kind = Bar_Stat_Kind.WIL, base = randint(statRanges(8), statRanges(9)))


@dataclass
class Storage:
    units : List[Unit] = [] 
    inventory : List[Item] = []


@dataclass
class Craft(Nameable, Storage):
    fuel : int = 100


@dataclass
class Region(Kinds, Coords):
    crafts : List[Craft] = []
    score : int = 0
    storage : Storage  # some regions may have the same storage
