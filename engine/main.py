import pygame

import json

from .userinput import get_input
from .level import Level
from .menu import Menu

def main():

    pygame.init()

    game_config_file = f"gamedata/gameconfig.json"

    with open(game_config_file, 'r') as f:
        game_config_data = json.load(f)

    screen = pygame.display.set_mode((game_config_data["width"], game_config_data["height"]))
    pygame.display.set_caption(game_config_data["title"])
    pygame.display.set_icon(pygame.image.load(game_config_data["icon"]).convert())

    clock = pygame.time.Clock()

    try:
        pygame.mixer.music.load(game_config_data["bgm"])
        pygame.mixer.music.play()
    except:
        print("If you're using Linux audio -- best of luck.")
        print("Something's up with the audio right now.")

    frame = 0

    test_level = Menu("title")

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
        
        pygame.display.flip()