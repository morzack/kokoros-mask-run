from .state import State
from .map import Map
from .kokoro import Kokoro
from .utils import make_new_transparent_surface
from .ui import render_text

import pygame

import json

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

        # load map
        self.map_config = f"{self.level_dir}/map/config.json"
        self.map = Map(self.map_config)

        self.player = Kokoro()

        self.score = 0

    def process_event(self, event : pygame.event.EventType):
        """
        process an event as needed. tl;dr keypresses and stuff
        """
        pass

    def update(self, surface : pygame.Surface, keys_pressed, current_time):
        """
        update the level and components or whatever
        """
        # the things here are on a surface that should move with the player, ie objects in the world
        scrollingSurface = make_new_transparent_surface(surface)
        offset_x = -self.player.x + scrollingSurface.get_width()/2
        offset_y = -self.player.y + scrollingSurface.get_height()/2
        self.map.draw_background(scrollingSurface, offset_x, offset_y)
        self.map.draw_platforms(scrollingSurface, offset_x, offset_y)
        self.map.draw_foreground(scrollingSurface, offset_x, offset_y)
        self.map.draw_masks(scrollingSurface, offset_x, offset_y)

        # the things here remain in the same place on the screen at all times
        staticSurface = make_new_transparent_surface(surface)
        self.player.draw_to_surface(staticSurface)
        self.player.update(keys_pressed)
        
        # combine the previously created surfaces
        surface.blit(self.background, (0, 0))
        surface.blit(scrollingSurface, (0, 0))
        surface.blit(staticSurface, (0, 0))

        player_colliders = [self.player.get_bounding_box()]
        player_map_collisions = self.map.check_collisions(player_colliders)
        self.player.grounded = player_map_collisions[0]

        self.score += self.map.check_mask_collisions(self.player.get_bounding_box())

        # here's that debug gore statement
        render_text(surface, 0, 0, f"gnd: {self.player.grounded} | scr: {self.score}", pygame.Color(255, 0, 0))