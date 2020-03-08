import pygame
import tensorflow as tf

from _random import Random

from gameObjects import Player, Wall
from util import Color

MAIN_WINDOW_DIMENSIONS = (800, 600)
WALL_COUNT = 500

pygame.init()

window_main = pygame.display.set_mode(MAIN_WINDOW_DIMENSIONS)
pygame.display.set_caption("NNNavigator")
clock = pygame.time.Clock()


gameObjects = []

wallCount = 500

for _ in range(wallCount):
    wall = Wall(0, 0, 1, 1, Color.WHITE)
    wall.get_random(MAIN_WINDOW_DIMENSIONS, (10, 10), wallCount / 10)
    gameObjects.append(wall)

player = Player(250, 250, 10, 10, Color.GREEN)
player.place_at_random_coords(MAIN_WINDOW_DIMENSIONS)
gameObjects.append(player)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for key in pygame.key.get_pressed():
        if key == pygame.K_LEFT:
            print()
        if key == pygame.K_RIGHT:
            print()

    window_main.fill((0, 0, 0))
    [pygame.draw.rect(window_main, obj.color, obj.rect())
     for obj in gameObjects]
    pygame.display.update()
    clock.tick(10)

pygame.quit()
