from gameObject import GameObject


class Player(GameObject):
    def __init__(self, x=0, y=0, width=1, height=1, sprite_filename="", *args, **kwargs):
        super().__init__(x, y, width, height, sprite_filename, *args, **kwargs)
        self.is_alive = False
