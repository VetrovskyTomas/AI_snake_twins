import torch
import random
import numpy as np
from collections import deque
from model import Linear_QNet, QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    def __init__(self, id):
        self.id = id
        # training
        self.train = True
        self.total_score = 0
        self.record = 0
        #
        self.n_games = 0
        self.epsilon = 0 # randomness - default 0
        self.rand_threshold = 80
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(11, 256, 3)
        if self.model.load('model_id'+str(self.id)+'.pth'):
            # if using trained model reduce randomness
            self.rand_threshold = 0
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def train_after_done(self, score):
        self.n_games += 1
        self.train_long_memory()

        if score > self.record:
            self.record = score
            self.model.save('model_id'+str(self.id)+'.pth')

        self.total_score += score
        self.mean_score = self.total_score / self.n_games
        print('Player', self.id,'- Game', self.n_games, 'Score', score, 'Record:', self.record, 'Mean:', self.mean_score)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action_ai(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = self.rand_threshold - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(np.array(state), dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move
