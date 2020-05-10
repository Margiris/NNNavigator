import numpy
from pygame import Surface, draw
import random
from time import time

from collections import deque
from keras.callbacks import Callback
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Activation, Flatten
from keras.optimizers import Adam
import tensorflow as tf

from settings import Settings


class VisionSurface:
    def __init__(self, tile_size, color, coords, surface):
        surface_size = ((Settings.VISION_DISTANCE * 2 + 1) * tile_size[0],
                        (Settings.VISION_DISTANCE * 2 + 1) * tile_size[1])
        self.parent_surface = surface
        self.surface = Surface(surface_size)
        self.surface.set_alpha(20)
        self.x, self.y = coords
        self.tile_size = tile_size
        self.color = color

    def draw(self):
        self.surface.fill(self.color)
        self.parent_surface.blit(self.surface, (self.x * self.tile_size[0],
                                                self.y * self.tile_size[1]))

    def move(self, dx=0, dy=0):
        self.x += dx
        self.y += dy


class Brain:
    OBSERVATION_SPACE_VALUES = (10,)
    action_space = {
        0: (0, 0),
        1: (0, -1),
        2: (1, 0),
        3: (0, 1),
        4: (-1, 0),
    }
    ACTION_SPACE_SIZE = len(action_space)

    def __init__(self, player, surface, reached_goal, file=None):
        self.fitness = 0
        self.score = 0
        self.episode_step = 0
        self.player = player
        self.surface = surface
        self.reached_goal = reached_goal

        # coords = (self.player.x - Settings.VISION_DISTANCE,
        #           self.player.y - Settings.VISION_DISTANCE)
        # self.visionSprite = VisionSurface(
        #     surface.tile_size, player.color, coords, surface.surface)

        # Main model
        if file:
            self.model = load_model(file)
        else:
            self.model = self.create_model_flat()

    def update(self):
        if self.player.move_ticker <= self.player.frames_per_move:
            return

        action_index = self.predict_action()

        self.player.move(*self.action_space[action_index])

    def move(self, dx=0, dy=0):
        # self.visionSprite.move(dx, dy)
        pass

    def predict_action(self):
        vision = self.player.look_8_ways()
        input_data = numpy.atleast_2d(numpy.asarray(vision))

        return numpy.argmax(self.model.predict(input_data, 1)[0])

    def draw(self):
        # self.visionSprite.draw()
        start_pos = (self.player.rect[0] + self.player.tile_size[0] / 2,
                     self.player.rect[1] + self.player.tile_size[1] / 2)
        # start_pos = (self.player.rect[0], self.player.rect[1])
        for direction, coord in self.player.DIRECTIONS.items():
            end_pos = (start_pos[0] + coord[0] * self.player.vision_distance[direction] * self.player.tile_size[0] * Settings.VISION_DISTANCE,
                       start_pos[1] + coord[1] * self.player.vision_distance[direction] * self.player.tile_size[1] * Settings.VISION_DISTANCE)
            draw.line(self.surface.surface,
                      Settings.PLAYER_VISION_COLOR, start_pos, end_pos)
        end_pos = (self.player.goal.rect[0] + self.player.tile_size[0] / 2,
                   self.player.goal.rect[1] + self.player.tile_size[1] / 2)
        draw.line(self.surface.surface,
                  Settings.GOAL_COLOR, start_pos, end_pos)

    def die(self):
        self.score = self.player.look_8_ways()[8]

    def resurrect(self):
        self.reached_goal = False

    def __str__(self):
        return Settings.TUPLE_SEP.join([str(self.reached_goal), str(self.score), str(self.fitness)])

    def create_model(self):
        model = Sequential()

        # OBSERVATION_SPACE_VALUES = (10, 10, 3) a 10x10 RGB image.
        model.add(Conv2D(256, (3, 3), input_shape=self.OBSERVATION_SPACE_VALUES))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.2))

        model.add(Conv2D(256, (3, 3)))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.2))

        # this converts our 3D feature maps to 1D feature vectors
        model.add(Flatten())
        model.add(Dense(64))

        # ACTION_SPACE_SIZE = how many choices (9)
        model.add(Dense(self.ACTION_SPACE_SIZE, activation='linear'))
        model.compile(loss="mse", optimizer=Adam(
            lr=0.001), metrics=['accuracy'])
        return model

    def create_model_flat(self):
        model = Sequential()

        model.add(
            Dense(128, input_shape=self.OBSERVATION_SPACE_VALUES))
        model.add(Dense(128, activation='sigmoid'))
        model.add(Dense(128, activation='sigmoid'))
        # model.add(Dense(self.ACTION_SPACE_SIZE, activation='softmax'))
        model.add(Dense(self.ACTION_SPACE_SIZE, activation='sigmoid'))
        model.compile(loss="mse", optimizer=Adam(
            lr=0.001), metrics=['accuracy'])
        return model

    def save_model(self, max_reward=None, average_reward=None, min_reward=None, filename=None):
        if filename:
            filename = 'models/{}.nnnm'.format(filename.split('/')[-1])
        else:
            filename = 'models/{:_>7.2f}max_{:_>7.2f}avg_{:_>7.2f}min_{}.nnnm'.format(
                max_reward, average_reward, min_reward, int(time()))
        self.model.save(filename)
        return filename

# Own Tensorboard class


class TensorBoard(Callback):

    # Set initial step and writer (we want one log file for all .fit() calls)
    def __init__(self, log_dir):
        self.step = 1
        self.log_dir = log_dir
        self.writer = tf.summary.create_file_writer(self.log_dir)

    # Saves logs with our step number (otherwise every .fit() will start writing from 0th step)
    def on_epoch_end(self, epoch, logs=None):
        self.update_stats(**logs)

    # Custom method for saving own (and also internal) metrics (can be called externally)
    def update_stats(self, **stats):
        self._write_logs(stats, self.step)

    # More or less the same writer as in Keras' Tensorboard callback
    # Physically writes to the log files
    def _write_logs(self, logs, index):
        for name, value in logs.items():
            if name in ['batch', 'size']:
                continue
            with self.writer.as_default():
                tf.summary.scalar(name, value, step=index)
