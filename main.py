import pygame
from pygame.locals import *
from settings import Settings
from state import State


class Program:
    def __init__(self):
        self.settings = Settings()
        pygame.init()
        self.clock = pygame.time.Clock()

        self.surface_main = pygame.display.set_mode(
            self.settings.WINDOW_SIZE, DOUBLEBUF | RESIZABLE)
        pygame.display.set_caption(self.settings.WINDOW_TITLE)
        # pygame.key.set_repeat(500, 50)

        self.state = None
        self.change_to_state(State.PLAY)

    def change_to_state(self, state):
        if isinstance(state, State):
            self.state = state
        else:
            self.state = State(state, self)

        if self.state == State.PAUSE:
            self.pause()

    def run(self):
        while self.state != State.QUIT:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.settings.MAX_FPS)

        # pygame.quit()
        # sys.exit()

    def pause(self):
        while self.state == State.PAUSE:
            self.handle_events()
            self.state.update()
            self.draw()
            self.clock.tick(self.settings.MIN_FPS)

    def handle_events(self):
        events = pygame.event.get()
        self.state.handle_events(self, events)

        for event in events:
            if event.type == pygame.QUIT:
                self.change_to_state(State.QUIT)
            elif event.type == VIDEORESIZE:
                self.resize(event.dict['size'])
                self.resize(event.dict['size'])
            # elif event.type == pygame.KEYDOWN:
            #     pass

    def update(self):
        self.state.update()

    def draw(self):
        self.surface_main.fill(self.settings.BACKGROUND_COLOR)
        self.state.draw()
        pygame.display.flip()

    def resize(self, size):
        self.settings.WINDOW_SIZE_CURRENT = (
            size[0] if size[0] >= self.settings.WINDOW_SIZE_MINIMUM[0] else self.settings.WINDOW_SIZE_CURRENT[0],
            size[1] if size[1] >= self.settings.WINDOW_SIZE_MINIMUM[1] else self.settings.WINDOW_SIZE_CURRENT[1])

        self.surface_main = pygame.display.set_mode(
            self.settings.WINDOW_SIZE_CURRENT, DOUBLEBUF | RESIZABLE)
        # self.surface_main.fill(self.settings.BACKGROUND_COLOR)
        self.draw()

    def limit_fps(self):
        if self.settings.MAX_FPS > 60:
            self.settings.MAX_FPS = 60
        else:
            self.settings.MAX_FPS *= 10


if __name__ == "__main__":
    NNNavigator = Program()
    NNNavigator.run()
