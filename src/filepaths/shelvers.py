import os
import shelve


save_directory = 'saves\\'

def save_game(player, entities, game_map, message_log, game_state, saveName='1'):
    with shelve.open(save_directory + saveName, 'n') as file:
        file['player_index'] = entities.index(player)
        file['entities'] = entities
        file['game_map'] = game_map
        file['message_log'] = message_log
        file['game_state'] = game_state


def load_game(saveName='1'):
    if not os.path.isfile(save_directory + saveName + '.dat'):
        raise FileNotFoundError

    with shelve.open('saves\\' + saveName, 'r') as file:
        player_index = file['player_index']
        entities = file['entities']
        game_map = file['game_map']
        message_log = file['message_log']
        game_state = file['game_state']

    player = entities[player_index]

    return player, entities, game_map, message_log, game_state


def delete_game(saveName='1'):
    if not os.path.isfile(save_directory + saveName + '.dat'):
        raise FileNotFoundError
    os.remove(save_directory + saveName + '.dat')