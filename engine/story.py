from .state import State

import pygame

import json

class Story(State):
    def __init__(self, story_config):
        """
        initialize the level given a number to pull from
        """
        super().__init__()

        with open(story_config, 'r') as f:
            self.config_data = json.load(f)

        self.images = []
        self.current_image = 0
        for i in range(self.config_data["image_count"]):
            self.images.append(pygame.image.load(f"{self.config_data['image_dir']}/{i}.png").convert())
        
        self.level_over = False

    def process_event(self, event : pygame.event.EventType):
        """
        process an event as needed. tl;dr keypresses and stuff
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RIGHT or event.key == pygame.K_RETURN:
                self.current_image += 1
            if event.key == pygame.K_LEFT:
                self.current_image -= 1
            
            if self.current_image < 0:
                self.current_image = 0
            
            if self.current_image >= len(self.images):
                self.current_image = len(self.images)-1
                self.level_over = True

    def update(self, surface : pygame.Surface, keys_pressed, current_time):
        """
        update the level and components or whatever
        """
        surface.blit(self.images[self.current_image], (0, 0))