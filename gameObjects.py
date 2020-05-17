from math import cos, atan2, pi
import pygame
import numpy
from brain import Brain
from settings import Settings


class GameObject(pygame.sprite.Sprite):
    def __init__(self, sprite_groups, tile_size, color, coords, size, is_movable=False, fpm=Settings.FRAMES_PER_MOVE, move_ticks=0):
        self.groups = sprite_groups
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.tile_size = tile_size
        self.image = pygame.Surface((size[0] * self.tile_size[0],
                                     size[1] * self.tile_size[1]))
        self.x, self.y = coords
        self.width, self.height = size
        self.color = color
        self.rect = self.image.get_rect()

        self.is_movable = is_movable
        self.frames_per_move = fpm
        self.move_ticker = move_ticks

    def update(self):
        self.image.fill(self.color)
        if self.is_movable:
            self.move_ticker += 1
        self.rect.x = self.x * self.tile_size[0]
        self.rect.y = self.y * self.tile_size[1]

    def draw(self):
        pass

    def move(self, dx=0, dy=0):
        if self.is_movable and self.move_ticker > self.frames_per_move:
            self.move_ticker = 0
            if 0 <= self.x + dx < Settings.TILE_COUNT[0]:
                self.x += dx
            if 0 <= self.y + dy < Settings.TILE_COUNT[1]:
                self.y += dy

    def __str__(self):
        return Settings.PROP_SEP.join([str(self.x), str(self.y), str(self.width), str(self.height),
                                       str(self.is_movable), str(self.frames_per_move), str(self.move_ticker)])


class Goal(GameObject):
    def __init__(self, sprite_groups, tile_size, color, coords, size=(1, 1)):
        super().__init__(sprite_groups, tile_size, color, coords, size)

    def __str__(self):
        return Settings.PROP_SEP.join(["G", tuple__str__(self.color), super().__str__()])


class Player(GameObject):
    DIRECTIONS = {0: (0, -1),
                  1: (1, -1),
                  2: (1, 0),
                  3: (1, 1),
                  4: (0, 1),
                  5: (-1, 1),
                  6: (-1, 0),
                  7: (-1, -1)}

    def __init__(self, sprite_groups, function, tile_size, color, coords, size=(1, 1), goal=None, walls=None, fpm=Settings.FRAMES_PER_MOVE, move_ticks=0, reached_goal=False, vision_surface=None, model_name=None, astar=None):
        super().__init__(sprite_groups, tile_size, color,
                         coords, size, True, fpm=fpm, move_ticks=move_ticks)
        self.steps_func = astar
        self.steps = False
        self.report = function
        self.goal = goal
        self.walls = walls
        self.original_color = color
        self.resurrect()

    def update(self):
        if self.is_alive and self.move_ticker > self.frames_per_move:
            self.astar()
        if self.collides_with_wall(self.x, self.y):
            self.die()
        return super().update()

    def draw_path(self, surface):
        if self.steps:
            for i in range(len(self.steps) - 1):
                start_pos = (self.steps[i][0] * self.tile_size[0] + self.tile_size[0] / 2,
                             self.steps[i][1] * self.tile_size[1] + self.tile_size[1] / 2)
                end_pos = (self.steps[i+1][0] * self.tile_size[0] + self.tile_size[0] / 2,
                           self.steps[i+1][1] * self.tile_size[1] + self.tile_size[1] / 2)
                pygame.draw.line(surface,
                                 Settings.PLAYER_VISION_COLOR, start_pos, end_pos)

    def astar(self):
        self.steps = self.steps_func((self.x, self.y))
        if self.steps:
            self.move(self.steps[-1][0] - self.x, self.steps[-1][1] - self.y)
        else:
            self.move_ticker = 0
        #     self.die()

    def move(self, dx=0, dy=0):
        if self.is_alive and self.move_ticker > self.frames_per_move:
            if self.collides_with_wall(self.x + dx, self.y + dy):
                self.die()
            else:
                if self.x + dx == self.goal.x and self.y + dy == self.goal.y:
                    self.die()
                return super().move(dx, dy)

    def die(self):
        self.is_alive = False
        self.color = Settings.PLAYER_DEAD_COLOR
        self.report(self)

    def resurrect(self):
        self.move_ticker = 0
        self.is_alive = True
        self.color = self.original_color

    def collides_with_wall(self, x, y):
        for wall in self.walls:
            if wall.x == x and wall.y == y:
                return True
        return False

    def __str__(self):
        return Settings.PROP_SEP.join(["P", tuple__str__(self.original_color), super().__str__(), str(self.is_alive), str(self.brain)])


class Wall(GameObject):
    def __init__(self, sprite_groups, tile_size, color, coords, size=(1, 1), is_movable=False,
                 fpm=Settings.FRAMES_PER_MOVE, movement_range=(0, 0), move_ticks=0, move_dir=None):
        super().__init__(sprite_groups, tile_size, color,
                         coords, size, is_movable, fpm, move_ticks)
        self.curr_pos, self.max_pos = movement_range

        if move_dir:
            self.move_dir = move_dir
        else:
            self.move_dir = 1 if self.max_pos < 0 else -1

    def update(self):
        if self.is_movable and self.move_ticker > self.frames_per_move:
            self.automover()
        return super().update()

    def automover(self):
        if self.max_pos > 0:
            if self.curr_pos <= 0 or self.curr_pos >= self.max_pos:
                self.move_dir = -self.move_dir
            self.move(self.move_dir, 0)
        elif self.max_pos < 0:
            if self.curr_pos >= 0 or self.curr_pos <= self.max_pos:
                self.move_dir = -self.move_dir
            self.move(0, -self.move_dir)
        self.curr_pos += self.move_dir

    def __str__(self):
        return Settings.PROP_SEP.join(["W", tuple__str__(self.color), super().__str__(), str(self.curr_pos), str(self.max_pos), str(self.move_dir)])


def tuple__str__(t):
    return Settings.TUPLE_SEP.join([str(c) for c in t])


def angle_between(v1, v2):
    dx = v2[0] - v1[0]
    dy = v2[1] - v1[1]
    rads = atan2(-dy, dx)
    rads %= 2*pi
    return cos(rads)
