from concepts.states import totalState, MainState, EscapeState


    
def handle_mouse(mouse_event):
    if mouse_event:
        (x, y) = mouse_event.cell

        if mouse_event.button == 'LEFT':
            return {'left_click': (x, y)}
        elif mouse_event.button == 'RIGHT':
            return {'right_click': (x, y)}

    return {}

def handle_keys(user_input, state : totalState):
    if(user_input):
        universal_output = handle_universal_keys(user_input)
        if(universal_output):
            return universal_output
        elif state.escape == EscapeState.NONE and state.main == MainState.MAIN:
            return handle_main_menu(user_input)
    return {}

    
def handle_universal_keys(user_input):
    if user_input:
        key, char, alt = user_input.key, user_input.char, user_input.alt
        if key == 'ENTER' and alt:
            return {'fullscreen': True}
        elif key == 'ESCAPE':
            return {'exit': True}
        elif char == 'q' and alt:
            return {'quit': True}
    return {}


def handle_main_menu(user_input):
    if user_input:
        char = user_input.char
        universal_output = handle_universal_keys(user_input)
        if(universal_output):
            return universal_output
        elif char == 'a':
            return {'new_game': True}
        elif char == 'b':
            return {'load_game': True}
        elif char == 'c':
            return {'quit': True}
    return {}
