from os import getcwd
import pygame
from random import randint, random
from tkinter import Tk
from tkinter.filedialog import askopenfile, asksaveasfile
from button import ButtonFactory
from gameObjects import Player, Wall
from surface import Surface, TiledScalableSurface
from settings import Settings


class State:
    def __init__(self, name, program):
        self.name = name
        self.previous_state = program.state
        self.buttons = []
        self.surfaces = []
        self.main_player = None
        self.all_sprites = None
        self.player_sprites = None
        self.wall_sprites = None

        if self == State.MENU:
            self.handle_specific_events = self.handle_events_menu

            self.surfaces.append(Surface(program.surface_main,
                                         program.settings.BUTTON_BAR_DIMENSIONS_CURRENT,
                                         Settings.BUTTON_BAR_POS))

            self.buttons.append(ButtonFactory.create_button_centered(program.settings, self.surfaces[-1].surface,
                                                                     Settings.GAME_BG_COLOR, "Start",
                                                                     program.change_to_state, State.PLAY))
        elif self == State.PLAY:
            self.handle_specific_events = self.handle_events_play
            self.all_sprites = pygame.sprite.Group()
            self.player_sprites = pygame.sprite.Group()
            self.wall_sprites = pygame.sprite.Group()

            self.surfaces.append(TiledScalableSurface(program.surface_main, Settings.GAME_DIMENSIONS,
                                                      program.settings.GAME_DIMENSIONS_CURRENT, program.settings.GAME_POS,
                                                      Settings.GAME_BG_COLOR, Settings.LINE_COLOR, Settings.LINE_WIDTH))
            self.surfaces.append(Surface(
                program.surface_main, program.settings.BUTTON_BAR_DIMENSIONS_CURRENT, Settings.BUTTON_BAR_POS))

            for _ in range(0, 10):
                Player((self.all_sprites, self.player_sprites),
                       self.surfaces[0].tile_size, Settings.PLAYER_COLOR, (10, 8), walls=self.wall_sprites)
            self.main_player = Player(
                (self.all_sprites, self.player_sprites), self.surfaces[0].tile_size, Settings.PLAYER_COLOR, (0, 0), walls=self.wall_sprites)

            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(-4),
                                                            Settings.BUTTON_BG_COLOR, "Pause",
                                                            program.change_to_state, State.PAUSE))
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(0),
                                                            Settings.BUTTON_BG_COLOR, "Load", self.load_state))
            self.buttons[-1].active = False
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(1),
                                                            Settings.BUTTON_BG_COLOR, "Save", self.save_state))
            self.buttons[-1].active = False
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(-3),
                                                            Settings.BUTTON_BG_COLOR, "Restart", self.restart))
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(-1),
                                                            Settings.BUTTON_BG_COLOR, program.clock.get_fps, program.limit_fps))
            self.spawn_random_walls()
        elif self == State.PAUSE:
            self.handle_specific_events = self.handle_events_pause
            self.all_sprites = self.previous_state.all_sprites
            self.player_sprites = self.previous_state.player_sprites
            self.wall_sprites = self.previous_state.wall_sprites

            [self.surfaces.append(
                s) for s in self.previous_state.surfaces if isinstance(s, TiledScalableSurface)]

            self.surfaces.append(Surface(program.surface_main,
                                         program.settings.BUTTON_BAR_DIMENSIONS_CURRENT,
                                         Settings.BUTTON_BAR_POS, Settings.BACKGROUND_COLOR))

            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(-4),
                                                            Settings.BUTTON_BG_COLOR, "Resume",
                                                            program.change_to_state, self.previous_state))
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(0),
                                                            Settings.BUTTON_BG_COLOR, "Load", self.load_state))
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(1),
                                                            Settings.BUTTON_BG_COLOR, "Save", self.save_state))
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(-3),
                                                            Settings.BUTTON_BG_COLOR, "Restart", self.restart))
            self.buttons[-1].active = False
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(-1),
                                                            Settings.BUTTON_BG_COLOR, program.clock.get_fps, program.limit_fps))
            self.buttons[-1].active = False

    def update(self):
        for surface in self.surfaces:
            surface.update()
        for button in self.buttons:
            button.update()
        if self != State.PAUSE:
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

    def handle_events_play(self, program, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.restart()
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
        if move_x or move_y:
            self.main_player.move(move_x, move_y)

    def handle_events_pause(self, program, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                    program.change_to_state(self.previous_state)
                    break

    def restart(self):
        for wall in self.wall_sprites:
            self.all_sprites.remove(wall)
            self.wall_sprites.remove(wall)
        self.spawn_random_walls()

        [p.die() for p in self.player_sprites]
        while any([not player.is_alive for player in self.player_sprites]):
            random_x = randint(0, Settings.TILE_COUNT[0] - 1)
            random_y = randint(0, Settings.TILE_COUNT[1] - 1)
            for player in self.player_sprites:
                player.resurrect()
                player.move(random_x - player.x, random_y - player.y)

    def spawn_random_walls(self):
        min_movement = 2
        min_length = 3
        for times in range(0, 4):
            axis = times % 2
            tile_count = Settings.TILE_COUNT[axis]

            for line in range(0, Settings.TILE_COUNT[1 - axis] - 1):
                if random() < Settings.WALL_SPAWN_RATE:
                    random_spot = randint(0, tile_count - 1)
                    length = randint(min_length,
                                     min_length + int((tile_count - 1) * random() / 2))
                    space_left = tile_count - random_spot - length

                    if random() < Settings.MOVING_WALL_SPAWN_RATE and space_left > min_movement:
                        color = Settings.MOVING_WALL_COLOR
                        movable = True
                        movement_range = (0, randint(
                            min_movement, space_left) if axis == 0 else 0 - randint(min_movement, space_left))
                    else:
                        color = Settings.WALL_COLOR
                        movable = False
                        movement_range = (0, 0)

                    speed = randint(1, Settings.MAX_FPS)
                    for i in range(random_spot, random_spot + length):
                        Wall((self.all_sprites, self.wall_sprites), self.surfaces[0].tile_size, color, (i, line) if axis == 0 else (
                            line, i), is_movable=movable, fpm=speed, movement_range=movement_range)

    def spawn_from_string(self, obj_data):
        props = obj_data.split(Settings.PROP_SEP)
        color = tuple(int(c) for c in props[1].split(','))
        if props[0] == "P":
            self.previous_state.main_player = Player((self.all_sprites, self.player_sprites), self.surfaces[0].tile_size, color, (int(props[2]), int(
                props[3])), (int(props[4]), int(props[5])), walls=self.wall_sprites, fpm=int(props[7]), move_ticks=int(props[8]))
            if props[9] != "True":
                self.previous_state.main_player.die()
        elif props[0] == "W":
            Wall((self.all_sprites, self.wall_sprites), self.surfaces[0].tile_size, color, (int(props[2]), int(
                props[3])), (int(props[4]), int(props[5])), is_movable=props[6] == "True", fpm=int(props[7]), move_ticks=int(props[8]), movement_range=(int(props[9]), int(props[10])), move_dir=int(props[11]))

    def load_state(self):
        Tk().withdraw()
        f = askopenfile(title="Open NNNavigator state file",
                        initialdir=getcwd() + "/maps",
                        filetypes=[("NNNavigator state file", ".nnn")])
        if f is None:
            return

        for player in self.player_sprites:
            self.all_sprites.remove(player)
            self.player_sprites.remove(player)
        for wall in self.wall_sprites:
            self.all_sprites.remove(wall)
            self.wall_sprites.remove(wall)

        for line in f:
            self.spawn_from_string(line)

        f.close()

        self.all_sprites.update()

    def save_state(self):
        Tk().withdraw()
        f = asksaveasfile(title="Save NNNavigator state",
                          initialdir=getcwd() + "/maps",
                          defaultextension=".nnn")
        if f is None:
            return

        for player in self.player_sprites:
            f.write(str(player) + Settings.PROP_SEP + "\n")
        for wall in self.wall_sprites:
            f.write(str(wall) + Settings.PROP_SEP + "\n")

        f.close()

    MENU = "menu"
    PLAY = "play"
    PAUSE = "pause"
    QUIT = "quit"
