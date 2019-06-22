# hata no kokoro to be technical but whatever

import pygame

import json
import math

from .utils import clamp
from .powerup import Powerup

class Kokoro:
    def __init__(self):
        with open(f"gamedata/player/playerconfig.json", 'r') as f:
            self.player_config_data = json.load(f)

        self.x = 100
        self.y = 0

        self.dx = 0
        self.dy = 0

        self.facing_right = True

        self.image = pygame.image.load(self.player_config_data["image"]).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.player_config_data["width"], self.player_config_data["height"]))

        self.walking_frames = []
        for i in range(self.player_config_data["animations"]["walking"]):
            im = pygame.image.load(f"gamedata/player/animations/walking/{i}.png").convert_alpha()
            im = pygame.transform.scale(im, (self.player_config_data["width"], self.player_config_data["height"]))
            self.walking_frames.append(im)
        
        self.framerate = self.player_config_data["framerate"]
        self.last_frame = 0

        self.grounded = False
        self.hit_left = False
        self.hit_right = False
        self.hit_top = False

        self.currentEffects = {"speed":0}

    def draw_to_surface(self, surface : pygame.Surface, current_time):
        if abs(self.dx) > self.player_config_data["lateralacceleration"]:
            f = self.framerate

            if self.currentEffects["speed"] > 0:
                f /= 2
            if not self.grounded:
                f *= 3

            if current_time % f == 0:
                self.last_frame += 1
                if self.last_frame >= len(self.walking_frames):
                    self.last_frame = 0
            i = self.walking_frames[self.last_frame]
        else:
            i = self.image

        if not self.facing_right:
            i = pygame.transform.flip(i, True, False)
        surface.blit(i, (surface.get_width()/2, self.player_config_data["bottomoffset"]+surface.get_height()/2))
        # surface.blit(i, (self.x, self.y)) # don't want this because kokoro should stay in the center

    def get_bounding_box(self):
        return pygame.Rect(self.x, self.y, self.player_config_data["width"], self.player_config_data["height"])

    def get_left_collider(self):
        bb = self.get_bounding_box()
        bb.x -= self.player_config_data["collideroffset"]
        return bb
    
    def get_right_collider(self):
        bb = self.get_bounding_box()
        bb.x += self.player_config_data["collideroffset"]
        return bb

    def get_top_collider(self):
        bb = self.get_bounding_box()
        bb.y -= self.player_config_data["collideroffset"]
        return bb
    
    def get_bottom_collider(self):
        bb = self.get_bounding_box()
        bb.y += self.player_config_data["collideroffset"]
        return bb

    def apply_powerup(self, powerup : Powerup):
        self.currentEffects[powerup.effect] = powerup.duration

    def update(self, keys_pressed):
        # update powerups
        speed_modifier = 1 if self.currentEffects["speed"] <= 0 else 2

        for k in self.currentEffects:
            self.currentEffects[k] -= 1

        # update the position and stuff
        if keys_pressed["left"] and self.grounded:
            self.dx -= self.player_config_data["lateralacceleration"]*speed_modifier
        if keys_pressed["right"] and self.grounded:
            self.dx += self.player_config_data["lateralacceleration"]*speed_modifier

        # janky lol
        if not self.grounded:
            self.dy += self.player_config_data["gravity"]
        if self.grounded and self.dy > 0:
            self.dy = 0
        if self.grounded and keys_pressed["up"]:
            self.dy -= self.player_config_data["jumppower"]
        if self.hit_left and self.dx < 0:
            self.dx = 0
        if self.hit_right and self.dx > 0:
            self.dx = 0
        if self.hit_top and self.dy < 0:
            self.dy = 1

        if self.grounded:
            self.dx *= self.player_config_data["friction"]
        
        # clamp speed in a shitty way because why not
        m_speed = self.player_config_data["maxlateralspeed"]
        self.dx = clamp(self.dx, -m_speed, m_speed)
        m_speed = self.player_config_data["maxverticalspeed"]
        self.dy = clamp(self.dy, -m_speed, m_speed)

        if self.dx < -self.player_config_data["lateralacceleration"]:
            self.facing_right = False
        if self.dx > self.player_config_data["lateralacceleration"]:
            self.facing_right = True

        self.x += self.dx
        self.y += self.dy