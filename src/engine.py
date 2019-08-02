from tcod import image_load
import tdl

from IO.constants import config, colors
from IO.input_handlers import handle_keys, handle_mouse, handle_main_menu
from IO.jsonpicklers import load_game, save_game, delete_game
from UI.menus import main_menu, message_box
from UI.messages import Message
from concepts.states import totalState

# from IO.initialize_new_game import get_game_variables
# from render_functions import clear_all, render_all
# Possible engine features: keyboard targeting, improved LoS, examining, "which thing would you like to pick up"
# Run function, ? screen
font_file = 'font/' + config['font'] + '.png'


def base_font():
    tdl.set_font(font_file, greyscale=config['greyscale'], altLayout=True)


def main():
    base_font()

    root_console = tdl.init(config['screen_width'], config['screen_height'], config['window_title'])
    con = tdl.Console(config['screen_width'], config['screen_height'])
    panel = tdl.Console(config['screen_width'], config['panel_height'])

    show_main_menu = True
    show_load_error_message = False

    main_menu_background_image = image_load('menu_background.png')

    while not tdl.event.is_window_closed():
        for event in tdl.event.get():
            if event.type == 'KEYDOWN':
                user_input = event
                break
        else:
            user_input = None

        if show_main_menu:
            main_menu(con, root_console, main_menu_background_image, config['screen_width'],
                      config['screen_height'], colors)

            if show_load_error_message:
                message_box(con, root_console, 'No save game to load', 50, config['screen_width'],
                            config['screen_height'])

            tdl.flush()

            action = handle_main_menu(user_input)

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            quit_ = action.get('quit')

            if show_load_error_message and (new_game or load_saved_game or quit_):
                show_load_error_message = False
            elif new_game:
                player, entities, game_map, message_log, game_state = get_game_variables(config)
                game_state = GameStates.PLAYERS_TURN

                show_main_menu = False
            elif load_saved_game:
                try:
                    player, entities, game_map, message_log, game_state = load_game()
                    delete_game()  # The save is deleted on load. If the program crashes you will have no save.
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif quit_:
                break

        else:
            root_console.clear()
            con.clear()
            panel.clear()
            play_game(player, entities, game_map, message_log, game_state, root_console, con, panel, config)

            show_main_menu = True  # Once done playing the game, if still open, show main menu


