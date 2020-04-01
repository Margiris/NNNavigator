from color import Color


class Settings:
    MIN_FPS = 10
    MAX_FPS = 30

    WINDOW_TITLE = "NNNavigator"

    BACKGROUND_COLOR = Color.DIM_GRAY
    BUTTON_TEXT_COLOR = Color.WHITE

    WINDOW_SIZE = (1000, 750)

    TILE_GRID = (16, 12)

    def __init__(self):
        self.WINDOW_SIZE_CURRENT = self.WINDOW_SIZE

    def BUTTON_POS_CENTER(self):
        return ((self.WINDOW_SIZE_CURRENT[0] - self.BUTTON_SIZE[0]) / 2,
                (self.WINDOW_SIZE_CURRENT[1] - self.BUTTON_SIZE[1]) / 2)

    def GAME_DIMENSIONS(self):
        return (self.WINDOW_SIZE_CURRENT[0] - self.MARGINS[0] * 2,
                self.WINDOW_SIZE_CURRENT[1] - self.MARGINS[1] * 3 - self.BUTTON_SIZE[1])

    @property
    def TILE_SIZE(self):
        return (self.GAME_DIMENSIONS()[0] / Settings.TILE_GRID[0],
                self.GAME_DIMENSIONS()[1] / Settings.TILE_GRID[1])

    @property
    def GAME_POS(self):
        return (self.MARGINS[0],
                self.MARGINS[1] * 2 + self.BUTTON_SIZE[1])

        # minimum size fits at least one button and a game window of size 1x1 px
    @property
    def WINDOW_SIZE_MINIMUM(self):
        return (self.GAME_POS[0] * 4 + self.BUTTON_SIZE[0],
                self.GAME_POS[1] + self.MARGINS[1] + 1)

    # @property
    # def BUTTON_TEXT_SIZE(self): return int(round(self.WINDOW_SIZE[1] / 30))
    BUTTON_TEXT_SIZE = int(round(WINDOW_SIZE[1] / 30))

    # @property
    # def MARGINS(self): return (int(round(self.WINDOW_SIZE[0] / 160)),
    #                            int(round(self.WINDOW_SIZE[1] / 120)))
    MARGINS = (int(round(WINDOW_SIZE[0] / 160)),
               int(round(WINDOW_SIZE[1] / 120)))

    # @property
    # def BUTTON_SIZE(self):
    #     return (int(round(self.WINDOW_SIZE[0] / 8)),
    #             int(round(self.WINDOW_SIZE[1] / 15)))

    BUTTON_SIZE = (int(round(WINDOW_SIZE[0] / 8)),
                   int(round(WINDOW_SIZE[1] / 15)))

    # def BUTTON_POS_TOP_1(self):
    #     return (self.MARGINS[0] * 2,
    #             self.MARGINS[1])

    BUTTON_POS_TOP_1 = (MARGINS[0] * 2,
                        MARGINS[1])

    # def BUTTON_POS_TOP_2(self):
    #     return (self.MARGINS[0] * 2 + self.BUTTON_POS_TOP_1()[0] + self.BUTTON_SIZE[0],
    #             self.MARGINS[1])
    BUTTON_POS_TOP_2 = (MARGINS[0] * 2 + BUTTON_POS_TOP_1[0] + BUTTON_SIZE[0],
                        MARGINS[1])

    # def BUTTON_POS_TOP_3(self):
    #     return (self.MARGINS[0] * 2 + self.BUTTON_POS_TOP_2()[0] + self.BUTTON_SIZE[0],
    #             self.MARGINS[1])
    BUTTON_POS_TOP_3 = (MARGINS[0] * 2 + BUTTON_POS_TOP_2[0] + BUTTON_SIZE[0],
                        MARGINS[1])
