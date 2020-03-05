#     A single state, an instance of the GameStates enum, tracks exactly which screens the player has open and what input is valid.
#     There are two exceptions:
#     First is the escape screen, which is tracked by an instance of the EscapeStates enum simultaneously.
#     Second is InputStates, which denotes whether we are waiting on user input.
#     All states are tracked at all times.

from dataclasses import dataclass
from enum import Enum


class MainState(Enum):
    MAIN, HI_SCORE, NEW_GAME, \
     G_MAIN, G_TURN, G_SOLDIER, G_ARMOR, G_EQUIP, G_CRAFT, G_CREW, G_BATTLE, G_ENEMY, G_SCORE, G_GRAPHS, G_COMBAT, \
     B_MAIN, B_INV, B_TURN, B_ENEMY = range(1, 22)

    
class EscapeState(Enum):
    NONE, SAVE, LOAD, OPTIONS, KEYBINDS, PEDIA = range(1, 7)


class InputState(Enum):
    NONE, TYPING, AIMING = range (1, 4)

    
@dataclass
class totalState:
    main : MainState
    escape : EscapeState
    input : InputState
