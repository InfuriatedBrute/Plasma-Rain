import os
import jsonpickle

#https://stackoverflow.com/a/7166139
project_folder = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
save_directory = os.path.join(project_folder, 'saves\\')
save_extension = '.save'

jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)

def save_game(player, entities, game_map, message_log, game_state, saveName='1'):
    path = save_directory + saveName + save_extension
    with open(path, 'w') as data_file:
        data_file.write(jsonpickle.encode({
            'player_index' : entities.index(player),
             'entities':entities, 'game_map':game_map,
              'message_log':message_log, 'game_state':game_state}))
        


def load_game(saveName='1'):
    path = save_directory + saveName + save_extension
    if not os.path.isfile(path):
        raise FileNotFoundError

    with open(path, 'r') as data_file:
        data = jsonpickle.decode(data_file.read())
        player_index = data['player_index']
        entities = data['entities']
        game_map = data['game_map']
        message_log = data['message_log']
        game_state = data['game_state']

    player = entities[player_index]

    return player, entities, game_map, message_log, game_state


def delete_game(saveName='1'):
    path = save_directory + saveName + save_extension
    if not os.path.isfile(path):
        raise FileNotFoundError
    os.remove(path)
