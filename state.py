import pygame
from button import Button, ButtonFactory
from color import Color
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

        if self == State.MENU:
            self.handle_specific_events = self.handle_events_menu

            self.surfaces.append(Surface(program.surface_main,
                                         program.settings.BUTTON_BAR_DIMENSIONS_CURRENT,
                                         Settings.BUTTON_BAR_POS, Settings.BACKGROUND_COLOR))
            #  Settings.BUTTON_BAR_POS, Color.DARK_SLATE_GRAY))

            self.buttons.append(ButtonFactory.createButtonCentered(program.settings, self.surfaces[-1].surface,
                                                                   Settings.GAME_BG_COLOR, "Start",
                                                                   program.change_to_state, State.PLAY))
        elif self == State.PLAY:
            self.handle_specific_events = self.handle_events_play

            self.surfaces.append(TiledScalableSurface(program.surface_main, Settings.GAME_DIMENSIONS,
                                                      program.settings.GAME_DIMENSIONS_CURRENT, program.settings.GAME_POS,
                                                      Color.DIM_DARK_GRAY, Settings.LINE_COLOR, Settings.LINE_WIDTH))
            self.surfaces.append(Surface(program.surface_main,
                                         program.settings.BUTTON_BAR_DIMENSIONS_CURRENT,
                                         Settings.BUTTON_BAR_POS, Settings.BACKGROUND_COLOR))
            #  Settings.BUTTON_BAR_POS, Color.DARK_SLATE_GRAY))

            self.buttons.append(ButtonFactory.createButton(self.surfaces[-1].surface, Settings.BUTTON_POS(0),
                                                           Color.MEDIUM_BLUE, "Pause",
                                                           program.change_to_state, State.PAUSE))

        elif self == State.PAUSE:
            self.handle_specific_events = self.handle_events_pause
            # self.surfaces = self.previous_state.surfaces
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

    def draw(self):
        for surface in self.surfaces:
            surface.surface.fill(surface.fill_color)
        for button in self.buttons:
            button.draw()
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

    def handle_events_pause(self, program, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                    program.change_to_state(self.previous_state)

    MENU = "menu"
    PLAY = "play"
    PAUSE = "pause"
    QUIT = "quit"
