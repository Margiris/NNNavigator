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
        # self.vision_cells = sprite.Group()
        # self.unobstructed_vision_cells = sprite.Group()
        # self.create_vision_cells()

    def update(self):
        random_x = randint(-1, 1)
        random_y = randint(-1, 1)
        self.update_vision()
        self.player.move(random_x, random_y)
        # to_add = []
        # to_remove = []

        # for cell in self.vision_cells:
        #     now_obstructed = self.player.collides_with_wall(cell.x, cell.y)
        #     if not cell.obstructed and now_obstructed:
        #         to_remove.append(cell)
        #     if cell.obstructed and not now_obstructed:
        #         to_add.append(cell)

        #     cell.obstructed = now_obstructed

        # self.unobstructed_vision_cells.add(to_add)
        # self.unobstructed_vision_cells.remove(to_remove)

        # self.vision_cells.update()
        # self.unobstructed_vision_cells.update()

    def move(self, dx=0, dy=0):
        for cell in self.vision_cells:
            cell.x += dx
            cell.y += dy

    def draw(self):
        # self.unobstructed_vision_cells.draw(self.surface.surface)
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
                self.vision[index] = Settings.VISION_DISTANCE
                for i in range(1, Settings.VISION_DISTANCE + 1):
                    if self.player.collides_with_wall(self.player.x + x * i, self.player.y + y * i):
                        self.vision[index] = i - 1
                        break
                    else:
                        self.vision_cells.append((self.player.x + x * i,
                                                  self.player.y + y * i))
                index += 1

    def create_vision_cells(self):
        from gameObjects import VisionCell
        for i in range(1, Settings.VISION_DISTANCE + 1):
            for y in range(0 - i, i + 1, i):
                for x in range(0 - i, i + 1, i):
                    if x == 0 and y == 0:
                        continue
                    self.vision_cells.add(VisionCell(
                        (self.vision_cells, self.unobstructed_vision_cells), self.surface.tile_size, Settings.VISION_COLOR, (self.player.x + x, self.player.y + y)))

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
