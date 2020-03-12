from bearlibterminal import terminal
from random import randrange
from math import ceil
import codecs
from IO.json_parsers import load_json

FPS = 60
SPEED_CAP = 40
SPEED_ACCELERATION = 1
MAP_SIZE = 64
TILE_SIZE = 32
# in fractions of screen size
OFFSET_LENIENCY = 0


def main():
    terminal.open()

    terminal.set("output.vsync=true");
    terminal.set("window: title='Plasma Rain', resizeable=true, minimum-size=1x1")
    terminal.set("window: size=28x21; font: ../data/media/lucida.ttf, size=32x32")
    terminal.set("input.filter={keyboard+}") #Enable key-release events.
    terminal.composition(terminal.TK_ON)
    terminal.bkcolor(terminal.color_from_name("gray"))
    #grey (or gray), red, flame, orange, amber, yellow, lime, 
    #chartreuse, green, sea, turquoise, cyan, sky, azure, blue,
    #han, violet, purple, fuchsia, magenta, pink, crimson, transparent
    terminal.color(terminal.color_from_name("black"))    
    
    xspeed, yspeed, textoffset = (0,) * 3

    map_depth, map_length, map_width = 4, 60, 60
    #initialize blank map
    map = [[[" " for _ in range(map_width)] for _ in range(map_length)] for _ in range(map_depth)]
    
    zone = load_json('../data/placeholder/map.json', pickle = False)
    load_zone(zone, map, z = 1, y = 1)
    overlay = load_UTF('../data/placeholder/overlay.txt')

    proceed = True

    # map will only render to screen inside the display, generally set to not overlap with UI
    # map will only be scrollable between the offset bounds
    # coordinates are down-right = positive, "opposite" for the offset    
    #set offset_leniency to 1 and you will only be allowed to scroll 1 more tile than enough to see every tile
    #in general the coordinate system is z, y, x: depth, length, width. No height because it's ambiguous.
    screen_width, screen_length, display_min_y, display_max_y, display_min_x, display_max_x, \
    min_yoffset, max_yoffset, min_xoffset, max_xoffset, xoffset_leniency, yoffset_leniency  = (None,) * 12
    
    """
    Adjusts the bounds defined above, to be called when opening and resizing
    """
    def reset_bounds():
        #nonlocal allows modification of outer function's variables
        nonlocal screen_width, screen_length, display_min_y, display_max_y, display_min_x, display_max_x, \
        min_yoffset, max_yoffset, min_xoffset, max_xoffset
        
        screen_length = terminal.state(terminal.TK_HEIGHT) * terminal.state(terminal.TK_CELL_HEIGHT)
        screen_width = terminal.state(terminal.TK_WIDTH) * terminal.state(terminal.TK_CELL_WIDTH)
       
        yoffset_leniency = int(screen_length * OFFSET_LENIENCY / TILE_SIZE)
        xoffset_leniency = int(screen_length * OFFSET_LENIENCY / TILE_SIZE)

        display_min_y = 3*TILE_SIZE
        display_max_y = screen_length
        display_min_x = 0
        display_max_x = screen_width
        
        min_yoffset = min(0, screen_length - map_length*TILE_SIZE - yoffset_leniency*TILE_SIZE)
        max_yoffset = 0 + yoffset_leniency*TILE_SIZE + display_min_y
        min_xoffset = min(0, screen_width - map_width*TILE_SIZE - xoffset_leniency*TILE_SIZE)
        max_xoffset = 0 + xoffset_leniency*TILE_SIZE + display_min_x
        
    reset_bounds()
        
    yoffset, xoffset = display_min_y,display_min_x

    camera_height = 0
    show_roofs = True

    while proceed:
        #t = partial-tile offset in pixels
        #i = full-tile offset in tiles
        #c = number of tiles to render 
        ty = yoffset%TILE_SIZE
        tx = xoffset%TILE_SIZE   
        iy = yoffset//TILE_SIZE
        ix = xoffset//TILE_SIZE
        vc = screen_length//TILE_SIZE + 1
        hc = screen_width//TILE_SIZE + 1
        
        xoffset = clamp(xoffset + xspeed, min_xoffset, max_xoffset)
        yoffset = clamp(yoffset + yspeed, min_yoffset, max_yoffset)
        
        terminal.clear()

        terminal.print(2, 1, "speed: {}, {}".format(xspeed, yspeed))
        terminal.print(2, 2, "offset: {}, {}".format(ix, iy))
        
        higher_tile_already_rendered = [[False for _ in range(map_width)] for _ in range(map_length)]
        
        # print scrollable map
        for z in range(camera_height, -1, -1): # top has higher render priority
            for y in range(0, map_length):
                for x in range(0, map_width):
                    # s = offset in pixels
                    sx = (x + ix)*TILE_SIZE + tx
                    sy = (y + iy)*TILE_SIZE + ty
                    # render only on-screen tiles, giving a bit more leniency for x-axis since UI is top or bottom
                    if(display_min_y <= sy <= display_max_y 
                       and display_min_x- TILE_SIZE<= sx <= display_max_x + TILE_SIZE
                       and not higher_tile_already_rendered[y][x]
                       and map[z][y][x] not in ['', ' ']):
                        if z < camera_height:
                            terminal.put_ext(0, 0, sx, sy, 0x2588, (terminal.color_from_name('yellow'),terminal.color_from_name('red')) * 4)
                        terminal.put_ext(0, 0, sx, sy, map[z][y][x])
                        higher_tile_already_rendered[y][x] = True 
        
        #print overlay
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
                camera_height = clamp(camera_height + 1, 0, map_depth-1)
            elif key == terminal.TK_KP_MINUS:
                camera_height = clamp(camera_height - 1, 0, map_depth-1)
        if terminal.state(terminal.TK_LEFT):
            if xspeed < SPEED_CAP: 
                xspeed += SPEED_ACCELERATION
            else:
                xspeed = SPEED_CAP
        elif terminal.state(terminal.TK_RIGHT):
            if xspeed > -SPEED_CAP: 
                xspeed -= SPEED_ACCELERATION
            else:
                xspeed = -SPEED_CAP
        else: 
            xspeed -= sgn(xspeed)
        if terminal.state(terminal.TK_UP):
            if yspeed < SPEED_CAP: 
                yspeed += SPEED_ACCELERATION
            else:
                yspeed = SPEED_CAP
        elif terminal.state(terminal.TK_DOWN):
            if yspeed > -SPEED_CAP: 
                yspeed -= SPEED_ACCELERATION
            else:
                yspeed = -SPEED_CAP
        else:
            yspeed -= sgn(yspeed)
        terminal.delay(1000//FPS)

    terminal.close()
    
def prep(line):
    return line[0:-2] if line[-2:] == '\r\n' else line 

def load_UTF(path):
    """
    loads a UTF file into a string array, padding each line with spaces to the maximum length among other lines
    """
    with codecs.open(path, encoding='utf-8') as f:
        array = [prep(line) for line in f]
        length = longest_in_list(array, 1)
        return [pad_to_length(line, length) for line in array]
    
def pad_to_length(line, length):
    while len(line) != length:
        line += ' '
    return line

def pad_all(l, length):
    """
     Pads all strings in the list to the given length
     Accepts a list of any dimension, only modifying strings contained by any number of lists
    """
    for item in l:
        if isinstance(item, list):
            pad_all(item, length)
        elif isinstance(item, string) :
            pad_to_length(item, length)
    return l

def longest_in_list(l, k):
    """
     Takes an n-dimensional list and returns the length of the longest n-k dimenional list in it.
     If k == 0, the function is equivalent to len(l). If k == -1, it will return the lowest dimensional list.
    """
    if k == 0: 
        return len(l)
    length = 0
    base_case = k == 1 or (k == -1 and not isinstance(l[0], list))
    for list in l:
        new_length = len(list) if base_case else longest_in_list(list, k-1)
        length = max(length, new_length) 
    return length

# loads the given zone onto the given map with the given offset
# will throw an error if map bounds are exceeded in the process
# for now zone attributes will just be LEVEL-X, but in the future there may be optional UNIT, ATMOSPHERE, and COLLAPSE
# every character corresponds to exactly one tile, but units are different
# Tiles primary attributes are height and width. Width is not physically modelled, height is.
# Tiles are twice as high as long as in OpenXCOM, and always have a floor
# For purposes of movement, tiles are either half-raised or not, independent of height. Standing on half-raised raises your height by half.
# You can move up to half-raised at +1TU, up from half-raised to full-raised at 0 TU
# Autofall for 0 damage like OpenXCOM
def load_zone(zone, map, x = 0, y = 0, z = 0):
    #bounds for zone and map respectively
    #NOTE potentially low-performance
    mz, my, mx = bounds(map)
    for iz in range(0, len(zone)):
        for iy in range(0, len(zone[iz])):
            for ix in range(0, len(zone[iz][iy])):
                assert iz + z < mz and iy + y < my and ix + x < mx , "Could not load zone, map bounds exceeded"
                 #NOTE z-coords are always "inverted" here relative to JSON indices
                map_z = 2*len(zone)-iz + z - mz
                map[map_z][iy + y][ix + x] = zone[iz][iy][ix]
        
def bounds(area):
    return (len(area), longest_in_list(area, 1), longest_in_list(area,2))

def clamp(a, l, r):    
    """
    Returns a clamped between l and r
    """
    assert l <= r, "L was not <= R when calling clamp(a, l, r)"
    return max(l, min(a, r))

def sgn(val):
    return (0 < val) - (val < 0)
          
if __name__ == '__main__':
    main()