import codecs
import os.path
import time

from bearlibterminal import terminal
from typing import Optional

from IO.json_parsers import load_json
from IO.paths import mods_dir
from data.blueprint_objects import build_blueprints, Tile

FPS = 60
SPEED_CAP = 40
SPEED_ACCELERATION = 1
MAP_DEPTH, MAP_LENGTH, MAP_WIDTH = 4, 20, 20
TILE_SIZE = 32
# In fractions of screen size
SCROLL_LENIENCY = 0
EMPTY_TILE = Tile()
DIR_PATH = os.path.dirname(__file__)
# In tiles, the size of the margins, negative meaning some is rendered offscreen
# negatives are for rendering partially-covered tiles
MARGIN_TOP, MARGIN_BOTTOM, MARGIN_LEFT, MARGIN_RIGHT = 4, 0, 0, 0


def main():
    terminal.open()

    terminal.set("output.vsync=true")
    terminal.set("window: title='Plasma Rain', resizeable=true, minimum-size=16x12")
    terminal.set("window: size=28x21; font: " + os.path.join(DIR_PATH, '../data/media/lucida.ttf') + ", size=32x32")
    terminal.set("input.filter= [keyboard+, mouse_move]")  # Only key release and mouse move trigger state updates
    terminal.composition(terminal.TK_ON)
    terminal.bkcolor(terminal.color_from_name("gray"))
    # grey (or gray), red, flame, orange, amber, yellow, lime,
    # chartreuse, green, sea, turquoise, cyan, sky, azure, blue,
    # han, violet, purple, fuchsia, magenta, pink, crimson, transparent
    terminal.color(terminal.color_from_name("black"))

    x_speed, y_speed, text_offset = (0,) * 3

    # initialize blank tile_map
    tile_map: [[[Tile]]] = [[[EMPTY_TILE
                              for _ in range(MAP_WIDTH)]
                             for _ in range(MAP_LENGTH)]
                            for _ in range(MAP_DEPTH)]
    blueprints = build_blueprints(load_json(os.path.join(mods_dir, "vanilla/blueprints/"), pickle=False))
    zone = load_zone(os.path.join(DIR_PATH, '../data/placeholder/map2.json'), blueprints)
    paste_zone(zone, tile_map, z=0, y=0)

    prev_frame_time = time.perf_counter()
    iterations = 0

    # tile_map will only render to screen inside the display, generally set to not overlap with UI
    # tile_map will only be scrollable between the offset bounds
    # coordinates are down-right = positive, "opposite" for the offset    
    # set offset_leniency to 1 and you will only be allowed to scroll 1 more tile than enough to see every tile
    # in general the coordinate system is z, y, x: depth, length, width. No height because it's ambiguous.
    screen_width, screen_length, display_min_y, display_max_y, display_min_x, display_max_x, \
        min_y_offset, max_y_offset, min_x_offset, max_x_offset, x_scroll_leniency, y_scroll_leniency = (0,) * 12

    """
    Adjusts the bounds defined above, to be called when opening and resizing
    """

    def reset_bounds():
        # nonlocal allows modification of outer function's variables
        nonlocal screen_width, screen_length, display_min_y, display_max_y, display_min_x, display_max_x, \
            min_y_offset, max_y_offset, min_x_offset, max_x_offset, y_scroll_leniency, x_scroll_leniency

        screen_length = terminal.state(terminal.TK_HEIGHT) * TILE_SIZE
        screen_width = terminal.state(terminal.TK_WIDTH) * TILE_SIZE

        y_scroll_leniency = int(screen_length * SCROLL_LENIENCY)
        x_scroll_leniency = int(screen_length * SCROLL_LENIENCY)

        display_min_y = 0 + MARGIN_TOP * TILE_SIZE
        display_max_y = screen_length - MARGIN_BOTTOM * TILE_SIZE
        display_min_x = 0 + MARGIN_LEFT * TILE_SIZE
        display_max_x = screen_width - MARGIN_RIGHT * TILE_SIZE

        # TODO convert offsets into actual tile offsets, exclude the complex GUI stuff
        min_y_offset = min(0, -y_scroll_leniency)
        max_y_offset = max(0, -screen_length + MAP_WIDTH * TILE_SIZE + y_scroll_leniency)
        min_x_offset = min(0, -x_scroll_leniency)
        max_x_offset = max(0, -screen_width + MAP_WIDTH * TILE_SIZE + x_scroll_leniency)

    def get_highest_tile_if_exists(start_z: int, tile_y: int, tile_x: int) -> Optional[Tile]:
        if tile_y not in range(0, MAP_WIDTH) or tile_x not in range(0, MAP_LENGTH):
            return None
        for zi in range(start_z, -1, -1):
            if tile_map[zi][tile_y][tile_x] != EMPTY_TILE:
                return tile_map[zi][tile_y][tile_x]
        return None

    reset_bounds()

    y_offset, x_offset = max(display_min_y, 0), max(0, display_min_x)

    camera_height = 0

    proceed = True
    while proceed:
        # t = partial-tile offset in pixels
        # i = full-tile offset in tiles
        # c = number of tiles to render
        ty = y_offset % TILE_SIZE
        tx = x_offset % TILE_SIZE
        iy = y_offset // TILE_SIZE
        ix = x_offset // TILE_SIZE
        # vc = screen_length // TILE_SIZE + 1
        # hc = screen_width // TILE_SIZE + 1
        mouse_x = terminal.state(terminal.TK_MOUSE_X) - x_offset - display_min_x // TILE_SIZE
        mouse_y = terminal.state(terminal.TK_MOUSE_Y) - y_offset - display_min_y // TILE_SIZE

        x_offset = clamp(x_offset + x_speed, min_x_offset, max_x_offset)
        y_offset = clamp(y_offset + y_speed, min_y_offset, max_y_offset)

        terminal.clear()

        mouse_over = get_highest_tile_if_exists(camera_height, mouse_y, mouse_x)
        if mouse_over is not None:
            mouse_over = mouse_over.blueprint.mouse_over_name

        terminal.print(2, 0, "speed: {}, {}".format(x_speed, y_speed))
        terminal.print(2, 1, "offset: {}, {}".format(ix, iy))
        terminal.print(2, 2, "tile at ({}, {}): {}".format(mouse_x, mouse_y, mouse_over))

        higher_tile_already_rendered: [[bool]] = [[False
                                                   for _ in range(MAP_WIDTH)]
                                                  for _ in range(MAP_LENGTH)]

        # print scrollable map
        for z in range(camera_height, -1, -1):  # top has higher render priority
            for y in range(0, MAP_LENGTH):
                for x in range(0, MAP_WIDTH):
                    # s = final coords in pixels
                    sx = (x + ix) * TILE_SIZE + tx + display_min_x
                    sy = (y + iy) * TILE_SIZE + ty + display_min_y
                    # render only on-screen tiles
                    if (display_min_y <= sy <= display_max_y
                            and display_min_x <= sx <= display_max_x
                            and not higher_tile_already_rendered[y][x]
                            and tile_map[z][y][x] != EMPTY_TILE):
                        if z < camera_height and tile_map[z][y][x] != EMPTY_TILE:
                            terminal.put_ext(0, 0, sx, sy, 0x2588,
                                             (terminal.color_from_name('yellow'), terminal.color_from_name('red')) * 4)
                        terminal.put_ext(0, 0, sx, sy, tile_map[z][y][x].blueprint.icon)
                        higher_tile_already_rendered[y][x] = tile_map[z][y][x] != EMPTY_TILE

        terminal.refresh()

        while proceed and terminal.has_input():
            key = terminal.read()
            if key == terminal.TK_CLOSE or key == terminal.TK_ESCAPE:
                proceed = False
            elif key == terminal.TK_RESIZED:
                reset_bounds()
            elif key == terminal.TK_KP_PLUS:
                camera_height = clamp(camera_height + 1, 0, MAP_DEPTH - 1)
            elif key == terminal.TK_KP_MINUS:
                camera_height = clamp(camera_height - 1, 0, MAP_DEPTH - 1)
        if terminal.state(terminal.TK_LEFT):
            if x_speed < SPEED_CAP:
                x_speed += SPEED_ACCELERATION
            else:
                x_speed = SPEED_CAP
        elif terminal.state(terminal.TK_RIGHT):
            if x_speed > -SPEED_CAP:
                x_speed -= SPEED_ACCELERATION
            else:
                x_speed = -SPEED_CAP
        else:
            x_speed -= sgn(x_speed)
        if terminal.state(terminal.TK_UP):
            if y_speed < SPEED_CAP:
                y_speed += SPEED_ACCELERATION
            else:
                y_speed = SPEED_CAP
        elif terminal.state(terminal.TK_DOWN):
            if y_speed > -SPEED_CAP:
                y_speed -= SPEED_ACCELERATION
            else:
                y_speed = -SPEED_CAP
        else:
            y_speed -= sgn(y_speed)

        current_time = time.perf_counter()
        # If twice as slow as desirable warn us, check once every 10 seconds
        if iterations % (10 * FPS) == 0 and iterations > 0 and current_time - prev_frame_time > 2 / FPS:
            print("Lag detected. Desired frame_time: {}; actual frame_time: {}".format(
                1 / FPS, current_time - prev_frame_time))
        prev_frame_time = current_time
        iterations += 1

        terminal.delay(1000 // FPS)
    terminal.close()

def prep(line: str) -> str:
    return line[0:-2] if line[-2:] == '\r\n' else line


def load_utf(path) -> [str]:
    """
    loads a UTF file into a string list, padding each line with spaces to the maximum length among other lines
    """
    with codecs.open(path, encoding='utf-8') as f:
        array = [prep(line) for line in f]
        length = longest_in_list(array, 1)
        return [pad_to_length(line, length) for line in array]


def pad_to_length(x: str, length: int) -> str:
    while len(x) != length:
        x += ' '
    return x


def pad_all(x: list, length: int) -> list:
    """
     Pads all strings in x to the given length, then returns x
     Accepts a list of any dimension, only modifying strings contained by any number of lists
    """
    for item in x:
        if isinstance(item, list):
            pad_all(item, length)
        elif isinstance(item, str):
            pad_to_length(item, length)
    return x


def longest_in_list(x: list, k: int) -> int:
    """
     Takes an n-dimensional list and returns the length of the longest n-k dimenional list in it.
     If k == 0, the function is equivalent to len(l). If k == -1, it will return the lowest dimensional list.
    """
    if k == 0:
        return len(x)
    length = 0
    base_case = k == 1 or (k == -1 and not isinstance(x[0], list))
    for sublist in x:
        new_length = len(sublist) if base_case else longest_in_list(sublist, k - 1)
        length = max(length, new_length)
    return length


def load_zone(path, blueprints) -> [[[Tile]]]:
    zone_json = load_json(path, pickle=False)
    zone = [[[Tile(blueprint=blueprints['tile'][c]) for c in row] for row in grid] for grid in
            zone_json]
    return zone


# pastes the given zone onto the given map with the given offset
# will throw an error if map bounds are exceeded in the process
def paste_zone(zone: list, tile_map: list, x=0, y=0, z=0):
    # bounds for zone and map respectively
    # NOTE potentially low-performance
    mz, my, mx = bounds(tile_map)
    for iz in range(0, len(zone)):
        for iy in range(0, len(zone[iz])):
            for ix in range(0, len(zone[iz][iy])):
                assert iz + z < mz and iy + y < my and ix + x < mx, "Could not load zone, map bounds exceeded"
                # NOTE z-coords are always "inverted" here relative to JSON indices
                map_z = 2 * len(zone) - iz + z - mz
                tile_map[map_z][iy + y][ix + x] = zone[iz][iy][ix]


def bounds(area):
    return len(area), longest_in_list(area, 1), longest_in_list(area, 2)


def clamp(a, left, right):
    """
    Returns a clamped between l and r
    """
    assert left <= right, "Left was not <= Right when calling clamp(a, left, right)"
    return max(left, min(a, right))


def sgn(val):
    return (0 < val) - (val < 0)


if __name__ == '__main__':
    main()
