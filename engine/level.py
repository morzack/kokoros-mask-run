from .state import State
from .map import Map
from .kokoro import Kokoro
from .utils import make_new_transparent_surface
from .ui import render_text
from .mask import Mask

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
        self.level_config_file = f"{self.level_dir}/configuration.json"

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

        self.get_random_map = lambda: Map(self.level_config_file, random.choice(self.map_part_dirs), self.current_map_offset)

        self.map_previous = None
        self.map_current = None
        self.map_next = self.get_random_map()
        self.cycle_map()
        self.cycle_map()

        self.player = Kokoro()

        self.player.x += self.map_previous.width

        self.score = 0
        self.score_mask = Mask(self.game_config_data["scoreX"], self.game_config_data["scoreY"])

    def cycle_map(self):
        self.map_previous = self.map_current
        self.map_current = self.map_next
        self.current_map_offset += self.map_current.width
        self.map_next = self.get_random_map()

    def process_event(self, event : pygame.event.EventType):
        """
        process an event as needed. tl;dr keypresses and stuff
        """
        pass

    def draw_map_back(self, mapIn : Map, surface : pygame.Surface):
        offset_x = -(self.player.x-self.player.x%2) + surface.get_width()/2
        offset_y = -self.player.y  + surface.get_height()/2
        # offset_x = -self.player.x
        # offset_y = -self.player.y
        mapIn.draw_background(surface, offset_x, offset_y)
        mapIn.draw_platforms(surface, offset_x, offset_y)
        # mapIn.draw_foreground(surface, offset_x, offset_y)
        mapIn.draw_masks(surface, offset_x, offset_y)
    
    def draw_map_front(self, mapIn : Map, surface : pygame.Surface):
        offset_x = -(self.player.x-self.player.x%2) + surface.get_width()/2
        offset_y = -self.player.y  + surface.get_height()/2
        # offset_x = -self.player.x
        # offset_y = -self.player.y
        # mapIn.draw_background(scrollingSurface, offset_x, offset_y)
        # mapIn.draw_platforms(scrollingSurface, offset_x, offset_y)
        mapIn.draw_foreground(surface, offset_x, offset_y)
        # mapIn.draw_masks(scrollingSurface, offset_x, offset_y)
        

    def update(self, surface : pygame.Surface, keys_pressed, current_time):
        """
        update the level and components or whatever
        """
        if self.player.x > self.current_map_offset:
            self.cycle_map()
        
        # the things here remain in the same place on the screen at all times
        staticSurface = make_new_transparent_surface(surface)
        self.player.draw_to_surface(staticSurface)
        self.player.update(keys_pressed)

        self.score_mask.draw_to_surface(staticSurface, 0, 0)
        
        # combine the previously created surfaces
        surface.blit(self.background, (0, 0))

        self.draw_map_back(self.map_previous, surface)
        self.draw_map_back(self.map_current, surface)
        self.draw_map_back(self.map_next, surface)

        surface.blit(staticSurface, (0, 0))

        self.draw_map_front(self.map_previous, surface)
        self.draw_map_front(self.map_current, surface)
        self.draw_map_front(self.map_next, surface)

        render_text(surface, self.score_mask.x+self.score_mask.w, self.game_config_data["scoreTextOffsetY"], f"{self.score}", pygame.Color(255, 0, 0))

        player_colliders = [self.player.get_left_collider(), self.player.get_right_collider(), self.player.get_top_collider(), self.player.get_bottom_collider()]
        player_map_collisions_current = self.map_current.check_collisions(player_colliders)
        player_map_collisions_next = self.map_next.check_collisions(player_colliders)
        self.player.hit_left = player_map_collisions_current[0] or player_map_collisions_next[0]
        self.player.hit_right = player_map_collisions_current[1] or player_map_collisions_next[1]
        self.player.hit_top = player_map_collisions_current[2] or player_map_collisions_next[2]
        self.player.grounded = player_map_collisions_current[3] or player_map_collisions_next[3]

        self.score += self.map_current.check_mask_collisions(self.player.get_bounding_box())

        # here's that debug gore statement
        # render_text(surface, 0, 50, f"col: {1}", pygame.Color(255, 0, 0))