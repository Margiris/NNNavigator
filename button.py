import pygame
from color import Color
from settings import Settings


class Button:
    def __init__(self, surface, coords, size, bg_color, text, function, *args):
        self.surface = surface
        self.coords = coords
        self.width, self.height = size
        self.bg_color = bg_color
        self.border_color = Color.randomColor()
        self.hover_color = Color.shadeColor(self.bg_color, 15)
        self.hovered = False
        self.text = text
        self.function = function
        self.args = args
        self.font = pygame.font.SysFont(
            'Roboto', Settings.BUTTON_TEXT_SIZE, bold=True)

    @property
    def x(self):
        return self.coords()[0] if callable(self.coords) else self.coords[0]

    @property
    def y(self):
        return self.coords()[1] if callable(self.coords) else self.coords[1]

    @property
    def coords_4(self):
        return (self.x, self.y, self.width, self.height)

    def update(self):
        cursor = pygame.mouse.get_pos()
        if self.x < cursor[0] < self.x + self.width and self.y < cursor[1] < self.y + self.height:
            self.hovered = True
        else:
            self.hovered = False

    def draw(self):
        if self.hovered:
            color = self.hover_color
            border_color = self.border_color
        else:
            color = self.bg_color
            border_color = None

        pygame.draw.rect(self.surface, color, self.coords_4)
        if border_color != None:
            pygame.draw.rect(self.surface, self.border_color, self.coords_4, 2)

        self.show_text()

    def show_text(self):
        if self.text != None:
            string = str(self.text() if callable(self.text) else self.text)
            text = self.font.render(
                string, True, Color.WHITE)
            text_size = text.get_size()
            text_x = self.x + (self.width / 2) - (text_size[0] / 2)
            text_y = self.y + (self.height / 2) - (text_size[1] / 2)
            self.surface.blit(text, (text_x, text_y))

    def click(self):
        if self.function != None and callable(self.function):
            self.function(*self.args)


class ButtonFactory:
    @staticmethod
    def createButton(surface, pos, color, text, function, *args):
        return Button(surface, pos, Settings.BUTTON_SIZE,
                      color, text, function, *args)

    @staticmethod
    def createButtonCentered(settings_instance, surface, color, text, function, *args):
        return ButtonFactory.createButton(surface, settings_instance.BUTTON_POS_CENTER,
                                          color, text, function, *args)
