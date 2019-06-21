import pygame

import json
import random

class Mask:
    def __init__(self, x, y):
        with open(f"gamedata/masks.json", 'r') as f:
            all_mask_data = json.load(f)

        self.mask_type, self.image_path = random.choice(list(all_mask_data["types"].items()))

        self.image = pygame.image.load(self.image_path)
        self.image = pygame.transform.scale(self.image, (all_mask_data["width"], all_mask_data["height"]))
        
        self.x = x
        self.y = y
        self.w = all_mask_data["width"]
        self.h = all_mask_data["height"]

        self.active = True

    def get_bounding_box(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw_to_surface(self, surface : pygame.Surface, x_offset, y_offset):
        if self.active:
            surface.blit(self.image, (self.x+x_offset, self.y+y_offset))