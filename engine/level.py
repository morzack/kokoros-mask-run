from .state import State
from .map import Map
from .kokoro import Kokoro
from .utils import make_new_transparent_surface
from .ui import render_text

import pygame

import json
import random

class Level(State):
    def __init__(self, level_name):
        """
        initialize the level given a number to pull from
        """
        super().__init__()
        self.name = level_name
        
        # load config stuff
        self.level_dir = f"gamedata/levels/{self.name}"

        with open(f"{self.level_dir}/configuration.json", 'r') as f:
            self.level_config_data = json.load(f)

        with open(f"gamedata/gameconfig.json", 'r') as f:
            self.game_config_data = json.load(f)

        # load assets
        self.background = pygame.image.load(f"{self.level_dir}/background.png")
        self.background = pygame.transform.scale(self.background, (self.game_config_data["width"], self.game_config_data["height"]))

        # load map parts into memory
        self.map_part_dirs = self.level_config_data["map_parts"]

        self.current_map_offset = 0

        self.map_previous = None
        self.map_current = None
        self.map_next = Map(f"{random.choice(self.map_part_dirs)}/config.json", self.current_map_offset)
        self.cycle_map()
        self.cycle_map()

        self.player = Kokoro()

        self.player.x += self.map_previous.width

        self.score = 0

    def cycle_map(self):
        self.map_previous = self.map_current
        self.map_current = self.map_next
        self.current_map_offset += self.map_current.width
        self.map_next = Map(f"{random.choice(self.map_part_dirs)}/config.json", self.current_map_offset)

    def process_event(self, event : pygame.event.EventType):
        """
        process an event as needed. tl;dr keypresses and stuff
        """
        pass

    def draw_map(self, mapIn : Map, surface : pygame.Surface):
        scrollingSurface = make_new_transparent_surface(surface)
        offset_x = -(self.player.x-self.player.x%2) + scrollingSurface.get_width()/2
        offset_y = -self.player.y  + scrollingSurface.get_height()/2
        # offset_x = -self.player.x
        # offset_y = -self.player.y
        mapIn.draw_background(scrollingSurface, offset_x, offset_y)
        mapIn.draw_platforms(scrollingSurface, offset_x, offset_y)
        mapIn.draw_foreground(scrollingSurface, offset_x, offset_y)
        mapIn.draw_masks(scrollingSurface, offset_x, offset_y)
        return scrollingSurface

    def update(self, surface : pygame.Surface, keys_pressed, current_time):
        """
        update the level and components or whatever
        """
        if self.player.x > self.current_map_offset:
            self.cycle_map()

        # the things here are on a surface that should move with the player, ie objects in the world
        previous_surface = self.draw_map(self.map_previous, surface)
        current_surface = self.draw_map(self.map_current, surface)
        next_surface = self.draw_map(self.map_next, surface)

        # the things here remain in the same place on the screen at all times
        staticSurface = make_new_transparent_surface(surface)
        self.player.draw_to_surface(staticSurface)
        self.player.update(keys_pressed)
        
        # combine the previously created surfaces
        surface.blit(self.background, (0, 0))
        surface.blit(previous_surface, (0, 0))
        surface.blit(current_surface, (0, 0))
        surface.blit(next_surface, (0, 0))
        surface.blit(staticSurface, (0, 0))

        player_colliders = [self.player.get_left_collider(), self.player.get_right_collider(), self.player.get_top_collider(), self.player.get_bottom_collider()]
        player_map_collisions = self.map_current.check_collisions(player_colliders)
        self.player.hit_left, self.player.hit_right, self.player.hit_top, self.player.grounded = player_map_collisions

        self.score += self.map_current.check_mask_collisions(self.player.get_bounding_box())

        # here's that debug gore statement
        render_text(surface, 0, 0, f"x: {self.player.x} | mapbnd: {self.current_map_offset} | scr: {self.score}", pygame.Color(255, 0, 0))