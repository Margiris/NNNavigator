from os import getcwd
from time import time
from re import split
import pygame
from random import randint, random
from tkinter import Tk
from tkinter.filedialog import askopenfile, asksaveasfilename
from button import ButtonFactory
from gameObjects import Goal, Player, Wall
from surface import Surface, TiledScalableSurface
from settings import Settings
from brain import TensorBoard
import Astar
import numpy


class State:
    MODEL_NAME = 'NNNavigator-Genetic'

    # Environment settings
    EPISODES = 20_000
    STEPS_PER_EPISODE = 200 * Settings.FRAMES_PER_MOVE
    MUTATE_EVERY = 5
    MUTATION_RATE = 0.01

    AGENT_COUNT = 50

    # scores = {
    #     # "total": [None for _ in range(EPISODES)],
    #     # "progress": [None for _ in range(EPISODES)],
    #     "max": [None for _ in range(EPISODES)],
    #     "avg": [None for _ in range(EPISODES)],
    #     "min": [None for _ in range(EPISODES)]
    # }

    def __init__(self, name, program):
        self.draw_game = program.settings.DRAW_GAME
        self.generation = 0
        self.episode = 0
        self.episode_step = 0
        self.alive_count = 0
        self.updates = 1
        self.name = name
        self.previous_state = program.state
        self.buttons = []
        self.surfaces = []

        self.goal = None
        self.main_player = None

        self.all_sprites = None
        self.player_sprites = None
        self.wall_sprites = None

        self.tensorboard = TensorBoard(
            log_dir="logs/{}-{}".format(self.MODEL_NAME, int(time())))

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

            # self.main_player = Player((self.all_sprites, self.player_sprites), self.acknowledge_death,
            #                           self.surfaces[0].tile_size, Settings.PLAYER_COLOR, (0, 0), goal=self.goal, walls=self.wall_sprites, vision_surface=self.surfaces[0])
            for _ in range(0, self.AGENT_COUNT):
                Player((self.all_sprites, self.player_sprites), self.acknowledge_death,
                       self.surfaces[0].tile_size, Settings.PLAYER_COLOR, (0, 0), goal=self.goal, walls=self.wall_sprites, vision_surface=self.surfaces[0])

            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(2),
                                                            Settings.BUTTON_BG_COLOR, "(P)ause",
                                                            program.change_to_state, State.PAUSE))
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(0),
                                                            Settings.BUTTON_BG_COLOR, "Save", self.save_state))
            self.buttons[-1].active = False
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(1),
                                                            Settings.BUTTON_BG_COLOR, "Load", self.load_state))
            self.buttons[-1].active = False
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(4),
                                                            Settings.BUTTON_BG_COLOR, "Rese(t)", self.reset))
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(3),
                                                            Settings.BUTTON_BG_COLOR, "(R)estart", self.restart))
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(-3),
                                                            Settings.BUTTON_BG_COLOR, self.get_celebrations, None))
            self.buttons[-1].active = False
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(-2),
                                                            Settings.BUTTON_BG_COLOR, self.get_episode, self.toggle_game_draw))
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(-1),
                                                            Settings.BUTTON_BG_COLOR, program.get_fps, program.limit_fps))
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

            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(2),
                                                            Settings.BUTTON_BG_COLOR, "Un(p)ause",
                                                            program.change_to_state, self.previous_state))
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(0),
                                                            Settings.BUTTON_BG_COLOR, "Save", self.save_state))
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(1),
                                                            Settings.BUTTON_BG_COLOR, "Load", self.load_state))
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(4),
                                                            Settings.BUTTON_BG_COLOR, "Rese(t)", self.reset))
            self.buttons[-1].active = False
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(3),
                                                            Settings.BUTTON_BG_COLOR, "(R)estart", self.restart))
            self.buttons[-1].active = False
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(-3),
                                                            Settings.BUTTON_BG_COLOR, self.previous_state.get_celebrations, None))
            self.buttons[-1].active = False
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(-2),
                                                            Settings.BUTTON_BG_COLOR, self.previous_state.get_episode, self.toggle_game_draw))
            self.buttons[-1].active = False
            self.buttons.append(ButtonFactory.create_button(self.surfaces[-1].surface, Settings.BUTTON_POS(-1),
                                                            Settings.BUTTON_BG_COLOR, program.get_fps, program.limit_fps))
            self.buttons[-1].active = False

    def update(self):
        for surface in self.surfaces:
            surface.update()
        for button in self.buttons:
            button.update()
        if self == State.PLAY:
            if self.all_sprites:
                self.all_sprites.update()

            self.episode_step += 1

            self.updates += 1

            if self.alive_count <= 0 or self.episode_step > self.STEPS_PER_EPISODE:
                if self.episode > self.EPISODES:
                    exit(0)
                if not self.episode % self.MUTATE_EVERY:
                    self.restart()
                else:
                    self.reset()

    def make_new_generation(self):
        if self.generation <= 0:
            self.generation += 1
            return
        total_score = sum([p.brain.score for p in self.player_sprites])

        if total_score == 0:
            return

        gen_max = max([p.brain.score for p in self.player_sprites])
        gen_avg = total_score / self.AGENT_COUNT
        gen_min = min([p.brain.score for p in self.player_sprites])

        self.tensorboard.update_stats(max=gen_max, avg=gen_avg, min=gen_min)

        for p in self.player_sprites:
            p.brain.fitness = p.brain.score / total_score

        new_generation_weights = []

        for _ in range(self.AGENT_COUNT):
            parent1 = self.get_one_player()
            parent2 = self.get_one_player()
            new_generation_weights.append(mutate(crossover(parent1, parent2)))

        for p in self.player_sprites:
            p.brain.model.set_weights(new_generation_weights.pop())
            p.brain.score = 0

        self.generation += 1
        self.tensorboard.step = self.generation

    def get_one_player(self):
        index = 0
        random_num = random()
        for p in self.player_sprites:
            random_num -= p.brain.fitness
            if random_num <= 0:
                return p

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
        elif self.surfaces:
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
                    self.toggle_game_draw()

    def toggle_game_draw(self):
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

    def handle_events_pause(self, program, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                    program.change_to_state(self.previous_state)
                    break

    def reset(self):
        self.episode += 1
        self.episode_step = 0
        self.finished_count = 0

        [p.die() for p in self.player_sprites if p.is_alive]
        [p.resurrect() for p in self.player_sprites]
        [self.all_sprites.add(p) for p in self.player_sprites]
        self.alive_count = len(self.player_sprites)

        for player in self.player_sprites:
            move_to(player.starting_pos, [player])
        self.respawn_goal()

    def restart(self):
        self.make_new_generation()
        for wall in self.wall_sprites:
            self.all_sprites.remove(wall)
            self.wall_sprites.remove(wall)
        self.spawn_random_walls()

        for player in self.player_sprites:
            player.starting_pos = put_at_random_empty_space(
                [player], self.collides_with_anything)
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
                    limit = random_spot + length if random_spot + length < tile_count else tile_count
                    for i in range(random_spot, limit):
                        Wall((self.all_sprites, self.wall_sprites), self.surfaces[0].tile_size, color, (i, line) if axis == 0 else (
                            line, i), is_movable=movable, fpm=speed, movement_range=movement_range)

    def spawn_from_string(self, obj_data):
        props = obj_data.split(Settings.PROP_SEP)
        color = tuple(int(c) for c in props[1].split(','))
        if props[0] == "P":
            model_filename = props[11] if len(props) == 13 else None
            self.previous_state.main_player = Player((self.previous_state.all_sprites, self.previous_state.player_sprites), self.previous_state.acknowledge_death, self.previous_state.surfaces[0].tile_size, color, (int(props[2]), int(
                props[3])), (int(props[4]), int(props[5])), goal=self.previous_state.goal, walls=self.previous_state.wall_sprites, fpm=int(props[7]), move_ticks=int(props[8]), reached_goal=props[10] == "True", vision_surface=self.previous_state.surfaces[0], model_name=model_filename)
            self.previous_state.alive_count += 1
            if props[9] != "True":
                self.previous_state.main_player.die()
            self.previous_state.buttons[-3].text = self.previous_state.main_player.get_celebrations
            self.previous_state.buttons[-2].text = self.previous_state.main_player.brain.get_episode

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
        files = [('Neural Network Navigator file', '*.nnn')]
        f = asksaveasfilename(title="Save NNNavigator state",
                              initialdir=getcwd() + "/maps",
                              defaultextension=files, filetypes=files)
        if f is None or f == '':
            return
        timestamp = str(int(time()))

        f = split('(\.)', f)
        model_filename = "".join(f[:-3])
        f = f[:-2] + ['_', timestamp] + f[-2:]
        f = "".join(f)

        with open(f, 'w') as f:
            f.write(str(self.previous_state.goal) + Settings.PROP_SEP + "\n")
            for player in self.player_sprites:
                # model_filename = player.brain.save_model(
                #     filename=model_filename)
                f.write(str(player) + Settings.PROP_SEP +
                        model_filename + Settings.PROP_SEP + "\n")
            for wall in self.wall_sprites:
                f.write(str(wall) + Settings.PROP_SEP + "\n")

        # f.close()

    def acknowledge_death(self, player):
        if self.updates:
            self.updates = 0
            self.map = numpy.zeros(Settings.TILE_COUNT, dtype=numpy.int8)
            for wall in self.wall_sprites:
                self.map[wall.x][wall.y] = 1

        steps_total_a_star = self.steps_to_goal_Astar(player.starting_pos)

        if player.brain.reached_goal:
            self.finished_count += 1
            steps_diff = self.episode_step - \
                len(steps_total_a_star) if steps_total_a_star else -1

            if steps_diff < 0:
                # this means agent did better than A*
                score = 2 + 1 / -steps_diff
            else:
                score = 1 + 1 / steps_diff
        else:
            # if agebt didn't finish and goal can be reached by A*, set score to ration between distance left and total,
            # otherwise add straight-line distance to score.
            # If agent got farther from goal than it's start, add 0 to score
            steps_left_a_star = self.steps_to_goal_Astar((player.x, player.y))
            if steps_left_a_star and steps_total_a_star:
                if len(steps_left_a_star) >= len(steps_total_a_star):
                    score = 0
                else:
                    score = len(steps_total_a_star) / \
                        len(steps_left_a_star) - 1
            else:
                score = 0.01 / player.look_8_ways()[8]
        player.brain.score += score

        self.all_sprites.remove(player)
        self.alive_count -= 1

    def steps_to_goal_Astar(self, pos):
        return Astar.astar(self.map, pos, (self.goal.x, self.goal.y))

    def respawn_goal(self):
        _from = (Settings.TILE_COUNT[0] * 2 / 4,
                 Settings.TILE_COUNT[1] * 2 / 4)
        _to = (Settings.TILE_COUNT[0] * 3 / 4,
               Settings.TILE_COUNT[1] * 3 / 4)
        put_at_random_empty_space(
            [self.goal], self.collides_with_anything, _from, _to)

    def get_alive_count(self):
        return self.alive_count

    def get_celebrations(self):
        return '{:3.0f}%|{:3.0f}%'.format(self.finished_count / self.AGENT_COUNT * 100, self.alive_count / self.AGENT_COUNT * 100)

    def get_episode(self):
        return '{:>d}/{:>d}/{:>3d}'.format(self.generation, self.episode, self.episode_step)

    def collides_with_anything(self, x, y):
        for a in self.all_sprites:
            if a.x == x and a.y == y:
                return True
        return False

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
        was_move_ticker = s.move_ticker
        s.move_ticker = s.frames_per_move + 1
        s.move(coords[0] - s.x, coords[1] - s.y)
        s.is_movable = was_movable
        s.move_ticker = was_move_ticker


def crossover(player1, player2):
    new_weights = player1.brain.model.get_weights()
    old_weights = player2.brain.model.get_weights()

    # iterate through every other array because we need to skip bias arrays
    for array in range(0, len(old_weights), 2):
        for dimm in range(len(old_weights[array])):
            for i in range(len(old_weights[array][dimm])):
                if random() > 0.5:
                    new_weights[array][dimm][i] = old_weights[array][dimm][i]

    return new_weights


def mutate(weights):
    # iterate through every other array because we need to skip bias arrays
    for array in range(0, len(weights), 2):
        for dimm in weights[array]:
            for i in dimm:
                if random() < State.MUTATION_RATE:
                    i += random()
    return weights
