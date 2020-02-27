from util import load_sprite


class GameObject:
    def __init__(self, x=0, y=0, width=1, height=1, sprite_filename=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.sprite = load_sprite(sprite_filename)

    def rect(self):
        return (self.x, self.y, self.width, self.height)
