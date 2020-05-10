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

    def __init__(self, sprite_groups, function, tile_size, color, coords, size=(1, 1), goal=None, walls=None, fpm=Settings.FRAMES_PER_MOVE, move_ticks=0, reached_goal=False, vision_surface=None, model_name=None):
        super().__init__(sprite_groups, tile_size, color,
                         coords, size, True, fpm=fpm, move_ticks=move_ticks)
        self.vision_cells = self.init_vision()
        self.vision = numpy.ones(
            Brain.OBSERVATION_SPACE_VALUES, dtype=numpy.float64)
        self.vision_distance = numpy.ones(
            Brain.OBSERVATION_SPACE_VALUES, dtype=numpy.float64)
        self.report = function
        self.goal = goal
        self.walls = walls
        self.original_color = color
        self.brain = Brain(self, vision_surface, reached_goal, model_name)
        self.resurrect()

    def init_vision(self):
        vision_cells = [set() for _ in range(10)]
        for i in range(1, Settings.VISION_DISTANCE + 1):
            for d, coord in self.DIRECTIONS.items():
                vision_cells[d].add((coord[0] * i, coord[1] * i))

        return vision_cells

    def update(self):
        self.brain.update()
        if self.collides_with_wall(self.x, self.y):
            self.die()
        return super().update()

    def move(self, dx=0, dy=0):
        if self.is_alive and self.move_ticker > self.frames_per_move:
            if self.collides_with_wall(self.x + dx, self.y + dy):
                self.die()
            else:
                if self.x + dx == self.goal.x and self.y + dy == self.goal.y:
                    self.brain.reached_goal = True
                    self.die()
                self.brain.move(dx, dy)
                return super().move(dx, dy)

    def die(self):
        self.is_alive = False
        self.color = Settings.PLAYER_DEAD_COLOR
        self.brain.die()
        self.report(self)

    def resurrect(self):
        self.move_ticker = 0
        self.is_alive = True
        self.color = self.original_color
        self.brain.resurrect()

    def collides_with_wall(self, x, y):
        for wall in self.walls:
            if wall.x == x and wall.y == y:
                return True
        return False

    def look_8_ways(self):
        self.vision_distance = numpy.ones(
            self.brain.OBSERVATION_SPACE_VALUES, dtype=numpy.float64)
        for wall in self.walls:
            x = wall.x - self.x
            y = wall.y - self.y
            if x > Settings.VISION_DISTANCE or y > Settings.VISION_DISTANCE:
                continue
            a = numpy.array((0, 0))
            b = numpy.array((x, y))
            for direction in range(8):
                if (x, y) in self.vision_cells[direction]:
                    dist = (int(numpy.linalg.norm(a-b)) - 1) / \
                        Settings.VISION_DISTANCE
                    if self.vision_distance[direction] > dist:
                        self.vision_distance[direction] = dist
                    break

        a = numpy.array((self.x, self.y))
        b = numpy.array((self.goal.x, self.goal.y))
        self.vision_distance[8] = int(
            numpy.linalg.norm(a-b)) / Settings.TILE_COUNT[0]

        self.vision_distance[9] = angle_between(
            (self.x, self.y), (self.goal.x, self.goal.y))

        # self.vision_distance[9] = numpy.math.atan2(
        #     numpy.linalg.det([a-b]), numpy.dot(a-b))
        return self.vision_distance

    def look_square(self):
        vision = numpy.zeros(
            self.brain.OBSERVATION_SPACE_VALUES, dtype=numpy.uint8)
        x_start = self.x - Settings.VISION_DISTANCE
        x_end = self.x + Settings.VISION_DISTANCE
        y_start = self.y - Settings.VISION_DISTANCE
        y_end = self.y + Settings.VISION_DISTANCE

        for wall in self.walls:
            if x_start <= wall.x <= x_end and y_start <= wall.y <= y_end:
                vision[wall.y - self.y + Settings.VISION_DISTANCE][wall.x -
                                                                   self.x + Settings.VISION_DISTANCE] = -1
        if x_start < self.goal.x < x_end and y_start < self.goal.y < y_end:
            vision[self.goal.y - self.y + Settings.VISION_DISTANCE][self.goal.x -
                                                                    self.x + Settings.VISION_DISTANCE] = 1

        return vision

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
