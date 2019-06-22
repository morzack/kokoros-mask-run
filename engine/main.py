import pygame

import json

from .userinput import get_input
from .level import Level
from .ui import render_text
from .menu import Menu

def main():
    pygame.init()

    game_config_file = f"gamedata/gameconfig.json"

    with open(game_config_file, 'r') as f:
        game_config_data = json.load(f)

    screen = pygame.display.set_mode((game_config_data["width"], game_config_data["height"]))
    pygame.display.set_caption(game_config_data["title"])

    clock = pygame.time.Clock()

    frame = 0

    test_level = Menu("title") # Level("testlevel")

    running = True
    while running:
        for event in pygame.event.get():
            test_level.process_event(event)
            
        keys_pressed = get_input()

        if keys_pressed["quit"]:
            running = False

        test_level.update(screen, keys_pressed, frame)

        pygame.event.pump()
        clock.tick(game_config_data["targetFPS"])
        frame += 1
        
        render_text(screen, 600, 10, f"FPS: {int(clock.get_fps())}", pygame.Color(0, 255, 0))

        pygame.display.flip()