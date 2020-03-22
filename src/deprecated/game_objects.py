from _ast import Str
from builtins import int, str
from dataclasses import dataclass
from enum import Enum
from random import randint

from deprecated.decorators import initialize_all_pre


class BarStatKind(Enum):
    STR = ("Strength", "Health", "Wounds")
    AGI = ("Agility", "TUs", "RUs")
    REF = ("Reflexes", "Consciousness", "Fatigue")
    FOC = ("Focus", "Accuracy", "Suppression")
    WIL = ("Will", "Morale", "Insanity")
    ARM = ("Armor", "Front Armor", "Rear Armor")

    def base_short(self): return self.name()

    def base_long(self): return self.value()[0]

    def current(self): return self.value()[1]

    def overlay(self): return self.value()[2]


# note that only current hp and base stats are relevant outside of battle and should not be reset at start
class BarStat:
    base: int
    mod_class: BarStatKind
    current, overlay = 0, 0


# includes a link to relevant mod data inherent to all similar objects
# not called type or class for naming conflict
class HasModClass:
    mod_class: ModClass


class Nameable(HasModClass):
    name: str


class Tile(HasModClass):
    lifetime: int = None


@dataclass
class Item(HasModClass):
    quantity: int = 1


@dataclass
class Currency(Item):
    def getString(self) -> Str:
        return self.mod_class['icon'] if self.mod_class['parent'] is None else (
                    self.parent.getString() + self.mod_class['icon'])  # eg $RB for bio research


@initialize_all_pre
class Unit(Nameable):
    inventory: [Item] = []
    STR : BarStat
    AGI: BarStat
    REF: BarStat
    FOC: BarStat
    WIL: BarStat

    def __init__(self, mod_class, name, stat_ranges):
        assert stat_ranges.length == 10
        self.STR = BarStat(mod_class=BarStatKind.STR, base=randint(stat_ranges(0), stat_ranges(1)))
        self.AGI = BarStat(mod_class=BarStatKind.AGI, base=randint(stat_ranges(2), stat_ranges(3)))
        self.REF = BarStat(mod_class=BarStatKind.REF, base=randint(stat_ranges(4), stat_ranges(5)))
        self.FOC = BarStat(mod_class=BarStatKind.FOC, base=randint(stat_ranges(6), stat_ranges(7)))
        self.WIL = BarStat(mod_class=BarStatKind.WIL, base=randint(stat_ranges(8), stat_ranges(9)))
        self.ARM = BarStat(mod_class=BarStatKind.WIL, base=randint(stat_ranges(9), stat_ranges(10)))


@dataclass
class Storage:
    units: [Unit]
    inventory: [Item]   # should be more complex eventually of course


@dataclass
class Craft(Nameable, Storage):
    pass


@dataclass
class Region(HasModClass):
    crafts: [Craft]
    score: int
    storage: Storage  # some, if not all, regions may have the same storage
