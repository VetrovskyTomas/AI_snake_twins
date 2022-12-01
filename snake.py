import vars
from vars import Direction, Point
import pygame
import random
import numpy as np
from agent import Agent

BLOCK_SIZE = vars.BLOCK_SIZE

# rgb colors
WHITE = (255, 255, 255)
BLUE1 = (0, 50, 255)
BLUE2 = (0, 100, 255)
BLUE3 = (0, 0, 155)
GREEN1 = (0, 155, 0)
GREEN2 = (0, 255, 0)
GREEN3 = (0, 55, 0)
YELLOW = (255,255,0)

class Snake:

    def __init__(self, game, id):
        self.id = id
        self.human = False
        self.agent = Agent(id)#Agent(self.id % 2, id)
        self.game = game
        self.total_score = 0
        self.frame_iteration = 0
        self.reset()

    def _place_snake(self):
        print('generating snake '+str(self.id))
        x = random.randint(0, (self.game.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.game.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.head = Point(x, y)
        new_snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]

        for pt in new_snake:
            if self.game.is_collision(pt):
                return self._place_snake()
        self.snake = new_snake

    def reset(self):
        self.score = 0
        self.frame_iteration = 0
        self.total_score -= 5
        if self.total_score<0:
            self.total_score = 0
        self.direction = Direction.RIGHT
        self._place_snake()

    def _draw_snake(self, COL1, COL2, COL3, pt, last, info, font):
        pygame.draw.rect(self.game.display, COL1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
        if not last == None:
            pygame.draw.line(self.game.display, COL3, [last.x + 9, last.y + 9], [pt.x + 9, pt.y + 9], 4)
        if pt == self.head:
            pygame.draw.rect(self.game.display, YELLOW, pygame.Rect(pt.x+4, pt.y+4, 12, 12))
        else:
            pygame.draw.rect(self.game.display, COL2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))
            if not last == None:
                pygame.draw.line(self.game.display, COL3, [last.x + 9, last.y + 9], [pt.x + 9, pt.y + 9], 4)
        text_raw = " PLAYER " + str(self.id+1) + " Score: " + str(self.score) + " - Total: " + str(self.total_score) + " / " + str(self.game.score_win) + " > Human: " + str(self.human) + " " + info + " Train: " + str(self.agent.train) + " Deaths: " + str(self.agent.n_games)
        return font.render(text_raw, True, COL2)

    def _update_ui(self, events, font):
        # switch ai/human
        for event in events:
            #print(event)
            if self.id == 0:
                if event.key == pygame.K_1: # "1"
                    self.human = not self.human
            if self.id == 1:
                if event.key == pygame.K_2: # "2"
                    self.human = not self.human
        #
        last = None
        for pt in reversed(self.snake):
            if self.id % 2 == 1:
                COL1 = BLUE1
                COL2 = BLUE2
                COL3 = BLUE3
                info = "ASDW"
            else:
                COL1 = GREEN1
                COL2 = GREEN2
                COL3 = GREEN3
                info = "<>^v"
            text = self._draw_snake(COL1, COL2, COL3, pt, last, info, font)
            last = pt
        self.game.display.blit(text, [0, self.id*(self.game.h-BLOCK_SIZE)])

    def move(self, action):
        self._move(action)  # update the head
        self.snake.insert(0, self.head)

    def _move(self, action):
        # action [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]  # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]  # right turn r -> d -> l -> u
        else:  # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]  # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

    def contains_point(self, pt):
        return pt in self.snake

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.game.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.game.h - BLOCK_SIZE or pt.y < 0:
            return True
        # hits itself
        for s in self.game.snakes:
            if s.snake == self.snake:
                if pt in s.snake[1:]:
                    return True
            else:
                if pt in s.snake:
                    return True
        # hits rocks
        if pt in self.game.rocks:
            return True
        return False

    def get_state(self):
        point_l = Point(self.head.x - 20, self.head.y)
        point_r = Point(self.head.x + 20, self.head.y)
        point_u = Point(self.head.x, self.head.y - 20)
        point_d = Point(self.head.x, self.head.y + 20)

        dir_l = self.direction == Direction.LEFT
        dir_r = self.direction == Direction.RIGHT
        dir_u = self.direction == Direction.UP
        dir_d = self.direction == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and self.is_collision(point_r)) or
            (dir_l and self.is_collision(point_l)) or
            (dir_u and self.is_collision(point_u)) or
            (dir_d and self.is_collision(point_d)),

            # Danger right
            (dir_u and self.is_collision(point_r)) or
            (dir_d and self.is_collision(point_l)) or
            (dir_l and self.is_collision(point_u)) or
            (dir_r and self.is_collision(point_d)),

            # Danger left
            (dir_d and self.is_collision(point_r)) or
            (dir_u and self.is_collision(point_l)) or
            (dir_r and self.is_collision(point_u)) or
            (dir_l and self.is_collision(point_d)),

            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # Food location
            self.game.food.x < self.head.x,  # food left
            self.game.food.x > self.head.x,  # food right
            self.game.food.y < self.head.y,  # food up
            self.game.food.y > self.head.y  # food down
        ]
        # print(np.array(state, dtype=int))
        return np.array(state, dtype=int)

    def get_action(self, state, events):
        # get ai/human action
        if self.human:
            return self.get_action_human(state, events)
        else:
            return self.agent.get_action_ai(state)

    def get_action_human(self, state, events):
        dir_l = state[3]
        dir_r = state[4]
        dir_u = state[5]
        dir_d = state[6]
        #print("left: "+str(dir_l)+" right "+str(dir_r)+" up "+str(dir_u)+" down "+str(dir_d))
        final_move = [1, 0, 0]
        # 1. collect user input
        for event in events:
            if self.id == 0:
                if event.key == pygame.K_LEFT:
                    if dir_u:
                        final_move = [0, 0, 1]
                    if dir_d:
                        final_move = [0, 1, 0]
                elif event.key == pygame.K_RIGHT:
                    if dir_u:
                        final_move = [0, 1, 0]
                    if dir_d:
                        final_move = [0, 0, 1]
                elif event.key == pygame.K_UP:
                    if dir_r:
                        final_move = [0, 0, 1]  # left
                    if dir_l:
                        final_move = [0, 1, 0]  # right
                elif event.key == pygame.K_DOWN:
                    if dir_r:
                        final_move = [0, 1, 0]  # left
                    if dir_l:
                        final_move = [0, 0, 1]  # right
            else:
                if event.key == pygame.K_a:
                    if dir_u:
                        final_move = [0, 0, 1]
                    if dir_d:
                        final_move = [0, 1, 0]
                elif event.key == pygame.K_d:
                    if dir_u:
                        final_move = [0, 1, 0]
                    if dir_d:
                        final_move = [0, 0, 1]
                elif event.key == pygame.K_w:
                    if dir_r:
                        final_move = [0, 0, 1]  # left
                    if dir_l:
                        final_move = [0, 1, 0]  # right
                elif event.key == pygame.K_s:
                    if dir_r:
                        final_move = [0, 1, 0]  # left
                    if dir_l:
                        final_move = [0, 0, 1]  # right
        return final_move

    def play_step(self, action):
        self.frame_iteration += 1
        # 2. move
        self.move(action)
        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.head == self.game.food:
            self.score += 1
            self.total_score += 1
            reward = 10
            self.game._place_food()
            if self.total_score == self.game.score_win:
                self.game.winner = self.id
                self.game.pause = True
                game_over = True
        else:
            self.snake.pop()

        # 6. return game over and score
        return reward, game_over, self.score

    def run(self, events):
        if not self.human and self.agent.train:
            # get old state
            state_old = self.get_state()

            # get move
            final_move = self.get_action(state_old, events)

            # perform move and get new state
            reward, done, score = self.play_step(final_move)
            state_new = self.get_state()

            # train short memory
            self.agent.train_short_memory(state_old, final_move, reward, state_new, done)

            # remember
            self.agent.remember(state_old, final_move, reward, state_new, done)
            if done:
                self.agent.train_after_done(self.score)
                if not self.game.winner == self.id:
                    self.reset()
        else:
            # get old state
            state_old = self.get_state()
            # get move
            final_move = self.get_action(state_old, events)
            reward, done, score = self.play_step(final_move)
            if done:
                if not self.game.winner == self.id:
                    self.reset()
            #if score>25:
            #    self.game.reset()