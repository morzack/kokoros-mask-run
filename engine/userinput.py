import pygame

def get_input():
    keys = pygame.key.get_pressed()
    return {
        "left" : keys[pygame.K_LEFT],
        "right" : keys[pygame.K_RIGHT],
        "up" : keys[pygame.K_UP] + keys[pygame.K_z],
        "down" : keys[pygame.K_DOWN],
        "enter" : keys[pygame.K_RETURN],
        "space" : keys[pygame.K_SPACE],
        "quit" : keys[pygame.K_q] + keys[pygame.K_ESCAPE]
    }