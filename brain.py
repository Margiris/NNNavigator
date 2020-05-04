from random import randint
from settings import Settings


class Brain:
    def __init__(self, player, reached_goal):
        self.player = player
        self.reached_goal = reached_goal

    def update(self):
        # pass
        random_x = randint(-1, 1)
        random_y = randint(-1, 1)
        self.player.move(random_x, random_y)

    def resurrect(self):
        pass

    def __str__(self):
        return Settings.TUPLE_SEP.join([str(self.reached_goal)])