def play_game(player, entities, game_map, message_log, game_state, root_console, con, panel, config):
    base_font()

    fov_recompute = True

    mouse_coordinates = (0, 0)

    previous_game_state = game_state

    targeting_item = None

    while not tdl.event.is_window_closed():
        if fov_recompute:
            if config['wallhack']:
                for x, y in game_map:
                    game_map.fov[x, y] = True
            else:
                game_map.compute_fov(player.x, player.y, fov=config['fov_algorithm'], radius=config['fov_radius'],
                                 light_walls=config['fov_light_walls'])

        render_all(con, panel, entities, game_map, fov_recompute, root_console, message_log,
                   config['screen_width'], config['screen_height'],
                   config['panel_height'], config['panel_y'], mouse_coordinates, colors,
                   game_state)
        tdl.flush()

        clear_all(con, entities)

        fov_recompute = False

        for event in tdl.event.get():
            if event.type == 'KEYDOWN':
                user_input = event
                break
            elif event.type == 'MOUSEMOTION':
                mouse_coordinates = event.cell
            elif event.type == 'MOUSEDOWN':
                user_mouse_input = event
                break
        else:
            user_input = None
            user_mouse_input = None

        if not (user_input or user_mouse_input):
            continue

        action = handle_keys(user_input, game_state)
        mouse_action = handle_mouse(user_mouse_input)

        move = action.get('move')
        wait = action.get('wait')
        interact = action.get('interact')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')
        level_up = action.get('level_up')
        show_character_screen = action.get('show_character_screen')
        exit_ = action.get('exit')
        quit_ = action.get('quit')
        fullscreen = action.get('fullscreen')
        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        player_turn_results = []
        
        # Start of action code, each button press / click results in one of these if statements being executed
        # Clicking and pressing really fast or sleeping the thread has been shown to cause multiple actions
        # Hence why we need a dictionary of actions instead of a single action, despite taking far more code
        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            if game_map.walkable[destination_x, destination_y]:
                target = get_blocking_entity_at(entities, destination_x, destination_y)

                if target:
                    attack_results = player.fighter.attack(target, game_map, entities)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)

                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN

        if wait:
            game_state = GameStates.ENEMY_TURN
            
        if interact and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.x == player.x and entity.y == player.y:
                    if entity.item :
                        pickup_results = player.inventory.add_item(entity, colors)
                        player_turn_results.extend(pickup_results)
                        break
                    if entity.stairs and entity.stairs.down:
                        game_map, entities = next_floor(player, message_log, entity.stairs.floor, config)
                        fov_recompute = True
                        con.clear()
                        break
            else:
                message_log.add_message(Message('There is nothing here to interact with.', colors.get('yellow')))
        
        if level_up:
            if level_up == 'hp':
                player.fighter.base_hp += 20
                player.fighter.hp += 20
            elif level_up == 'str':
                player.fighter.base_power += 1
            elif level_up == 'def':
                player.fighter.base_defense += 1
            game_state = previous_game_state
        if show_character_screen:
            previous_game_state = game_state
            game_state = GameStates.CHARACTER_SCREEN
        if show_inventory:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(
                player.inventory.items):
            item = player.inventory.items[inventory_index]

            if game_state == GameStates.SHOW_INVENTORY:
                results, next_turn = player.inventory.use(item, entities=entities, game_map=game_map)
                if(next_turn): game_state = GameStates.ENEMY_TURN
                player_turn_results.extend(results)

            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item, colors))
        
        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results, next_turn = player.inventory.use(targeting_item, entities=entities,
                                                        game_map=game_map, target_x=target_x, target_y=target_y)
                if(next_turn): game_state = GameStates.ENEMY_TURN
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if exit_:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.CHARACTER_SCREEN):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
        
        if quit_:
            save_game(player, entities, game_map, message_log, game_state)
            return True
        if fullscreen:
            tdl.set_fullscreen(not tdl.get_fullscreen())
        # End of action code

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            equip = player_turn_result.get('equip')            
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')
            xpBounty = player_turn_result.get('xpBounty')

            if message:
                message_log.add_message(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity, colors)
                else:
                    message = kill_monster(dead_entity, colors)

                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)

                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if item_dropped:
                entities.append(item_dropped)

                game_state = GameStates.ENEMY_TURN
                
            if equip:
                equip_results = player.equipment.toggle_equip(equip)

                for equip_result in equip_results:
                    equipped = equip_result.get('equipped')
                    dequipped = equip_result.get('dequipped')

                    if equipped:
                        message_log.add_message(Message('You equipped the {0}'.format(equipped.name)))

                    if dequipped:
                        message_log.add_message(Message('You dequipped the {0}'.format(dequipped.name)))

                game_state = GameStates.ENEMY_TURN

            if targeting:
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)

            if targeting_cancelled:
                game_state = previous_game_state

                message_log.add_message(Message('Targeting cancelled'))
                
            if xpBounty:
                leveled_up = player.level.add_xp(xpBounty)
                message_log.add_message(Message('You gain {0} experience points.'.format(xpBounty)))
                if leveled_up:
                    message_log.add_message(Message(
                        'Your battle skills grow stronger! You reached level {0}'.format(player.level.current_level) + '!',
                        colors.get('yellow')))
                    previous_game_state = game_state
                    game_state = GameStates.LEVEL_UP

        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, game_map, entities)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                            message_log.add_message(message)
                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity, colors)
                            else:
                                message = kill_monster(dead_entity, colors)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break
            else:
                game_state = GameStates.PLAYERS_TURN

    # If this line is reached the program was quit via the exit button. Save and quit.
    save_game(player, entities, game_map, message_log, game_state)

          
if __name__ == '__main__':
    main()
