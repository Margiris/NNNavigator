import random


class GameObject:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color()

    def rect(self):
        return (self.x, self.y, self.width, self.height)

    def coords(self):
        return (self.x, self.y)

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


class Player(GameObject, Moveable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_alive = False


class Wall(GameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_random(self, coord_max, min_dimensions, tile_count=1):
        self.width = random.randint(
            min_dimensions[0], coord_max[0] / tile_count)
        self.height = random.randint(
            min_dimensions[1], coord_max[1] / tile_count)

        if self.height > self.width:
            self.width = 10
        else:
            self.height = 10

        self.place_at_random_coords(coord_max)


class WallMoveable(Wall, Moveable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
