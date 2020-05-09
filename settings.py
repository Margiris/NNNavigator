from color import Color


class Settings:
    ##################################### Static #####################################
    TUPLE_SEP = ','
    PROP_SEP = ';'

    DRAW_GAME = True
    MIN_FPS = 10
    MAX_FPS = 60
    FRAMES_PER_MOVE = 5

    WALL_SPAWN_RATE = 0.2
    MOVING_WALL_SPAWN_RATE = WALL_SPAWN_RATE * 0.8

    SCALE = 1.7

    COLOR_SHADE = 30
    BACKGROUND_COLOR = Color.KOMBU_GREEN
    GAME_BG_COLOR = Color.PINE_TREE
    LINE_COLOR = Color.KOMBU_GREEN

    BUTTON_BG_COLOR = Color.EMERALD
    BUTTON_TEXT_COLOR = Color.WHITE
    BUTTON_TEXT_INACTIVE_COLOR = Color.shade_color(
        BUTTON_TEXT_COLOR, -COLOR_SHADE)
    # BUTTON_BORDER_COLOR = Color.FOREST_GREEN_CRAYOLA

    GOAL_COLOR = Color.WHITE

    PLAYER_COLOR = Color.TURQUOISE_BLUE
    PLAYER_DEAD_COLOR = Color.shade_color(PLAYER_COLOR, -COLOR_SHADE)

    WALL_COLOR = Color.DARK_OLIVE_GREEN
    MOVING_WALL_COLOR = Color.FOREST_GREEN_CRAYOLA
    # MOVING_WALL_COLOR = Color.shade_color(WALL_COLOR, COLOR_SHADE)

    VISION_COLOR = Color.shade_color(PLAYER_COLOR, -COLOR_SHADE * 2)
    # VISION_COLOR = Color.shade_color(GAME_BG_COLOR, 1)
    VISION_DISTANCE = 15
    GOAL_DISTANCE = 1.0

    WINDOW_TITLE = "NNNavigator"

    GAME_DIMENSIONS = (1024, 768)
    LINE_WIDTH = 1

    WINDOW_SIZE = (GAME_DIMENSIONS[0] + LINE_WIDTH * 2,
                   GAME_DIMENSIONS[1] + 0)

    MARGINS = (int(round(GAME_DIMENSIONS[0] / 128 * SCALE)),
               int(round(GAME_DIMENSIONS[1] / 128 * SCALE)))

    BUTTON_TEXT_SIZE = int(round(GAME_DIMENSIONS[1] / 76 * SCALE))

    BUTTON_SIZE = (int(round(GAME_DIMENSIONS[0] / 16 * SCALE)),
                   int(round(GAME_DIMENSIONS[1] / 48 * SCALE)))

    @staticmethod
    def BUTTON_POS(i):
        if i < 0:
            return (Settings.WINDOW_SIZE[0] - Settings.MARGINS[0] * (-i) - Settings.BUTTON_SIZE[0] * (-i),
                    Settings.MARGINS[1])
        else:
            return (Settings.MARGINS[0] * (i + 1) + Settings.BUTTON_SIZE[0] * i,
                    Settings.MARGINS[1])

    BUTTON_BAR_DIMENSIONS = (
        WINDOW_SIZE[0], MARGINS[1] * 2 + BUTTON_SIZE[1])

    WINDOW_SIZE = (GAME_DIMENSIONS[0],
                   GAME_DIMENSIONS[1] + BUTTON_BAR_DIMENSIONS[1])

    BUTTON_BAR_POS = (0, 0)
    GAME_POS = (0, BUTTON_BAR_DIMENSIONS[1] + 0)

    TILE_COUNT = (128, 96)
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
