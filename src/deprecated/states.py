#     A single state, an instance of the GameStates enum, tracks exactly which screens the player has open and what input is valid.
#     There are two exceptions:
#     First is the escape screen, which is tracked by an instance of the EscapeStates enum simultaneously.
#     Second is InputStates, which denotes whether we are waiting on user input.
#     All states are tracked at all times.

from dataclasses import dataclass
from enum import Enum


class MainState(Enum):
    MAIN, \
    B_MAIN, B_INV, B_ENEMY, B_AIMING = range(0, 21)


class EscapeState(Enum):
    NONE, MAIN = range(0, 6)


@dataclass
class totalState:
    main: MainState
    escape: EscapeState
