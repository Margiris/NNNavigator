import pygame
from color import Color
from settings import Settings


class Surface:
    def __init__(self, parent, size_func, offset, fill_color):
        self.parent = parent
        self.size_func = size_func
        self.pos = offset
        self.fill_color = fill_color

        self.surface = pygame.Surface(size_func())

    @property
    def size(self):
        return self.size_func()

    def update(self):
        pass

    def draw(self):
        # self.surface.fill(self.fill_color)

        self.parent.blit(pygame.transform.scale(
            self.surface, self.size), self.pos)


class TiledScalableSurface(Surface):
    def __init__(self, parent, size, size_func, offset, fill_color, line_color, line_width):
        super().__init__(parent, size_func, offset, fill_color)

        self.original_size = size
        self.line_color = line_color
        self.line_width = line_width
        self.tile_size = (int(round(self.original_size[0] / Settings.TILE_COUNT[0])),
                          int(round(self.original_size[1] / Settings.TILE_COUNT[1])))

        self.font = pygame.font.SysFont('Roboto', 10, bold=True)

    def draw(self):
        self.draw_grid()
        self.draw_border()

        self.parent.blit(pygame.transform.scale(
            self.surface, self.size), self.pos)

    # Draw a border on surface
    def draw_border(self):
        pygame.draw.rect(self.surface, self.line_color,
                         # pygame.draw.rect(self.surface, Color.ALICE_BLUE,
                         (0, 0, self.original_size[0], self.original_size[1]),
                         self.line_width)

    def draw_grid(self):
        for x in range(0, self.original_size[0], self.tile_size[0]):
            pygame.draw.line(self.surface, self.line_color,
                             (x, 0), (x, self.original_size[1]),
                             self.line_width)
            self.show_text(x=x, text=str(int(round(x / self.tile_size[0]))))

        for y in range(0, self.original_size[1], self.tile_size[1]):
            pygame.draw.line(self.surface, self.line_color,
                             (0, y), (self.original_size[0], y),
                             self.line_width)
            self.show_text(y=y, text=str(int(round(y / self.tile_size[1]))))

    def show_text(self, x=0, y=0, text=""):
        text = self.font.render(text, True, self.line_color)
        text_size = text.get_size()
        text_x = x + self.tile_size[0] / 2 - (text_size[0] / 2)
        text_y = y + self.tile_size[0] / 2 - (text_size[1] / 2)
        self.surface.blit(text, (text_x, text_y))
