import codecs
import os.path

from bearlibterminal import terminal

from IO.json_parsers import load_json
from IO.paths import mods_dir
from data.blueprint_objects import build_blueprints, Tile

FPS = 60
SPEED_CAP = 40
SPEED_ACCELERATION = 1
MAP_SIZE = 64
TILE_SIZE = 32
# in fractions of screen size
OFFSET_LENIENCY = 0
DO_NOT_RENDER = ['', ' ', False]
dir_path = os.path.dirname(__file__)

empty_tile = Tile()


def main():
    terminal.open()

    terminal.set("output.vsync=true")
    terminal.set("window: title='Plasma Rain', resizeable=true, minimum-size=16x12")
    terminal.set("window: size=28x21; font: " + os.path.join(dir_path, '../data/media/lucida.ttf') + ", size=32x32")
    terminal.set("input.filter={keyboard+}")  # Enable key-release events.
    terminal.composition(terminal.TK_ON)
    terminal.bkcolor(terminal.color_from_name("gray"))
    # grey (or gray), red, flame, orange, amber, yellow, lime,
    # chartreuse, green, sea, turquoise, cyan, sky, azure, blue,
    # han, violet, purple, fuchsia, magenta, pink, crimson, transparent
    terminal.color(terminal.color_from_name("black"))

    x_speed, y_speed, text_offset = (0,) * 3

    map_depth, map_length, map_width = 4, 60, 60
    # initialize blank tile_map
    tile_map: [[[Tile]]] = [[[empty_tile
                            for _ in range(map_width)]
                            for _ in range(map_length)]
                            for _ in range(map_depth)]
    print(mods_dir)
    blueprints = build_blueprints(load_json(os.path.join(mods_dir, "vanilla/blueprints/"), pickle=False))
    zone = load_zone(os.path.join(dir_path, '../data/placeholder/map2.json'), blueprints)
    paste_zone(zone, tile_map, z=1, y=1)
    overlay = load_utf(os.path.join(dir_path, '../data/placeholder/overlay.txt'))

    proceed = True

    # tile_map will only render to screen inside the display, generally set to not overlap with UI
    # tile_map will only be scrollable between the offset bounds
    # coordinates are down-right = positive, "opposite" for the offset    
    # set offset_leniency to 1 and you will only be allowed to scroll 1 more tile than enough to see every tile
    # in general the coordinate system is z, y, x: depth, length, width. No height because it's ambiguous.
    screen_width, screen_length, display_min_y, display_max_y, display_min_x, display_max_x, \
        min_y_offset, max_y_offset, min_x_offset, max_x_offset, x_offset_leniency, y_offset_leniency = (0,) * 12

    """
    Adjusts the bounds defined above, to be called when opening and resizing
    """

    def reset_bounds():
        # nonlocal allows modification of outer function's variables
        nonlocal screen_width, screen_length, display_min_y, display_max_y, display_min_x, display_max_x, \
            min_y_offset, max_y_offset, min_x_offset, max_x_offset, y_offset_leniency, x_offset_leniency

        screen_length = terminal.state(terminal.TK_HEIGHT) * terminal.state(terminal.TK_CELL_HEIGHT)
        screen_width = terminal.state(terminal.TK_WIDTH) * terminal.state(terminal.TK_CELL_WIDTH)

        y_offset_leniency = int(screen_length * OFFSET_LENIENCY / TILE_SIZE)
        x_offset_leniency = int(screen_length * OFFSET_LENIENCY / TILE_SIZE)

        display_min_y = 3 * TILE_SIZE
        display_max_y = screen_length
        display_min_x = 0
        display_max_x = screen_width

        min_y_offset = min(0, screen_length - map_length * TILE_SIZE - y_offset_leniency * TILE_SIZE)
        max_y_offset = 0 + y_offset_leniency * TILE_SIZE + display_min_y
        min_x_offset = min(0, screen_width - map_width * TILE_SIZE - x_offset_leniency * TILE_SIZE)
        max_x_offset = 0 + x_offset_leniency * TILE_SIZE + display_min_x

    reset_bounds()

    y_offset, x_offset = display_min_y, display_min_x

    camera_height = 0
    # TODO show_roofs = True

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

        x_offset = clamp(x_offset + x_speed, min_x_offset, max_x_offset)
        y_offset = clamp(y_offset + y_speed, min_y_offset, max_y_offset)

        terminal.clear()

        terminal.print(2, 1, "speed: {}, {}".format(x_speed, y_speed))
        terminal.print(2, 2, "offset: {}, {}".format(ix, iy))

        higher_tile_already_rendered: [[bool]] = [[False
                                                  for _ in range(map_width)]
                                                  for _ in range(map_length)]

        # print scrollable map
        for z in range(camera_height, -1, -1):  # top has higher render priority
            for y in range(0, map_length):
                for x in range(0, map_width):
                    # s = offset in pixels
                    sx = (x + ix) * TILE_SIZE + tx
                    sy = (y + iy) * TILE_SIZE + ty
                    # render only on-screen tiles, giving a bit more leniency for x-axis since UI is top or bottom
                    if (display_min_y <= sy <= display_max_y
                            and display_min_x - TILE_SIZE <= sx <= display_max_x + TILE_SIZE
                            and not higher_tile_already_rendered[y][x]
                            and tile_map[z][y][x] not in DO_NOT_RENDER):
                        assert higher_tile_already_rendered not in DO_NOT_RENDER
                        if z < camera_height and tile_map[z][y][x] != empty_tile:
                            terminal.put_ext(0, 0, sx, sy, 0x2588,
                                             (terminal.color_from_name('yellow'), terminal.color_from_name('red')) * 4)
                        terminal.put_ext(0, 0, sx, sy, tile_map[z][y][x].blueprint.icon)
                        higher_tile_already_rendered[y][x] = tile_map[z][y][x] != empty_tile

                        # print overlay
        i = 5
        for line in overlay:
            i += 1
            terminal.print(2, i, prep(line))

        terminal.refresh()

        while proceed and terminal.has_input():
            key = terminal.read()
            if key == terminal.TK_CLOSE or key == terminal.TK_ESCAPE:
                proceed = False
            elif key == terminal.TK_RESIZED:
                reset_bounds()
            elif key == terminal.TK_KP_PLUS:
                camera_height = clamp(camera_height + 1, 0, map_depth - 1)
            elif key == terminal.TK_KP_MINUS:
                camera_height = clamp(camera_height - 1, 0, map_depth - 1)
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
        terminal.delay(1000 // FPS)

    terminal.close()


def prep(line):
    return line[0:-2] if line[-2:] == '\r\n' else line


def load_utf(path):
    """
    loads a UTF file into a string array, padding each line with spaces to the maximum length among other lines
    """
    with codecs.open(path, encoding='utf-8') as f:
        array = [prep(line) for line in f]
        length = longest_in_list(array, 1)
        return [pad_to_length(line, length) for line in array]


def pad_to_length(x: str, length: int):
    while len(x) != length:
        x += ' '
    return x


def pad_all(x: list, length: int):
    """
     Pads all strings in the list to the given length
     Accepts a list of any dimension, only modifying strings contained by any number of lists
    """
    for item in x:
        if isinstance(item, list):
            pad_all(item, length)
        elif isinstance(item, str):
            pad_to_length(item, length)
    return x


def longest_in_list(x: list, k: int):
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
