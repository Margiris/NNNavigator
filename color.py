class Color:
    @staticmethod
    def shade_color(color, percent):
        t = 0 if percent < 0 else 255
        p = (percent * -1 if percent < 0 else percent) / 100
        r, g, b = color
        return (round((t - r) * p) + r,
                round((t - g) * p) + g,
                round((t - b) * p) + b)

    @staticmethod
    def random_color():
        from random import randint
        colors = [value for _, value in Color.__dict__.items()
                  if type(value) is tuple]
        return colors[randint(0, len(colors) - 5)]

    BLACK = (0, 0, 0)
    TURQUOISE_BLUE = (96, 235, 221)
    KOMBU_GREEN = (33, 42, 36)
    PINE_TREE = (18, 21, 20)
    EMERALD = (34, 153, 50)
    DARK_OLIVE_GREEN = (82, 117, 75)
    FOREST_GREEN_CRAYOLA = (99, 164, 108)
    WHITE = (255, 255, 255)
