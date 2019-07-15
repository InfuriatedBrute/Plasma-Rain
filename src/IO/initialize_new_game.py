
from UI.messages import MessageLog

colors

def get_game_variables(settings=config):

    message_log = MessageLog(settings[message_x], settings[message_width],
                             settings[message_height])

    return message_log
 