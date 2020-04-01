import pygame


class Surface:
    def __init__(self, parent, size_func, offset, fill_color):
        self.parent = parent
        self.size_func = size_func
        self.pos = offset
        self.fill_color = fill_color

        self.surface = pygame.Surface(size_func())

        # self.pic = pygame.surface.Surface((50, 50))
        # self.pic.fill((255, 100, 200))

    @property
    def size(self):
        return self.size_func()

    def update(self):
        pass

    def draw(self):
        self.surface.fill(self.fill_color)
        # self.surface.blit(self.pic, (150, 80))

        self.parent.blit(pygame.transform.scale(
            self.surface, self.size), self.pos)


class GameSurface(Surface):
    def __init__(self, parent, size_func, offset, fill_color):
        super().__init__(parent, size_func, offset, fill_color)

    def draw(self):
        self.surface.fill(self.fill_color)

        self.draw_grid()

        self.parent.blit(pygame.transform.scale(
            self.surface, self.size), self.pos)

    def draw_grid(self):
        for x in range(10):
            pass
