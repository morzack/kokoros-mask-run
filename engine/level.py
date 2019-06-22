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
        self.background = pygame.image.load(f"{self.level_dir}/background.png").convert()
        self.background = pygame.transform.scale(self.background, (self.game_config_data["width"], self.game_config_data["height"]))

        self.background = pygame.image.load(f"{self.level_config_data['background']}").convert()
        bg_height = self.background.get_height()
        scale_up_ratio = self.game_config_data["height"]/bg_height
        self.background = pygame.transform.scale(self.background, (int(self.background.get_width()*scale_up_ratio), int(self.background.get_height()*scale_up_ratio)))

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

        self.mask_goal = self.game_config_data["maskgoal"]

        self.level_over = False

        self.cam_x = self.player.x

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

    def calc_x_offset(self):
        return -(self.cam_x-self.cam_x%2)

    def draw_map_back(self, mapIn : Map, surface : pygame.Surface):
        offset_x = self.calc_x_offset() + surface.get_width()/2
        offset_y = -self.player.y  + surface.get_height()/2
        # offset_x = -self.player.x
        # offset_y = -self.player.y
        mapIn.draw_background(surface, offset_x, offset_y)
        mapIn.draw_platforms(surface, offset_x, offset_y)
        # mapIn.draw_foreground(surface, offset_x, offset_y)
        mapIn.draw_masks(surface, offset_x, offset_y)
    
    def draw_map_front(self, mapIn : Map, surface : pygame.Surface):
        offset_x = self.calc_x_offset() + surface.get_width()/2
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
        self.player.draw_to_surface(staticSurface, current_time, self.cam_x-self.player.x)
        self.player.update(keys_pressed)

        self.score_mask.draw_to_surface(staticSurface, 0, 0)
        
        # combine the previously created surfaces
        scaled_player_x = self.cam_x * self.level_config_data["scrollratio"]
        scaled_player_x = scaled_player_x % self.background.get_width()
        surface.blit(self.background, (-scaled_player_x, 0))
        surface.blit(self.background, (-scaled_player_x+self.background.get_width(), 0))

        self.draw_map_back(self.map_previous, surface)
        self.draw_map_back(self.map_current, surface)
        self.draw_map_back(self.map_next, surface)

        surface.blit(staticSurface, (0, 0))

        self.draw_map_front(self.map_previous, surface)
        self.draw_map_front(self.map_current, surface)
        self.draw_map_front(self.map_next, surface)

        render_text(surface, self.score_mask.x+self.score_mask.w, self.game_config_data["scoreTextOffsetY"], f"{self.score} / {self.mask_goal}", pygame.Color(255, 255, 255))

        player_colliders = [self.player.get_left_collider(), self.player.get_right_collider(), self.player.get_top_collider(), self.player.get_bottom_collider()]
        player_map_collisions_current = self.map_current.check_collisions(player_colliders)
        player_map_collisions_next = self.map_next.check_collisions(player_colliders)
        player_map_collisions_prev = self.map_previous.check_collisions(player_colliders)
        self.player.hit_left = player_map_collisions_current[0] or player_map_collisions_next[0] or player_map_collisions_prev[0]
        self.player.hit_right = player_map_collisions_current[1] or player_map_collisions_next[1] or player_map_collisions_prev[1]
        self.player.hit_top = player_map_collisions_current[2] or player_map_collisions_next[2] or player_map_collisions_prev[2]
        self.player.grounded = player_map_collisions_current[3] or player_map_collisions_next[3] or player_map_collisions_prev[3]

        self.score += self.map_current.check_mask_collisions(self.player.get_bounding_box())

        powerups_hit = self.map_current.check_powerup_collisions(self.player.get_bounding_box())
        [self.player.apply_powerup(p) for p in powerups_hit]

        if self.map_current.check_enemy_collisions(self.player.get_bounding_box()):
            self.level_over = True

        if self.player.y > self.map_current.height:
            self.level_over = True

        completion_percent = self.score/self.mask_goal
        if completion_percent >= 1:
            # yay, you won. good job.
            pass

        self.cam_x = max(self.cam_x, self.player.x)

        self.player.hit_edge = self.cam_x-self.player.x > surface.get_width()/2

        # here's that debug gore statement
        render_text(surface, 0, 50, f"col: {player_map_collisions_current}", pygame.Color(255, 0, 0))