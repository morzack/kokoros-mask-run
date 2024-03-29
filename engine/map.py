import pygame

from os import listdir
from os.path import isfile, join

from .mask import Mask
from .powerup import Powerup
from .enemy import Enemy

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

def array_to_tiles(array, w, h, tilepath, x_off):
    # make sure to use this lol:
    # https://ezgif.com/sprite-cutter/
    # god tier resource
    tiles = []
    i = 0
    for y in array:
        j = 0
        for x in y:
            if x != -1:
                tiles.append(Tile(f"{tilepath}/tile{str(x).zfill(3)}.png", j*w+x_off, i*h, w, h))
            j += 1
        i += 1
    return tiles

def array_to_masks(mask_array, x_off):
    with open(f"gamedata/masks.json", 'r') as f:
        mask_data = json.load(f)

    masks = []
    i = 0
    for y in mask_array:
        j = 0
        for x in y:
            if x != -1:
                masks.append(Mask(mask_data["width"]*j+x_off, mask_data["height"]*i))
            j+=1
        i+=1
    return masks

def array_to_powerups(powerup_array, x_off):
    with open(f"gamedata/powerups.json", 'r') as f:
        powerup_data = json.load(f)

    powerups = []
    i = 0
    for y in powerup_array:
        j = 0
        for x in map(str, y):
            if x in powerup_data["powerupids"]:
                powerups.append(Powerup(powerup_data["powerupConfig"]["width"]*j+x_off, powerup_data["powerupConfig"]["width"]*i, powerup_data["powerupids"][x]))
            j+=1
        i+=1
    return powerups

def array_to_enemies(enemy_array, x_off):
    with open(f"gamedata/enemies/config.json", 'r') as f:
        enemy_data = json.load(f)

    w = enemy_data["width"]
    h = enemy_data["height"]

    enemies = []
    i = 0
    for y in enemy_array:
        j = 0
        for x in map(str, y):
            if x in enemy_data["enemyids"]:
                enemies.append(Enemy(x, w*j+x_off, h*i))
            j+=1
        i+=1
    return enemies

def draw_tiles(tiles, surface : pygame.Surface, x_offset, y_offset):
    for t in tiles:
        surface.blit(t.image, (t.x+x_offset, t.y+y_offset))

class Tile:
    def __init__(self, imagepath, pos_x, pos_y, width, height):
        self.image = pygame.image.load(imagepath).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.x = pos_x
        self.y = pos_y
        self.w = width
        self.h = height
        self.bounding_box = pygame.Rect(self.x, self.y, self.w, self.h)

    def get_position(self):
        return [self.x, self.y]

class Map:
    def __init__(self, level_config_file, data_dir, x_offset, end=False):
        self.end = end
        
        with open(level_config_file, 'r') as f:
            self.config_data = json.load(f)
        
        self.tileatlas = self.config_data["tileatlas"]

        foreground_data = csv_to_array(f"{data_dir}/_Objects.csv")
        platform_data = csv_to_array(f"{data_dir}/_Platforms.csv")
        background_data = csv_to_array(f"{data_dir}/_Background.csv")

        w = self.config_data["tilew"]
        h = self.config_data["tileh"]
        self.foreground = array_to_tiles(foreground_data, w, h, self.tileatlas, x_offset)
        self.platforms = array_to_tiles(platform_data, w, h, self.tileatlas, x_offset)
        self.background = array_to_tiles(background_data, w, h, self.tileatlas, x_offset)

        mask_data = csv_to_array(f"{data_dir}/_Masks.csv")
        self.masks = array_to_masks(mask_data, x_offset)

        powerup_data = csv_to_array(f"{data_dir}/_Powerups.csv")
        self.powerups = array_to_powerups(powerup_data, x_offset)

        enemy_data = csv_to_array(f"{data_dir}/_Enemies.csv")
        self.enemies = array_to_enemies(enemy_data, x_offset)

        self.width = len(foreground_data[0])*w
        self.height = len(foreground_data)*h

        self.x = x_offset

    def draw_foreground(self, surf : pygame.Surface, x_off, y_off):
        draw_tiles(self.foreground, surf, x_off, y_off)

    def draw_platforms(self, surf : pygame.Surface, x_off, y_off):
        draw_tiles(self.platforms, surf, x_off, y_off)

    def draw_background(self, surf : pygame.Surface, x_off, y_off):
        draw_tiles(self.background, surf, x_off, y_off)
    
    def draw_masks(self, surf : pygame.Surface, x_off, y_off, active):
        if active:
            for mask in self.masks:
                mask.draw_to_surface(surf, x_off, y_off)
        for powerup in self.powerups:
            powerup.draw_to_surface(surf, x_off, y_off)
        for enemy in self.enemies:
            enemy.draw_to_surface(surf, x_off, y_off)

    def check_collisions(self, othercolliders):
        collisions = [False for i in othercolliders]
        j = 0
        for collider in othercolliders:
            for platform in self.platforms:
                if platform.bounding_box.colliderect(collider):
                    collisions[j] = True
                    break
            j+=1
        return collisions

    def check_mask_collisions(self, collider):
        num_masks_hit = 0
        for mask in [x for x in self.masks if x.active]:
            if mask.get_bounding_box().colliderect(collider):
                num_masks_hit += 1
                mask.active = False
        return num_masks_hit

    def check_powerup_collisions(self, collider):
        powerups_hit = []
        for powerup in [x for x in self.powerups if x.active]:
            if powerup.get_bounding_box().colliderect(collider):
                powerups_hit.append(powerup)
                powerup.active = False
        return powerups_hit
    
    def check_enemy_collisions(self, collider):
        for enemy in self.enemies:
            if enemy.get_bounding_box().colliderect(collider):
                return True
        return False