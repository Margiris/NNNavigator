import pygame
from button import Button, ButtonFactory
from color import Color
from gameObjects import Player
from surface import Surface, TiledScalableSurface
from settings import Settings


class State:
    def __init__(self, name, program):
        self.enum = []
        self.name = name
        self.previous_state = program.state
        self.setup_buttons_and_surfaces(program)

    def setup_buttons_and_surfaces(self, program):
        self.buttons = []
        self.surfaces = []
        self.player = None
        self.sprites = None

        if self == State.MENU:
            self.handle_specific_events = self.handle_events_menu

            self.surfaces.append(Surface(program.surface_main,
                                         program.settings.BUTTON_BAR_DIMENSIONS_CURRENT,
                                         Settings.BUTTON_BAR_POS, Settings.BACKGROUND_COLOR))

            self.buttons.append(ButtonFactory.createButtonCentered(program.settings, self.surfaces[-1].surface,
                                                                   Settings.GAME_BG_COLOR, "Start",
                                                                   program.change_to_state, State.PLAY))
        elif self == State.PLAY:
            self.handle_specific_events = self.handle_events_play
            self.sprites = pygame.sprite.Group()

            self.surfaces.append(TiledScalableSurface(program.surface_main, Settings.GAME_DIMENSIONS,
                                                      program.settings.GAME_DIMENSIONS_CURRENT, program.settings.GAME_POS,
                                                      Color.DIM_DARK_GRAY, Settings.LINE_COLOR, Settings.LINE_WIDTH))
            self.surfaces.append(Surface(program.surface_main,
                                         program.settings.BUTTON_BAR_DIMENSIONS_CURRENT,
                                         Settings.BUTTON_BAR_POS, Settings.BACKGROUND_COLOR))

            self.buttons.append(ButtonFactory.createButton(self.surfaces[-1].surface, Settings.BUTTON_POS(0),
                                                           Color.MEDIUM_BLUE, "Pause",
                                                           program.change_to_state, State.PAUSE))
            self.player = Player(
                self.sprites, self.surfaces[0], Color.YELLOW, (0, 0))
        elif self == State.PAUSE:
            self.handle_specific_events = self.handle_events_pause
            self.sprites = self.previous_state.sprites
            [self.surfaces.append(
                s) for s in self.previous_state.surfaces if isinstance(s, TiledScalableSurface)]

            self.surfaces.append(Surface(program.surface_main,
                                         program.settings.BUTTON_BAR_DIMENSIONS_CURRENT,
                                         Settings.BUTTON_BAR_POS, Settings.BACKGROUND_COLOR))

            self.buttons.append(ButtonFactory.createButton(self.surfaces[-1].surface, Settings.BUTTON_POS(0),
                                                           Color.MEDIUM_BLUE, "Resume",
                                                           program.change_to_state, self.previous_state))
            # self.buttons.append(ButtonFactory.createButton(self.surfaces[-1].surface, Settings.BUTTON_POS(5),
            #                                                Color.randomColor(), "A",
            #                                                program.change_to_state, State.PAUSE))
            # self.buttons.append(ButtonFactory.createButton(self.surfaces[-1].surface, Settings.BUTTON_POS(6),
            #                                                Color.randomColor(), "B",
            #                                                program.change_to_state, State.PAUSE))

    def update(self):
        for surface in self.surfaces:
            surface.update()
        for button in self.buttons:
            button.update()
        if self.sprites:
            self.sprites.update()

    def draw(self):
        for surface in self.surfaces:
            surface.surface.fill(surface.fill_color)
        for button in self.buttons:
            button.draw()
        if self.sprites:
            self.sprites.draw(self.surfaces[0].surface)
        for surface in self.surfaces:
            surface.draw()

    def __eq__(self, value):
        return self.name == value

    def handle_events(self, program, events):
        self.handle_specific_events(program, events)

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                for button in self.buttons:
                    if button.hovered:
                        button.click()

    def handle_events_menu(self, program, events):
        for event in events:
            pass

    def handle_events_play(self, program, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                    program.change_to_state(State.PAUSE)
                    break
        move_x, move_y = 0, 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            move_x += -1
        if keys[pygame.K_RIGHT]:
            move_x += 1
        if keys[pygame.K_UP]:
            move_y += -1
        if keys[pygame.K_DOWN]:
            move_y += 1
        self.player.move(move_x, move_y)

    def handle_events_pause(self, program, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                    program.change_to_state(self.previous_state)
                    break

    MENU = "menu"
    PLAY = "play"
    PAUSE = "pause"
    QUIT = "quit"
