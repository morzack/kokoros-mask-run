import pygame

from .state import State
from .ui import render_text
from .level import Level

import json

class Menu(State):
    def __init__(self, menu_name):
        """
        initialize the given menu while pulling from a json thing to load stuff
        """
        super().__init__()
        self.file_dir = f"gamedata/menus.json"

        self.done = False

        with open(f"{self.file_dir}", 'r') as f:
            self.config_data = json.load(f)

        self.menu_config = self.config_data[menu_name]
        
        # load this as a level if this is the case
        self.islevel = "level" in self.menu_config["flags"]

        self.ismenu = "menu" in self.menu_config["flags"]

        self.isimage = "title_image" in self.menu_config["flags"]

        if self.ismenu:
            self.option_dict = self.menu_config["options"]
            self.options = list(self.option_dict.keys())
            self.selected_option = 0
        
        if "image_location" in self.menu_config:
            self.image = pygame.image.load(self.menu_config["image_location"]).convert()
        else:
            self.image = None

        self.next_menu = "" if not "next_menu" in self.menu_config else self.menu_config["next_menu"]
        self.next_state_active = False
        self.next_menu_object = Menu(self.next_menu) if self.next_menu != "" else None

        if self.islevel:
            self.level = Level(self.menu_config["name"])

            with open(f"gamedata/scoreconfig.json", 'r') as f:
                self.score_config = json.load(f)

    def process_event(self, event : pygame.event.EventType):
        if not self.next_state_active:
            if event.type == pygame.KEYDOWN:
                if self.ismenu:
                    if event.key == pygame.K_UP:
                        self.selected_option -= 1
                    if event.key == pygame.K_DOWN:
                        self.selected_option += 1

                    if self.selected_option < 0:
                        self.selected_option = len(self.options)-1
                    if self.selected_option >= len(self.options):
                        self.selected_option = 0
                    
                    if event.key == pygame.K_RETURN:
                        self.next_state_active = True
                        self.next_menu_object = Menu(self.option_dict[self.options[self.selected_option]])
                
                if self.isimage:
                    if event.key == pygame.K_RETURN:
                       self.next_state_active = True
        elif self.next_menu_object != None:
            self.next_menu_object.process_event(event)

    def get_next_done(self):
        if self.ismenu and self.next_state_active: # should be a level
            return self.next_menu_object.done
        else:
            return self.done

    def update(self, surface : pygame.Surface, keys_pressed, current_time):
        if not self.next_state_active:
            if self.image != None:
                surface.blit(self.image, (0, 0))
            if self.ismenu:
                current = 0
                y = self.menu_config["ypadding"]
                r, g, b = self.menu_config["textcolor"]
                text_color = pygame.Color(r, g, b)
                r, g, b = self.menu_config["boxcolor"]
                selected_color = pygame.Color(r, g, b)
                for option in self.options:
                    render_text(surface, self.menu_config["xpadding"], y, option, text_color if not current == self.selected_option else selected_color)
                    y += self.menu_config["textpadding"] + self.menu_config["textsize"]
                    current += 1
            if self.islevel:
                if not self.level.level_over:
                    self.level.update(surface, keys_pressed, current_time)
                else:
                    r, g, b = self.score_config["color"]
                    score_color = pygame.Color(r, g, b)
                    render_text(surface, self.score_config["xpaddingover"], self.score_config["ypaddingover"], "Game over", score_color)
                    render_text(surface, self.score_config["ypaddingscore"]+self.score_config["xpaddingover"], self.score_config["ypaddingscore"]+self.score_config["ypaddingover"], f"Your score: {self.level.score}", score_color)

                    if keys_pressed["enter"]:
                        self.done = True

        elif self.next_menu_object != None:
            self.next_menu_object.update(surface, keys_pressed, current_time)
        
        if self.get_next_done():
            self.next_state_active = False