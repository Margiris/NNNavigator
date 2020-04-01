import pygame
from color import Color
from settings import Settings


class Surface:
    def __init__(self, parent, size_func, offset, fill_color):
        self.parent = parent
        self.size_func = size_func
        self.original_size = size_func()
        self.pos = offset
        self.fill_color = fill_color

        self.surface = pygame.Surface(self.original_size)

    @property
    def size(self):
        return self.size_func()

    def update(self):
        pass

    def draw(self):
        self.surface.fill(self.fill_color)

        self.parent.blit(pygame.transform.scale(
            self.surface, self.size), self.pos)


class TiledSurface(Surface):
    def __init__(self, parent, size_func, offset, fill_color, line_color, line_width):
        super().__init__(parent, size_func, offset, fill_color)

        self.line_color = line_color
        self.line_width = line_width
        self.tile_size = (self.original_size[0] / Settings.TILE_COUNT[0],
                          self.original_size[1] / Settings.TILE_COUNT[1])

    def draw(self):
        self.surface.fill(self.fill_color)

        # draw border on parent's surface
        line_width_offset = int(
            round(self.line_width / 2)) if self.line_width > 1 else self.line_width
        pygame.draw.rect(self.parent, self.line_color,
                         (self.pos[0] - line_width_offset,
                          self.pos[1] - line_width_offset,
                          self.size[0] + line_width_offset * 2,
                          self.size[1] + line_width_offset * 2),
                         self.line_width)

        self.draw_grid()

        self.parent.blit(pygame.transform.scale(
            self.surface, self.size), self.pos)

    def draw_grid(self):
        for x in range(1, Settings.TILE_COUNT[0]):
            pygame.draw.line(self.surface, self.line_color,
                             (self.tile_size[0] * x, 0),
                             (self.tile_size[0] * x, self.original_size[1]),
                             self.line_width)

        for y in range(1, Settings.TILE_COUNT[1]):
            pygame.draw.line(self.surface, self.line_color,
                             (0, self.tile_size[1] * y),
                             (self.original_size[0], self.tile_size[1] * y),
                             self.line_width)
