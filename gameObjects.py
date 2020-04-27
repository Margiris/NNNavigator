import pygame
import random
from settings import Settings


class GameObject(pygame.sprite.Sprite):
    def __init__(self, all_sprites, surface, color, coords, size, isMoveable):
        self.groups = all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.surface = surface
        self.image = pygame.Surface((size[0] * self.surface.tile_size[0],
                                     size[1] * self.surface.tile_size[1]))
        self.x, self.y = coords
        self.width, self.height = size
        self.color = color
        self.image.fill(self.color)
        self.rect = self.image.get_rect()

        self.isMoveable = isMoveable
        self.move_ticker = 0

    def update(self):
        self.move_ticker += 1
        self.rect.x = self.x * self.surface.tile_size[0]
        self.rect.y = self.y * self.surface.tile_size[1]

    def draw(self):
        pass

    def place_at_random_coords(self, x_max, y_max, x_min=0, y_min=0):
        self.x = random.randint(x_min, x_max - self.width)
        self.y = random.randint(y_min, y_max - self.height)

    def move(self, dx=0, dy=0):
        if self.isMoveable and self.move_ticker > Settings.FRAMES_PER_MOVE:
            self.move_ticker = 0
            if 0 <= self.x + dx < Settings.TILE_COUNT[0]:
                self.x += dx
            if 0 <= self.y + dy < Settings.TILE_COUNT[1]:
                self.y += dy

    def to_string(self):
        return str(self.rect) + " " + str(self.color)


class Goal(GameObject):
    def __init__(self, all_sprites, surface, color, coords, size=(1, 1)):
        super().__init__(all_sprites, surface, color, coords, size, False)


class Player(GameObject):
    def __init__(self, all_sprites, surface, color, coords, size=(1, 1)):
        super().__init__(all_sprites, surface, color, coords, size, True)
        self.is_alive = False


class Wall(GameObject):
    def __init__(self, all_sprites, surface, color, coords, size, isMoveable):
        super().__init__(all_sprites, surface, color, coords, size, isMoveable)

    def get_random(self, x_max, y_max, tile_count=1):
        self.width = random.randint(1, x_max)
        self.height = random.randint(1, y_max)

        if self.height > self.width:
            self.width = 1
        else:
            self.height = 1

        self.place_at_random_coords(x_max, y_max)
