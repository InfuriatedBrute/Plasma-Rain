from IO.data.settings import config, colors
from IO.initialize_new_game import get_game_variables
from IO.input_handlers import handle_keys, handle_mouse, handle_main_menu
from IO.json_parsers import load_game, save_game, delete_game
from UI.menus import main_menu, message_box
from UI.messages import Message
from concepts.states import MainState, EscapeState, InputState, totalState

font_file = 'font/' + config['font'] + '.png'
m_state = MainState.MAIN
e_state = EscapeState.NONE
i_state = InputState.NONE
t_state = totalState(mstate, estate, istate)
#TODO rebuild engine


def main():
    pass
          
if __name__ == '__main__':
    main()
