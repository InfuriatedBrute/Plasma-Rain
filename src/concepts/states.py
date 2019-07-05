from utils.enum import enum

#     A single state, an instance of this enum, tracks exactly which screens the player has open and what input is valid.
#     There are two exceptions:
#     First is the escape screen, which is tracked by an instance of the EscapeGameState enum simultaneously.
#     Second is the typingaiming state, which denotes whether we are waiting on user input.
#     All states are tracked at all times.


GameStates = enum('MAIN', 'HI_SCORE', 'NEW_GAME', 'G_MAIN', 'G_TURN', 'G_SOLDIER', 'G_ARMOR', 'G_EQUIP', 'G_CRAFT', 'G_CREW', 'G_BATTLE', 
                  'G_ENEMY', 'G_SCORE', 'G_GRAPHS', 'G_RESEARCH', 'G_MANUFACTURE', 'G_COMBAT', 'B_MAIN', 'B_INV', 'B_TURN', 'B_ENEMY')
    
EscapeGameState = enum('NONE', 'SAVE', 'LOAD', 'OPTIONS', 'KEYBINDS', 'PEDIA')

TypingAimingState = enum('NONE', 'TYPING', 'AIMING')