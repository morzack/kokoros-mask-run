import pygame

import json
import random

class Powerup:
    def __init__(self, x, y, name):
        with open(f"gamedata/powerups.json", 'r') as f:
            config = json.load(f)

        powerup_config = [i for i in config["powerups"] if i["name"] == name][0]
    
        self.image = pygame.image.load(powerup_config["image"]).convert_alpha()
        self.image = pygame.transform.scale(self.image, (config["powerupConfig"]["width"], config["powerupConfig"]["height"]))

        self.duration = powerup_config["duration"]
        self.effect = powerup_config["effect"]

        self.x = x
        self.y = y
        self.w = config["powerupConfig"]["width"]
        self.h = config["powerupConfig"]["height"]

        self.active = True

    def get_bounding_box(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw_to_surface(self, surface : pygame.Surface, x_offset, y_offset):
        if self.active:
            surface.blit(self.image, (self.x+x_offset, self.y+y_offset))