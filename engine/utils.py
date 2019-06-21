import math

from pygame import Surface, SRCALPHA

def clamp(i, mi, ma):
    return min(max(i, mi), ma)

def make_new_transparent_surface(surf : Surface):
    """
    make a new transparent surface with the same size as the passed in one
    """
    surf = Surface((surf.get_width(), surf.get_height()), SRCALPHA, 32)
    surf = surf.convert_alpha()
    return surf