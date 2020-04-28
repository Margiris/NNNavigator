import pygame
from random import randint, random
from button import ButtonFactory
from color import Color
from gameObjects import Player, Wall
from surface import Surface, TiledScalableSurface
from settings import Settings


class State:
    def __init__(self, name, program):
        self.enum = []
        self.name = name
        self.previous_state = program.state
        self.setup_buttons_sprites_and_surfaces(program)

    def setup_buttons_sprites_and_surfaces(self, program):
        self.buttons = []
        self.surfaces = []
        self.player = None
        self.all_sprites = None
        self.wall_sprites = None

        if self == State.MENU:
            self.handle_specific_events = self.handle_events_menu

            self.surfaces.append(Surface(program.surface_main,
                                         program.settings.BUTTON_BAR_DIMENSIONS_CURRENT,
                                         Settings.BUTTON_BAR_POS, Settings.BACKGROUND_COLOR))

            self.buttons.append(ButtonFactory.create_button_centered(program.settings, self.surfaces[-1].surface,
                                                                     Settings.GAME_BG_COLOR, "Start",
                                                                     program.change_to_state, State.PLAY))
        elif self == State.PLAY:
            self.handle_specific_events = self.handle_events_play
            self.all_sprites = pygame.sprite.Group()
            self.wall_sprites = pygame.sprite.Group()

            self.surfaces.append(TiledScalableSurface(program.surface_main, Settings.GAME_DIMENSIONS,
                                                      program.settings.GAME_DIMENSIONS_CURRENT, program.settings.GAME_POS,
                                                      Color.DIM_DARK_GRAY, Settings.LINE_COLOR, Settings.LINE_WIDTH))
            self.surfaces.append(Surface(program.surface_main,
                                         program.settings.BUTTON_BAR_DIMENSIONS_CURRENT,
                                         Settings.BUTTON_BAR_POS, Settings.BACKGROUND_COLOR))

            self.player = Player(
                self.all_sprites, self.surfaces[0].tile_size, Color.YELLOW, (0, 0), walls=self.wall_sprites)

            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(0),
                                                            Color.MEDIUM_BLUE, "Pause",
                                                            program.change_to_state, State.PAUSE))
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(5),
                                                            Color.NAVY, "Respawn w",
                                                            self.respawn_random_walls))
            self.spawn_random_walls()

        elif self == State.PAUSE:
            self.handle_specific_events = self.handle_events_pause
            self.all_sprites = self.previous_state.all_sprites
            self.wall_sprites = self.previous_state.wall_sprites

            [self.surfaces.append(
                s) for s in self.previous_state.surfaces if isinstance(s, TiledScalableSurface)]

            self.surfaces.append(Surface(program.surface_main,
                                         program.settings.BUTTON_BAR_DIMENSIONS_CURRENT,
                                         Settings.BUTTON_BAR_POS, Settings.BACKGROUND_COLOR))

            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(0),
                                                            Color.MEDIUM_BLUE, "Resume",
                                                            program.change_to_state, self.previous_state))
            # self.buttons.append(ButtonFactory.createButton(self.surfaces[-1].surface, Settings.BUTTON_POS(6),
            #                                                Color.randomColor(), "B",
            #                                                program.change_to_state, State.PAUSE))

    def update(self):
        for surface in self.surfaces:
            surface.update()
        for button in self.buttons:
            button.update()
        if self.all_sprites:
            self.all_sprites.update()

    def draw(self):
        for surface in self.surfaces:
            surface.draw()
        for button in self.buttons:
            button.draw()
        if self.all_sprites:
            self.all_sprites.draw(self.surfaces[0].surface)
        for surface in self.surfaces:
            surface.blit()

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
        pass
        # for event in events:

    def handle_events_play(self, program, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.player.resurrect()
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

    def respawn_random_walls(self):
        for wall in self.wall_sprites:
            self.all_sprites.remove(wall)
            self.wall_sprites.remove(wall)
        self.spawn_random_walls()

    def spawn_random_walls(self):
        for axis in range(0, 2):
            tile_count = Settings.TILE_COUNT[axis]

            for line in range(0, Settings.TILE_COUNT[1 - axis] - 1):
                if random() < Settings.WALL_SPAWN_RATE:
                    random_spot = randint(0, tile_count - 1)
                    length = randint(
                        0, int((tile_count - 1) * random()))
                    space_left = tile_count - random_spot - length
                    min_movement = 10

                    if random() < Settings.MOVING_WALL_SPAWN_RATE and space_left > min_movement:
                        color = Color.CORN_FLOWER_BLUE
                        movable = True
                        upper = randint(min_movement, space_left)
                        movement_range = (0, upper if axis == 0 else 0 - upper)
                        # print(movement_range, (random_spot, line)
                        #       if axis == 0 else (line, random_spot))
                    else:
                        color = Color.STEEL_BLUE
                        movable = False
                        movement_range = (0, 0)

                    for i in range(random_spot, random_spot + length):
                        Wall((self.all_sprites, self.wall_sprites), self.surfaces[0].tile_size, color, (i, line) if axis == 0 else (
                            line, i), is_movable=movable, fpm=1, movement_range=movement_range)

    MENU = "menu"
    PLAY = "play"
    PAUSE = "pause"
    QUIT = "quit"
