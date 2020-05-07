import numpy
from pygame import Surface
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
    # Agent class

    DISCOUNT = 0.99
    REPLAY_MEMORY_SIZE = 50_000  # How many last steps to keep for model training
    # Minimum number of steps in a memory to start training
    MIN_REPLAY_MEMORY_SIZE = 1_000
    MINIBATCH_SIZE = 64  # How many steps (samples) to use for training
    UPDATE_TARGET_EVERY = 5  # Terminal states (end of episodes)
    MODEL_NAME = 'NNNavigator'
    MIN_REWARD = 0  # For model save
    MEMORY_FRACTION = 0.20

    # Environment settings
    EPISODES = 20_000
    STEPS_PER_EPISODE = 200

    # Exploration settings
    epsilon = 1  # not a constant, going to be decayed
    EPSILON_DECAY = 0.99975
    MIN_EPSILON = 0.001

    MOVE_PENALTY = 0
    DEATH_PENALTY = -300
    GOAL_REWARD = 100
    OBSERVATION_SPACE_VALUES = (Settings.VISION_DISTANCE * 2 + 1,
                                Settings.VISION_DISTANCE * 2 + 1, 1)

    AGGREGATE_STATS_EVERY = 50  # episodes

    action_space = {
        0: (0, 0),
        1: (0, -1),
        2: (1, 0),
        3: (0, 1),
        4: (-1, 0),
    }
    ACTION_SPACE_SIZE = len(action_space)

    def __init__(self, player, surface, reached_goal, file=None):
        self.ep_rewards = [self.MIN_REWARD]
        self.episode = 1
        self.episode_step = 0
        self.player = player
        self.surface = surface
        self.reached_goal = reached_goal

        coords = (self.player.x - Settings.VISION_DISTANCE,
                  self.player.y - Settings.VISION_DISTANCE)
        self.visionSprite = VisionSurface(
            surface.tile_size, player.color, coords, surface.surface)

        # Main model
        if file:
            self.model = load_model(file)
        else:
            self.model = self.create_model()

        # Target network
        self.target_model = self.create_model()
        self.target_model.set_weights(self.model.get_weights())

        # An array with last n steps for training
        self.replay_memory = deque(maxlen=self.REPLAY_MEMORY_SIZE)

        # Custom tensorboard object
        self.tensorboard = TensorBoard(
            log_dir="logs/{}-{}".format('NNNavigator', int(time())))

        # Used to count when to update target network with main network's weights
        self.target_update_counter = 0

    def get_episode(self):
        return '{:d}/{:>3d} (d)'.format(self.episode, self.episode_step)

    def update(self):
        if self.player.move_ticker <= self.player.frames_per_move:
            return
        # random_x = random.randint(-1, 1)
        # random_y = random.randint(-1, 1)
        # self.player.move(random_x, random_y)

        # This part stays mostly the same, the change is to query a model for Q values
        if numpy.random.random() > self.epsilon:
            # Get action from Q table
            action = numpy.argmax(self.get_qs())
        else:
            # Get random action
            action = numpy.random.randint(0, self.ACTION_SPACE_SIZE)

        new_state, reward, done = self.do_step(action)

        # Transform new continous state to new discrete state and count reward
        self.episode_reward += reward

        # Every step we update replay memory and train main network
        self.update_replay_memory(
            (self.current_state, action, reward, new_state, done))
        self.train(done, self.episode_step + 1)

        self.current_state = new_state

        if self.episode_step >= self.STEPS_PER_EPISODE:
            self.player.die()

    def move(self, dx=0, dy=0):
        self.visionSprite.move(dx, dy)

    def draw(self):
        self.visionSprite.draw()

    def do_step(self, action_index):
        self.episode_step += 1
        self.player.move(*self.action_space[action_index])

        if self.reached_goal:
            reward = self.GOAL_REWARD
            self.reached_goal = False
        elif self.player.is_alive:
            reward = self.MOVE_PENALTY
        else:
            reward = self.DEATH_PENALTY

        return self.player.look_square(), reward, not self.player.is_alive

    def die(self):
        if self.episode_step <= 0:
            return
        self.ep_rewards.append(self.episode_reward)
        if not self.episode % self.AGGREGATE_STATS_EVERY or self.episode == 1:
            average_reward = sum(
                self.ep_rewards[-self.AGGREGATE_STATS_EVERY:])/len(self.ep_rewards[-self.AGGREGATE_STATS_EVERY:])
            min_reward = min(self.ep_rewards[-self.AGGREGATE_STATS_EVERY:])
            max_reward = max(self.ep_rewards[-self.AGGREGATE_STATS_EVERY:])
            self.tensorboard.update_stats(
                reward_avg=average_reward, reward_min=min_reward, reward_max=max_reward, epsilon=self.epsilon)

            # Save model, but only when min reward is greater or equal a set value
            if min_reward >= self.MIN_REWARD:
                self.save_model(max_reward, average_reward, min_reward)

                # Decay epsilon
        if self.epsilon > self.MIN_EPSILON:
            self.epsilon *= self.EPSILON_DECAY
            self.epsilon = max(self.MIN_EPSILON, self.epsilon)

        self.episode += 1

    def resurrect(self):
        self.reached_goal = False
        # Update tensorboard step every episode
        self.tensorboard.step = self.episode

        # Restarting episode - reset episode reward and step number
        self.episode_reward = 0
        self.episode_step = 0
        self.current_state = self.player.look_square()
        # self.step = 1
        self.current_state = self.player.look_square()

    def __str__(self):
        return Settings.TUPLE_SEP.join([str(self.reached_goal)])

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

    def save_model(self, max_reward=None, average_reward=None, min_reward=None, filename=None):
        if filename:
            filename = 'models/{}'.format(filename.split('/')[-1])
        else:
            filename = 'models/{:_>7.2f}max_{:_>7.2f}avg_{:_>7.2f}min_{}.nnnm'.format(
                max_reward, average_reward, min_reward, int(time()))
        self.model.save(filename)
        return filename

    # Adds step's data to a memory replay array
    # (observation space, action, reward, new observation space, done)
    def update_replay_memory(self, transition):
        self.replay_memory.append(transition)

    # Trains main network every step during episode
    def train(self, terminal_state, step):

        # Start training only if certain number of samples is already saved
        if len(self.replay_memory) < self.MIN_REPLAY_MEMORY_SIZE:
            return

        # Get a minibatch of random samples from memory replay table
        minibatch = random.sample(self.replay_memory, self.MINIBATCH_SIZE)

        # Get current states from minibatch, then query NN model for Q values
        current_states = numpy.array([transition[0]
                                      for transition in minibatch])
        current_qs_list = self.model.predict(current_states)

        # Get future states from minibatch, then query NN model for Q values
        # When using target network, query it, otherwise main network should be queried
        new_current_states = numpy.array(
            [transition[3] for transition in minibatch])
        future_qs_list = self.target_model.predict(new_current_states)

        X = []
        y = []

        # Now we need to enumerate our batches
        for index, (current_state, action, reward, new_current_state, done) in enumerate(minibatch):

            # If not a terminal state, get new q from future states, otherwise set it to 0
            # almost like with Q Learning, but we use just part of equation here
            if not done:
                max_future_q = numpy.max(future_qs_list[index])
                new_q = reward + self.DISCOUNT * max_future_q
            else:
                new_q = reward

            # Update Q value for given state
            current_qs = current_qs_list[index]
            current_qs[action] = new_q

            # And append to our training data
            X.append(current_state)
            y.append(current_qs)

        # Fit on all samples as one batch, log only on terminal state
        self.model.fit(numpy.array(X), numpy.array(y), batch_size=self.MINIBATCH_SIZE, verbose=0,
                       shuffle=False, callbacks=[self.tensorboard] if terminal_state else None)

        # Update target network counter every episode
        if terminal_state:
            self.target_update_counter += 1

        # If counter reaches set value, update target network with weights of main network
        if self.target_update_counter > self.UPDATE_TARGET_EVERY:
            self.target_model.set_weights(self.model.get_weights())
            self.target_update_counter = 0

    # Queries main network for Q values given current observation space (environment state)
    def get_qs(self):
        return self.model.predict(numpy.array(self.current_state).reshape(-1, *self.current_state.shape))[0]


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
