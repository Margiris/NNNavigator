import pygame
from button import Button, ButtonFactory
from color import Color
from surface import GameSurface
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
            self.buttons.append(ButtonFactory.createStartButton(
                program.settings, program.surface_main, "Start", program.change_to_state, State.PLAY))
        elif self == State.PLAY:
            self.handle_specific_events = self.handle_events_play
            self.buttons.append(ButtonFactory.createPauseButton(
                program.surface_main, "Pause", program.change_to_state, State.PAUSE))
            # self.buttons.append(ButtonFactory.createStartButton(
            #     program.surface_main, "Menu", program.change_to_state, self.previous_state))

            self.surfaces.append(GameSurface(
                program.surface_main, program.settings.GAME_DIMENSIONS_CURRENT, program.settings.GAME_POS, Color.DIM_DARK_GRAY, Settings.LINE_COLOR, Settings.LINE_WIDTH))
            print(self.surfaces[0].size)
        elif self == State.PAUSE:
            self.handle_specific_events = self.handle_events_pause
            self.buttons.append(ButtonFactory.createPauseButton(
                program.surface_main, "Resume", program.change_to_state, self.previous_state))
            self.buttons.append(ButtonFactory.createAButton(
                program.surface_main, Settings.BUTTON_POS_TOP_2, "A", program.change_to_state, State.PAUSE))
            self.buttons.append(ButtonFactory.createAButton(
                program.surface_main, Settings.BUTTON_POS_TOP_3, "B", program.change_to_state, State.PAUSE))

            self.surfaces = self.previous_state.surfaces

    def update(self):
        for surface in self.surfaces:
            surface.update()
        for button in self.buttons:
            button.update()

    def draw(self):
        for surface in self.surfaces:
            surface.draw()
        for button in self.buttons:
            button.draw()

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
