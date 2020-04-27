import pygame
import random
from settings import Settings


class GameObject(pygame.sprite.Sprite):
    def __init__(self, sprite_groups, tile_size, color, coords, size, is_moveable):
        self.groups = sprite_groups
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.tile_size = tile_size
        self.image = pygame.Surface((size[0] * self.tile_size[0],
                                     size[1] * self.tile_size[1]))
        self.x, self.y = coords
        self.width, self.height = size
        self.color = color
        self.image.fill(self.color)
        self.rect = self.image.get_rect()

        self.is_moveable = is_moveable
        self.move_ticker = 0

    def update(self):
        if self.is_moveable:
            self.move_ticker += 1
        self.rect.x = self.x * self.tile_size[0]
        self.rect.y = self.y * self.tile_size[1]

    def draw(self):
        pass

    def place_at_random_coords(self, x_max, y_max, x_min=0, y_min=0):
        self.x = random.randint(x_min, x_max - self.width)
        self.y = random.randint(y_min, y_max - self.height)

    def move(self, dx=0, dy=0):
        if self.is_moveable and self.move_ticker > Settings.FRAMES_PER_MOVE:
            self.move_ticker = 0
            if 0 <= self.x + dx < Settings.TILE_COUNT[0]:
                self.x += dx
            if 0 <= self.y + dy < Settings.TILE_COUNT[1]:
                self.y += dy

    def to_string(self):
        return str(self.rect) + " " + str(self.color)


class Goal(GameObject):
    def __init__(self, sprite_groups, tile_size, color, coords, size=(1, 1)):
        super().__init__(sprite_groups, tile_size, color, coords, size, False)


class Player(GameObject):
    def __init__(self, sprite_groups, tile_size, color, coords, size=(1, 1), walls=None):
        super().__init__(sprite_groups, tile_size, color, coords, size, True)
        self.is_alive = True
        self.walls = walls

    def move(self, dx=0, dy=0):
        if self.is_alive and not self.collides_with_wall(self.x + dx, self.y + dy):
            super().move(dx, dy)

    def collides_with_wall(self, x, y):
        for wall in self.walls:
            if wall.x == x and wall.y == y:
                return True
        return False


class Wall(GameObject):
    def __init__(self, sprite_groups, tile_size, color, coords, size=(1, 1), isMoveable=False):
        super().__init__(sprite_groups, tile_size, color, coords, size, isMoveable)

    def get_random(self, x_max, y_max, tile_count=1):
        self.width = random.randint(1, x_max)
        self.height = random.randint(1, y_max)

        if self.height > self.width:
            self.width = 1
        else:
            self.height = 1

        self.place_at_random_coords(x_max, y_max)
