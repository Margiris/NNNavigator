from color import Color


class Settings:
    ##################################### Static #####################################
    MIN_FPS = 10
    MAX_FPS = 60
    FRAMES_PER_MOVE = 5

    WALL_SPAWN_RATE = 0.2
    MOVING_WALL_SPAWN_RATE = WALL_SPAWN_RATE * 0.8

    SCALE = 1

    BACKGROUND_COLOR = Color.DIM_GRAY
    BUTTON_TEXT_COLOR = Color.WHITE
    LINE_COLOR = Color.BLACK
    GAME_BG_COLOR = Color.DIM_DARK_GRAY

    WINDOW_TITLE = "NNNavigator"

    GAME_DIMENSIONS = (1024, 768)
    LINE_WIDTH = 1

    WINDOW_SIZE = (GAME_DIMENSIONS[0] + LINE_WIDTH * 2,
                   GAME_DIMENSIONS[1] + 0)

    MARGINS = (int(round(GAME_DIMENSIONS[0] / 64 * SCALE)),
               int(round(GAME_DIMENSIONS[1] / 128 * SCALE)))

    BUTTON_TEXT_SIZE = int(round(GAME_DIMENSIONS[1] / 64 * SCALE))

    BUTTON_SIZE = (int(round(GAME_DIMENSIONS[0] / 16 * SCALE)),
                   int(round(GAME_DIMENSIONS[1] / 32 * SCALE)))

    @staticmethod
    def BUTTON_POS(i):
        return (Settings.MARGINS[0] * (i + 1) + Settings.BUTTON_SIZE[0] * i,
                Settings.MARGINS[1])

    BUTTON_BAR_DIMENSIONS = (
        WINDOW_SIZE[0], MARGINS[1] * 2 + BUTTON_SIZE[1])

    WINDOW_SIZE = (GAME_DIMENSIONS[0],
                   GAME_DIMENSIONS[1] + BUTTON_BAR_DIMENSIONS[1])

    BUTTON_BAR_POS = (0, 0)
    GAME_POS = (0, BUTTON_BAR_DIMENSIONS[1] + 0)

    TILE_COUNT = (64, 48)
    # TILE_SIZE = ()
    # TILE_COUNT = (8, 6)

    # minimum size fits at least one button and a game window of 1x1 px in size
    WINDOW_SIZE_MINIMUM = (GAME_POS[0] * 2 + BUTTON_SIZE[0],
                           BUTTON_BAR_DIMENSIONS[1] + MARGINS[1] + 1)

    #################################### Instance ####################################
    def __init__(self):
        self.WINDOW_SIZE_CURRENT = self.WINDOW_SIZE

    def BUTTON_POS_CENTER(self):
        return ((self.WINDOW_SIZE_CURRENT[0] - self.BUTTON_SIZE[0]) / 2,
                # (self.WINDOW_SIZE_CURRENT[1] - self.BUTTON_SIZE[1]) / 2)
                self.MARGINS[1])

    def BUTTON_BAR_DIMENSIONS_CURRENT(self):
        return self.BUTTON_BAR_DIMENSIONS

    def GAME_DIMENSIONS_CURRENT(self):
        return (self.WINDOW_SIZE_CURRENT[0] - self.GAME_POS[0] * 2,
                self.WINDOW_SIZE_CURRENT[1] - self.GAME_POS[1])

    # @property
    # def TILE_SIZE(self):
    #     return (GAME_DIMENSIONS[0] / Settings.TILE_GRID[0],
    #             GAME_DIMENSIONS[1] / Settings.TILE_GRID[1])
