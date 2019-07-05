from utils.enum import enum
from dataclasses import dataclass
from typing import List

#There should not be a single game object which is not a Namey or Inty.

#types are mod-based, supertypes are not
#Every game should have one Namey with HOME_BASE type and BASE supertype, unless research isn't shared
#Recommended BASE  stats are starting attributes and whether the base is established or not

Namey_Supertype = enum('SOLDIER', 'CRAFT', 'BASE')
@dataclass
class Namey:
    type : str
    supertype : Namey_Supertype
    name : str
    inventory : List
    stats : dict[str : int]

Inty_Supertype = enum('ITEM', 'TERRAIN', 'STRUCTURE', 'PRODUCTION', 'PRODUCTION_PROGRESS', 'SCORE')
#ITEM stat = number of that item, TERRAIN stat = lifetime, STRUCTURE stat = HP, or days until complete if negative
#PRODOUCTION stat = number of sci/eng working (or not working if type = "idle"), PRODUCTION_PROGRESS = completion of tech/manufacture 0-100
#SCORE stat = number of that particular score
@dataclass
class Inty:
    type : str
    supertype : Inty_Supertype
    stat : int