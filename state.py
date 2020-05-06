from os import getcwd
import pygame
from random import randint, random
from tkinter import Tk
from tkinter.filedialog import askopenfile, asksaveasfile
from button import ButtonFactory
from gameObjects import Goal, Player, Wall
from surface import Surface, TiledScalableSurface
from settings import Settings


class State:
    def __init__(self, name, program):
        self.draw_game = program.settings.DRAW_GAME
        self.alive_count = 0
        self.name = name
        self.previous_state = program.state
        self.buttons = []
        self.surfaces = []

        self.goal = None
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

            self.goal = Goal(
                (self.all_sprites), self.surfaces[0].tile_size, Settings.GOAL_COLOR, (0, 0))

            self.main_player = Player((self.all_sprites, self.player_sprites), self.acknowledge_death,
                                      self.surfaces[0].tile_size, Settings.PLAYER_COLOR, (0, 0), goal=self.goal, walls=self.wall_sprites, vision_surface=self.surfaces[0])
            # for _ in range(0, 10):
            #     Player((self.all_sprites, self.player_sprites), self.acknowledge_death,
            #            self.surfaces[0].tile_size, Settings.PLAYER_COLOR, (10, 8), goal=self.goal, walls=self.wall_sprites, vision_surface=self.surfaces[0])

            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(3),
                                                            Settings.BUTTON_BG_COLOR, "(P)ause",
                                                            program.change_to_state, State.PAUSE))
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(0),
                                                            Settings.BUTTON_BG_COLOR, "Save", self.save_state))
            self.buttons[-1].active = False
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(1),
                                                            Settings.BUTTON_BG_COLOR, "Load", self.load_state))
            self.buttons[-1].active = False
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(5),
                                                            Settings.BUTTON_BG_COLOR, "Rese(t)", self.reset))
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(4),
                                                            Settings.BUTTON_BG_COLOR, "(R)estart", self.restart))
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(-2),
                                                            Settings.BUTTON_BG_COLOR, self.get_alive_count, None))
            self.buttons[-1].active = False
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(-1),
                                                            Settings.BUTTON_BG_COLOR, program.clock.get_fps, program.limit_fps))
            self.restart()
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

            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(3),
                                                            Settings.BUTTON_BG_COLOR, "Un(p)ause",
                                                            program.change_to_state, self.previous_state))
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(0),
                                                            Settings.BUTTON_BG_COLOR, "Save", self.save_state))
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(1),
                                                            Settings.BUTTON_BG_COLOR, "Load", self.load_state))
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(5),
                                                            Settings.BUTTON_BG_COLOR, "Rese(t)", self.reset))
            self.buttons[-1].active = False
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(4),
                                                            Settings.BUTTON_BG_COLOR, "(R)estart", self.restart))
            self.buttons[-1].active = False
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(-2),
                                                            Settings.BUTTON_BG_COLOR, self.previous_state.get_alive_count, None))
            self.buttons[-1].active = False
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(-1),
                                                            Settings.BUTTON_BG_COLOR, program.clock.get_fps, program.limit_fps))
            self.buttons[-1].active = False

    def update(self):
        for surface in self.surfaces:
            surface.update()
        for button in self.buttons:
            button.update()
        if self == State.PLAY:
            if self.all_sprites:
                self.all_sprites.update()
            if self.alive_count <= 0:
                self.reset()

    def draw(self):
        if self.draw_game:
            for surface in self.surfaces:
                surface.draw()
            for button in self.buttons:
                button.draw()
            if self.all_sprites:
                self.all_sprites.draw(self.surfaces[0].surface)
            if self.player_sprites:
                self.player_sprites.draw(self.surfaces[0].surface)
                [player.brain.draw()
                 for player in self.player_sprites if player.is_alive]
            for surface in self.surfaces:
                surface.blit()
        else:
            self.surfaces[1].draw()
            for button in self.buttons:
                button.draw()
            self.surfaces[1].blit()

    def __eq__(self, value):
        return self.name == value

    def handle_events(self, program, events):
        self.handle_specific_events(program, events)

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                for button in self.buttons:
                    if button.hovered:
                        button.click()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    self.draw_game = not self.draw_game
                    self.surfaces[0].draw()

    def handle_events_menu(self, program, events):
        pass

    def handle_events_play(self, program, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.restart()
                elif event.key == pygame.K_t:
                    self.reset()
                elif event.key == pygame.K_p or event.key == pygame.K_SPACE:
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

    def reset(self):
        [p.die() for p in self.player_sprites]
        [p.resurrect() for p in self.player_sprites]
        [self.all_sprites.add(p) for p in self.player_sprites]
        self.alive_count = len(self.player_sprites)

        move_to(self.player_starting_pos, self.player_sprites)
        # _from = (max(0, int(self.main_player.x - Settings.VISION_DISTANCE * Settings.GOAL_DISTANCE)),
        #          max(0, int(self.main_player.y - Settings.VISION_DISTANCE * Settings.GOAL_DISTANCE)))
        # _to = (max(0, int(self.main_player.x + Settings.VISION_DISTANCE * Settings.GOAL_DISTANCE)),
        #        max(0, int(self.main_player.y + Settings.VISION_DISTANCE * Settings.GOAL_DISTANCE)))
        # put_at_random_empty_space([self.goal], self.main_player.collides_with_wall, _from, _to)

    def restart(self):
        for wall in self.wall_sprites:
            self.all_sprites.remove(wall)
            self.wall_sprites.remove(wall)
        self.spawn_random_walls()

        self.player_starting_pos = put_at_random_empty_space(
            self.player_sprites, self.main_player.collides_with_wall)

        _from = (max(0, int(self.main_player.x - Settings.VISION_DISTANCE * Settings.GOAL_DISTANCE)),
                 max(0, int(self.main_player.y - Settings.VISION_DISTANCE * Settings.GOAL_DISTANCE)))
        _to = (max(0, int(self.main_player.x + Settings.VISION_DISTANCE * Settings.GOAL_DISTANCE)),
               max(0, int(self.main_player.y + Settings.VISION_DISTANCE * Settings.GOAL_DISTANCE)))
        put_at_random_empty_space(
            [self.goal], self.main_player.collides_with_wall, _from, _to)
        self.reset()

    def spawn_random_walls(self):
        for i in range(0, Settings.TILE_COUNT[0]):
            Wall((self.all_sprites, self.wall_sprites),
                 self.surfaces[0].tile_size, Settings.WALL_COLOR, (i, 0))
            Wall((self.all_sprites, self.wall_sprites),
                 self.surfaces[0].tile_size, Settings.WALL_COLOR, (i, Settings.TILE_COUNT[1] - 1))
        for i in range(1, Settings.TILE_COUNT[1] - 1):
            Wall((self.all_sprites, self.wall_sprites),
                 self.surfaces[0].tile_size, Settings.WALL_COLOR, (0, i))
            Wall((self.all_sprites, self.wall_sprites),
                 self.surfaces[0].tile_size, Settings.WALL_COLOR, (Settings.TILE_COUNT[0] - 1, i))

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
                            min_movement, space_left) if axis == 0 else -randint(min_movement, space_left))
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
            self.previous_state.main_player = Player((self.previous_state.all_sprites, self.previous_state.player_sprites), self.previous_state.acknowledge_death, self.previous_state.surfaces[0].tile_size, color, (int(props[2]), int(
                props[3])), (int(props[4]), int(props[5])), goal=self.goal, walls=self.previous_state.wall_sprites, fpm=int(props[7]), move_ticks=int(props[8]), reached_goal=props[10] == "True", vision_surface=self.previous_state.surfaces[0])
            self.previous_state.alive_count += 1
            if props[9] != "True":
                self.previous_state.main_player.die()
        elif props[0] == "W":
            Wall((self.previous_state.all_sprites, self.previous_state.wall_sprites), self.previous_state.surfaces[0].tile_size, color, (int(props[2]), int(
                props[3])), (int(props[4]), int(props[5])), is_movable=props[6] == "True", fpm=int(props[7]), move_ticks=int(props[8]), movement_range=(int(props[9]), int(props[10])), move_dir=int(props[11]))
        elif props[0] == "G":
            self.previous_state.goal = Goal((self.previous_state.all_sprites), self.previous_state.surfaces[0].tile_size, color, (int(props[2]), int(
                props[3])), (int(props[4]), int(props[5])))

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
        for s in self.all_sprites:
            self.all_sprites.remove(s)
        self.previous_state.alive_count = 0

        for line in f:
            self.spawn_from_string(line)

        f.close()

        for p in self.previous_state.player_sprites:
            p.goal = self.previous_state.goal

        self.all_sprites.update()
        self.player_sprites.update()

    def save_state(self):
        Tk().withdraw()
        f = asksaveasfile(title="Save NNNavigator state",
                          initialdir=getcwd() + "/maps",
                          defaultextension=".nnn")
        if f is None:
            return

        f.write(str(self.previous_state.goal) + Settings.PROP_SEP + "\n")
        for player in self.player_sprites:
            f.write(str(player) + Settings.PROP_SEP + "\n")
        for wall in self.wall_sprites:
            f.write(str(wall) + Settings.PROP_SEP + "\n")

        f.close()

    def acknowledge_death(self, player):
        self.all_sprites.remove(player)
        self.alive_count -= 1
        return "ok"

    def get_alive_count(self):
        return self.alive_count

    MENU = "menu"
    PLAY = "play"
    PAUSE = "pause"
    QUIT = "quit"


def put_at_random_empty_space(sprite_list, collision_func, _from=(0, 0), _to=Settings.TILE_COUNT):
    while True:
        random_x = randint(_from[0], _to[0] - 1)
        random_y = randint(_from[1], _to[1] - 1)
        if collision_func(random_x, random_y):
            continue
        move_to((random_x, random_y), sprite_list)
        return (random_x, random_y)


def move_to(coords, list):
    for s in list:
        if hasattr(s, 'is_alive'):
            s.is_alive = True
        was_movable = s.is_movable
        s.is_movable = True
        s.move_ticker = s.frames_per_move + 1
        s.move(coords[0] - s.x, coords[1] - s.y)
        s.is_movable = was_movable
