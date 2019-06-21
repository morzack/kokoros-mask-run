import pygame

import json

def get_font_config():
    with open(f"gamedata/gameconfig.json") as f:
        data = json.load(f)

    font = pygame.font.match_font(data["fontname"])
    if font == None:
        return

    return pygame.font.Font(font, data["fontsize"])

def render_text(surface : pygame.Surface, x, y, text, color : pygame.Color):
    font = get_font_config()
    surface.blit(font.render(text, True, color), (x, y))