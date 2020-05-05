from random import randint
from pygame import sprite, Rect
from settings import Settings

from find_a_way.solver import Star as AStar


class Brain:
    def __init__(self, player, surface, reached_goal):
        self.player = player
        self.surface = surface
        self.reached_goal = reached_goal
        self.vision = [None for _ in range(8)]
        self.vision_cells = []

    def update(self):
        random_x = randint(-1, 1)
        random_y = randint(-1, 1)
        self.update_vision()
        self.player.move(random_x, random_y)

    def move(self, dx=0, dy=0):
        pass

    def draw(self):
        for cell in self.vision_cells:
            self.surface.surface.fill(Settings.VISION_COLOR, ((
                cell[0] * self.surface.tile_size[0], cell[1] * self.surface.tile_size[1]), self.surface.tile_size))

    def update_vision(self):
        self.vision_cells = []
        index = 0
        for y in range(-1, 2):
            for x in range(-1, 2):
                if x == 0 and y == 0:
                    continue
                self.vision[index] = 0
                for i in range(1, Settings.VISION_DISTANCE + 1):
                    if self.player.collides_with_wall(self.player.x + x * i, self.player.y + y * i):
                        self.vision[index] = Settings.VISION_DISTANCE - i + 1
                        break
                    else:
                        self.vision_cells.append((self.player.x + x * i,
                                                  self.player.y + y * i))
                index += 1

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
