import numpy
from settings import Settings
from pygame import sprite, Rect, Surface, sprite
from random import randint
import sys
print(sys.executable)


class VisionSurface:
    def __init__(self, tile_size, color, coords, surface):
        surface_size = ((Settings.VISION_DISTANCE * 2 + 1) * tile_size[0],
                        (Settings.VISION_DISTANCE * 2 + 1) * tile_size[1])
        self.parent_surface = surface
        self.surface = Surface(surface_size)
        self.surface.set_alpha(20)
        self.x, self.y = coords
        self.tile_size = tile_size
        self.color = color

    def draw(self):
        self.surface.fill(self.color)
        self.parent_surface.blit(self.surface, (self.x * self.tile_size[0],
                                                self.y * self.tile_size[1]))

    def move(self, dx=0, dy=0):
        self.x += dx
        self.y += dy


class Brain:
    def __init__(self, player, surface, reached_goal):
        self.player = player
        self.surface = surface
        self.reached_goal = reached_goal

        coords = (self.player.x - Settings.VISION_DISTANCE,
                  self.player.y - Settings.VISION_DISTANCE)
        self.visionSprite = VisionSurface(
            surface.tile_size, player.color, coords, surface.surface)

    def update(self):
        random_x = randint(-1, 1)
        random_y = randint(-1, 1)
        self.look_square()
        # self.look_8_ways()
        # self.player.move(random_x, random_y)
        # print("------------------")
        # print(self.look_square())

    def move(self, dx=0, dy=0):
        self.visionSprite.move(dx, dy)

    def draw(self):
        self.visionSprite.draw()

    def look_8_ways(self):
        vision_cells = []
        vision = [None for _ in range(8)]
        index = 0
        for y in range(-1, 2):
            for x in range(-1, 2):
                if x == 0 and y == 0:
                    continue
                vision[index] = 0
                for i in range(1, Settings.VISION_DISTANCE + 1):
                    if self.player.collides_with_wall(self.player.x + x * i, self.player.y + y * i):
                        vision[index] = Settings.VISION_DISTANCE - i + 1
                        break
                    else:
                        vision_cells.append((self.player.x + x * i,
                                             self.player.y + y * i))
                index += 1
        return vision, vision_cells

    def look_square(self):
        vision = numpy.ones((Settings.VISION_DISTANCE * 2 + 1,
                             Settings.VISION_DISTANCE * 2 + 1), dtype=numpy.uint8)
        x_start = self.player.x - Settings.VISION_DISTANCE
        x_end = self.player.x + Settings.VISION_DISTANCE
        y_start = self.player.y - Settings.VISION_DISTANCE
        y_end = self.player.y + Settings.VISION_DISTANCE

        for wall in self.player.walls:
            if x_start <= wall.x <= x_end and y_start <= wall.y <= y_end:
                vision[wall.y - self.player.y + Settings.VISION_DISTANCE][wall.x -
                                                                          self.player.x + Settings.VISION_DISTANCE] = 0
        if x_start < self.player.goal.x < x_end and y_start < self.player.goal.y < y_end:
            vision[self.player.goal.y - self.player.y + Settings.VISION_DISTANCE][self.player.goal.x -
                                                                                  self.player.x + Settings.VISION_DISTANCE] = 2

        return vision

    def die(self):
        # self.unobstructed_vision_cells.remove(
        #     [cell for cell in self.unobstructed_vision_cells])
        pass

    def resurrect(self):
        # self.unobstructed_vision_cells.add(
        #     [cell for cell in self.vision_cells])
        pass

    def __str__(self):
        return Settings.TUPLE_SEP.join([str(self.reached_goal)])
