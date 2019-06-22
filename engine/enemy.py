import pygame

import json
import random

class Enemy:
    def __init__(self, enemytype, x, y):
        with open(f"gamedata/enemies/config.json", 'r') as f:
            all_enemy_data = json.load(f)

        self.image_dir = all_enemy_data[enemytype]

        self.image = pygame.image.load(self.image_dir).convert_alpha()
        self.image = pygame.transform.scale(self.image, (all_enemy_data["width"], all_enemy_data["height"]))
        
        self.x = x
        self.y = y
        self.w = all_enemy_data["width"]
        self.h = all_enemy_data["height"]

    def get_bounding_box(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw_to_surface(self, surface : pygame.Surface, x_offset, y_offset):
        surface.blit(self.image, (self.x+x_offset, self.y+y_offset))