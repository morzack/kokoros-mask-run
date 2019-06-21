import pygame

from os import listdir
from os.path import isfile, join

import json

def csv_to_array(filepath):
    with open(filepath, 'r') as f:
        data = f.read()

    out = []
    for row in data.split('\n'):
        buf = []
        for col in row.split(","):
            try:
                buf.append(int(col))
            except ValueError:
                pass
        out.append(buf)

    return out

def array_to_tiles(array, w, h, tilepath):
    # make sure to use this lol:
    # https://ezgif.com/sprite-cutter/
    # god tier resource
    tiles = []
    i = 0
    for y in array:
        j = 0
        for x in y:
            if x != -1:
                tiles.append(Tile(f"{tilepath}/tile{str(x).zfill(3)}.png", j*w, i*h, w, h))
            j += 1
        i += 1
    return tiles

def draw_tiles(tiles, surface : pygame.Surface, x_offset, y_offset):
    for t in tiles:
        surface.blit(t.image, (t.x+x_offset, t.y+y_offset))

class Tile:
    def __init__(self, imagepath, pos_x, pos_y, width, height):
        self.image = pygame.image.load(imagepath)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.x = pos_x
        self.y = pos_y
        self.w = width
        self.h = height
        self.bounding_box = pygame.Rect(self.x, self.y, self.w, self.h)

    def get_position(self):
        return [self.x, self.y]

class Map:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self.config_data = json.load(f)
        
        self.tileatlas = self.config_data["tileatlas"]

        foreground_data = csv_to_array(self.config_data["foreground"])
        platform_data = csv_to_array(self.config_data["platforms"])
        background_data = csv_to_array(self.config_data["background"])

        w = self.config_data["tilew"]
        h = self.config_data["tileh"]
        self.foreground = array_to_tiles(foreground_data, w, h, self.tileatlas)
        self.platforms = array_to_tiles(platform_data, w, h, self.tileatlas)
        self.background = array_to_tiles(background_data, w, h, self.tileatlas)

    def draw_foreground(self, surf : pygame.Surface, x_off, y_off):
        draw_tiles(self.foreground, surf, x_off, y_off)

    def draw_platforms(self, surf : pygame.Surface, x_off, y_off):
        draw_tiles(self.platforms, surf, x_off, y_off)

    def draw_background(self, surf : pygame.Surface, x_off, y_off):
        draw_tiles(self.background, surf, x_off, y_off)