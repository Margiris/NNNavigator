import pygame
from _random import Random

from gameObject import GameObject
from player import Player

MAIN_WINDOW_DIMENSIONS = (800, 450)
WALL_COUNT = 500

pygame.init()

window_main = pygame.display.set_mode(MAIN_WINDOW_DIMENSIONS)
pygame.display.set_caption("NNNavigator")

clock = pygame.time.Clock()

player = Player(250, 250, sprite_filename="red_dot.png")
walls = [GameObject(x) for x in list()]

while True:

    # all_events
    print(clock.get_fps())
    clock.tick(10)
