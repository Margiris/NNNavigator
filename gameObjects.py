import pygame
import random
from settings import Settings


class GameObject(pygame.sprite.Sprite):
    def __init__(self, surface, coords, size, color):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.surface = surface
        self.x, self.y = coords
        self.width, self.height = size
        self.color = color

    @property
    def rect(self):
        return (self.x, self.y, self.width, self.height)

    @property
    def coords(self):
        return (self.x, self.y)

    def update(self):
        pass

    def draw(self):
        pass

    def place_at_random_coords(self, coord_max, coord_min=(0, 0)):
        self.x = random.randint(coord_min[0], coord_max[0] - self.width)
        self.y = random.randint(coord_min[1], coord_max[1] - self.height)

    def to_string(self):
        return str(self.x) + " " + str(self.y) + " " + str(self.width) + " " + str(self.height) + " " + str(self.color)


class Moveable:
    def __init__(self, max_vel):
        self.max_velocity = max_vel
        self.velocity = 0

    def move(self, direction):
        if self.velocity < self.max_velocity:
            self.accelerate()

    def accelerate(self):
        self.velocity += 2


class Goal(GameObject):
    def __init__(self, color, x=0, y=0, width=1, height=1):
        super().__init__(color, x, y, width, height)


class Player(GameObject, Moveable):
    def __init__(self, color, x=0, y=0, width=1, height=1):
        super().__init__(color, x, y, width, height)
        self.is_alive = False


class Wall(GameObject):
    def __init__(self, color, x=0, y=0, width=1, height=1):
        super().__init__(color, x, y, width, height)

    def get_random(self, coord_max, tile_count=1):
        self.width = random.randint(1, coord_max[0] / tile_count)
        self.height = random.randint(1, coord_max[1] / tile_count)

        if self.height > self.width:
            self.width = 10
        else:
            self.height = 10

        self.place_at_random_coords(coord_max)


class WallMoveable(Wall, Moveable):
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height, color)
