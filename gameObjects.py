import pygame
from color import Color
from settings import Settings


class GameObject(pygame.sprite.Sprite):
    def __init__(self, sprite_groups, tile_size, color, coords, size, is_moveable=False, fpm=Settings.FRAMES_PER_MOVE):
        self.groups = sprite_groups
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.tile_size = tile_size
        self.image = pygame.Surface((size[0] * self.tile_size[0],
                                     size[1] * self.tile_size[1]))
        self.x, self.y = coords
        self.width, self.height = size
        self.color = color
        self.rect = self.image.get_rect()

        self.is_moveable = is_moveable
        self.frames_per_move = fpm
        self.move_ticker = 0

    def update(self):
        self.image.fill(self.color)
        if self.is_moveable:
            self.move_ticker += 1
        self.rect.x = self.x * self.tile_size[0]
        self.rect.y = self.y * self.tile_size[1]

    def draw(self):
        pass

    def move(self, dx=0, dy=0):
        if self.is_moveable and self.move_ticker > self.frames_per_move:
            self.move_ticker = 0
            if 0 <= self.x + dx < Settings.TILE_COUNT[0]:
                self.x += dx
            if 0 <= self.y + dy < Settings.TILE_COUNT[1]:
                self.y += dy

    def to_string(self):
        return str(self.x) + " " + str(self.y) + " " + str(self.color)


class Goal(GameObject):
    def __init__(self, sprite_groups, tile_size, color, coords, size=(1, 1)):
        super().__init__(sprite_groups, tile_size, color, coords, size)


class Player(GameObject):
    def __init__(self, sprite_groups, tile_size, color, coords, size=(1, 1), walls=None):
        super().__init__(sprite_groups, tile_size, color, coords, size, True)
        self.is_alive = True
        self.walls = walls
        self.original_color = color

    def is_alive_now(self):
        return "Alive" if self.is_alive else "Dead"

    def die(self):
        self.is_alive = False
        self.color = Color.BLACK

    def resurrect(self):
        self.is_alive = True
        self.color = self.original_color

    def update(self):
        if self.collides_with_wall(self.x, self.y):
            self.die()
        return super().update()

    def move(self, dx=0, dy=0):
        if self.is_alive:
            if self.collides_with_wall(self.x + dx, self.y + dy):
                self.die()
            else:
                super().move(dx, dy)

    def collides_with_wall(self, x, y):
        for wall in self.walls:
            if wall.x == x and wall.y == y:
                return True
        return False


class Wall(GameObject):
    def __init__(self, sprite_groups, tile_size, color, coords, size=(1, 1), isMoveable=False, fpm=Settings.FRAMES_PER_MOVE, movement_range=(0, 0)):
        super().__init__(sprite_groups, tile_size, color, coords, size, isMoveable, fpm)
        self.move_dir = 1
        self.curr_pos, self.max_pos = movement_range

    def update(self):
        if self.is_moveable and self.move_ticker > self.frames_per_move:
            self.automover()
        return super().update()

    def automover(self):
        self.curr_pos += self.move_dir
        if self.max_pos > 0:
            self.move(self.move_dir, 0)
            if self.curr_pos <= 0 or self.curr_pos >= self.max_pos:
                self.move_dir = 0 - self.move_dir
        elif self.max_pos < 0:
            self.move(0, self.move_dir)
            if self.curr_pos >= 0 or self.curr_pos <= self.max_pos:
                self.move_dir = 0 - self.move_dir
