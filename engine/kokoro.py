# hata no kokoro to be technical but whatever

import pygame

import json

from .utils import clamp

class Kokoro:
    def __init__(self):
        with open(f"gamedata/player/playerconfig.json", 'r') as f:
            self.player_config_data = json.load(f)

        self.x = 0
        self.y = 0

        self.dx = 0
        self.dy = 0

        self.facing_right = True

        self.image = pygame.image.load(self.player_config_data["image"])
        self.image = pygame.transform.scale(self.image, (self.player_config_data["width"], self.player_config_data["height"]))

    def draw_to_surface(self, surface : pygame.Surface):
        # TODO this should be updated when animations are a thing because those are useful/important
        # surface.blit(self.image, (self.x, self.y)) # don't want this because kokoro should stay in the center
        i = self.image
        if self.facing_right:
            i = pygame.transform.flip(i, True, False)
        surface.blit(i, (surface.get_width()/2, surface.get_height()/2))

    def get_bounding_box(self):
        return pygame.Rect(self.x, self.y, self.player_config_data["width"], self.player_config_data["height"])

    def update(self, keys_pressed):
        # update the position and stuff
        if keys_pressed["left"]:
            self.dx -= self.player_config_data["lateralacceleration"]
        if keys_pressed["right"]:
            self.dx += self.player_config_data["lateralacceleration"]

        self.dx *= self.player_config_data["friction"]
        
        # clamp speed in a shitty way because why not
        m_speed = self.player_config_data["maxlateralspeed"]
        self.dx = clamp(self.dx, -m_speed, m_speed)
        m_speed = self.player_config_data["maxverticalspeed"]
        self.dy = clamp(self.dy, -m_speed, m_speed)

        if self.dx < -0.1:
            self.facing_right = False
        if self.dx > 0.1:
            self.facing_right = True

        self.x += self.dx
        self.y += self.dy