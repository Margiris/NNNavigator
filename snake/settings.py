from color import Color


class Settings:
    ##################################### Static #####################################
    MIN_FPS = 10
    MAX_FPS = 30

    BACKGROUND_COLOR = Color.DIM_GRAY
    BUTTON_TEXT_COLOR = Color.WHITE
    LINE_COLOR = Color.BLACK

    WINDOW_TITLE = "NNNavigator"
    WINDOW_SIZE = (810, 662)
    LINE_WIDTH = 1

    MARGINS = (int(round(WINDOW_SIZE[0] / 160)),
               int(round(WINDOW_SIZE[1] / 120)))

    BUTTON_TEXT_SIZE = int(round(WINDOW_SIZE[1] / 30))

    BUTTON_SIZE = (int(round(WINDOW_SIZE[0] / 8)),
                   int(round(WINDOW_SIZE[1] / 15)))

    BUTTON_POS_TOP_1 = (MARGINS[0] * 2,
                        MARGINS[1])
    BUTTON_POS_TOP_2 = (MARGINS[0] * 2 + BUTTON_POS_TOP_1[0] + BUTTON_SIZE[0],
                        MARGINS[1])
    BUTTON_POS_TOP_3 = (MARGINS[0] * 2 + BUTTON_POS_TOP_2[0] + BUTTON_SIZE[0],
                        MARGINS[1])

    # GAME_DIMENSIONS = Settings().GAME_DIMENSIONS_CURRENT()
    TILE_COUNT = (64, 48)
    # TILE_COUNT = (8, 6)

    @property
    def GAME_POS(self):
        return (self.MARGINS[0],
                self.MARGINS[1] * 2 + self.BUTTON_SIZE[1])

    # minimum size fits at least one button and a game window of 1x1 px in size
    @property
    def WINDOW_SIZE_MINIMUM(self):
        return (self.GAME_POS[0] * 4 + self.BUTTON_SIZE[0],
                self.GAME_POS[1] + self.MARGINS[1] + 1)

    #################################### Instance ####################################
    def __init__(self):
        self.WINDOW_SIZE_CURRENT = self.WINDOW_SIZE

    def BUTTON_POS_CENTER(self):
        return ((self.WINDOW_SIZE_CURRENT[0] - self.BUTTON_SIZE[0]) / 2,
                (self.WINDOW_SIZE_CURRENT[1] - self.BUTTON_SIZE[1]) / 2)

    def GAME_DIMENSIONS_CURRENT(self):
        return (self.WINDOW_SIZE_CURRENT[0] - self.MARGINS[0] * 2,
                self.WINDOW_SIZE_CURRENT[1] - self.MARGINS[1] * 3 - self.BUTTON_SIZE[1])

    # @property
    # def TILE_SIZE(self):
    #     return (GAME_DIMENSIONS[0] / Settings.TILE_GRID[0],
    #             GAME_DIMENSIONS[1] / Settings.TILE_GRID[1])
