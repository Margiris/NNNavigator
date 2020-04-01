import pygame, sys
from pygame.locals import *
# from pygame.locals import HWSURFACE, DOUBLEBUF, RESIZABLE, VIDEORESIZE
import tensorflow as tf

from _random import Random

from gameObjects import Goal, Player, Wall
from util import Color

WINDOW_DIMENSIONS = (800, 600)
MATRIX_DIMENSIONS = (80, 60)
MIN_OBJECT_DIMENSIONS = (
    WINDOW_DIMENSIONS[0] / MATRIX_DIMENSIONS[0],
    WINDOW_DIMENSIONS[1] / MATRIX_DIMENSIONS[1])
WALL_COUNT = 500

pygame.init()

screen = pygame.display.set_mode(
    WINDOW_DIMENSIONS, HWSURFACE | DOUBLEBUF | RESIZABLE)
pygame.display.set_caption("NNNavigator")
clock = pygame.time.Clock()


gameObjects = []

wallCount = 500

for _ in range(wallCount):
    wall = Wall(Color.WHITE)
    wall.get_random(MATRIX_DIMENSIONS, wallCount / 50)
    gameObjects.append(wall)

player = Player(Color.GREEN)
player.place_at_random_coords(MATRIX_DIMENSIONS)
gameObjects.append(player)

goal = Goal(Color.RED)
goal.place_at_random_coords(WINDOW_DIMENSIONS)
gameObjects.append(goal)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == VIDEORESIZE:
            screen = pygame.display.set_mode(
                event.dict['size'], HWSURFACE | DOUBLEBUF | RESIZABLE)
            # screen.blit(pygame.transform.scale(pic,event.dict['size']),(0,0))

            WINDOW_DIMENSIONS = screen.get_size()
            MIN_OBJECT_DIMENSIONS = (
                WINDOW_DIMENSIONS[0] / MATRIX_DIMENSIONS[0],
                WINDOW_DIMENSIONS[1] / MATRIX_DIMENSIONS[1])
            print(MIN_OBJECT_DIMENSIONS)
            pygame.display.flip()
            for obj in gameObjects:
                obj.width = MIN_OBJECT_DIMENSIONS[0]
                obj.height = MIN_OBJECT_DIMENSIONS[1]

    for key in pygame.key.get_pressed():
        if key == pygame.K_LEFT:
            print()
        if key == pygame.K_RIGHT:
            print()

    screen.fill((0, 0, 0))

    pygame.display.update()
    clock.tick(10)

pygame.quit()
sys.exit()
