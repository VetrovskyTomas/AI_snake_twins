import sys
import pygame
import random
from vars import Direction, Point
import numpy as np
from snake import Snake

pygame.init()
font = pygame.font.Font('arial.ttf', 16)
#font = pygame.font.SysFont('courier', 25)

caption_info = '                     Wietrack Softwork (c)2022'

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE2 = (0, 100, 255)
GREEN2 = (0, 255, 0)
BLACK = (0,0,0)
YELLOW = (255,255,0)
GRAY = (55,55,55)

BLOCK_SIZE = 20

class GameWorld:

    def __init__(self, w=640, h=480, players=2, speed = 5, score_win = 30):
        self.w = w
        self.h = h
        self.speed = speed
        self.score_win = score_win
        # init display
        self.fullscreen = False
        self.display = pygame.display.set_mode((self.w, self.h))# pygame.FULLSCREEN
        self.clock = pygame.time.Clock()
        self.players = players
        self.pause = True
        self.update_title()
        self.reset()

    def update_title(self):
        pygame.display.set_caption(
            'Snake Twins - player(s): ' + str(self.players) + ' speed: ' + str(self.speed) + ' score to win: ' + str(
                self.score_win) + caption_info)

    def reset(self):
        self.winner = -1
        self.rocks = {}
        self._place_rocks()
        self.snakes = []
        for i in range(self.players):
            self.snakes.append(Snake(self, i))
        self.food = None
        self._place_food()

    def _place_rocks(self):
        wb = (self.w-BLOCK_SIZE )//BLOCK_SIZE+1
        hb = (self.h-BLOCK_SIZE )//BLOCK_SIZE+1
        print("width blocks: "+str(wb)+" height blocks: "+str(hb))
        for x in range(wb):
            for y in range(hb):
                if x == 0:
                    self.rocks[Point(x * BLOCK_SIZE, y * BLOCK_SIZE)] = 0
                else:
                    if y == 0:
                        self.rocks[Point(x * BLOCK_SIZE, y * BLOCK_SIZE)] = 0
                if x == wb-1:
                    self.rocks[Point(x * BLOCK_SIZE, y * BLOCK_SIZE)] = 0
                else:
                    if y == hb-1:
                        self.rocks[Point(x * BLOCK_SIZE, y * BLOCK_SIZE)] = 0

    def get_neighbours(self, pt):
        return [Point(pt.x - 20, pt.y),
                Point(pt.x + 20, pt.y),
                Point(pt.x, pt.y - 20),
                Point(pt.x, pt.y + 20)]

    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.is_collision(self.food):
            self._place_food()

    def is_collision(self, pt):
        for snake in self.snakes:
            if snake.contains_point(pt):
                return True
        for rock in self.rocks:
            if pt == rock:
                return True
        return False

    def _update_ui(self, events):
        self.display.fill(BLACK)

        for pt in self.rocks:
            if self.rocks[pt] == 0:
                pygame.draw.rect(self.display, GRAY, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))

        for i in range(self.players):
            self.snakes[i]._update_ui(events, font)

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        if self.pause:
            if self.winner == -1:
                text = font.render("SNAKE TWINS _/\/\/\_o-< ", True, WHITE)
                self.display.blit(text, [40, self.h / 2 - 72])
                text = font.render("*** (PAUSE) ***", True, WHITE)
                self.display.blit(text, [40, self.h / 2 - 24])
                text = font.render("press [SPACE] to play", True, WHITE)
                self.display.blit(text, [40, self.h/2])
                text = font.render("press [1] or [2] key to change the PLAYER mode (AI / HUMAN)", True, WHITE)
                self.display.blit(text, [40, self.h / 2 + 24])
                text = font.render("press [f] key to change fullscreen / window mode", True, WHITE)
                self.display.blit(text, [40, self.h / 2 + 48])
                text = font.render("press [+] / [-] keys to increase / decrease game speed ("+str(self.speed)+")", True, WHITE)
                self.display.blit(text, [40, self.h / 2 + 72])
                text = font.render("press [^] / [v] keys to increase / decrease score to win (" + str(self.score_win) + ")",True, WHITE)
                self.display.blit(text, [40, self.h / 2 + 96])
                text = font.render("press [<] / [>] keys to decrease / increase number of players (" + str(self.players) + ")", True, WHITE)
                self.display.blit(text, [40, self.h / 2 + 120])
                text = font.render("press [r] key to reset game", True, YELLOW)
                self.display.blit(text, [40, self.h / 2 + 144])
                text = font.render("press [ESC] key to EXIT game", True, RED)
                self.display.blit(text, [40, self.h / 2 + 168])
            else:
                if self.winner == 0:
                    COL = GREEN2
                else:
                    COL = BLUE2
                text = font.render("PLAYER "+str(self.winner+1)+" WON!!!", True, COL)
                self.display.blit(text, [40, self.h / 2])
                text = font.render("PAUSE: PRESS SPACE TO PLAY", True, WHITE)
                self.display.blit(text, [40, self.h / 2 + 24])

        pygame.display.flip()

    def quit(self):
        print("BYE BYE!")
        sys.exit()

    def get_events(self):
        update_title = False
        pressed_keys = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # SPACE
                    if self.winner > -1:
                        self.reset()
                    else:
                        self.pause = not self.pause
                if event.key == pygame.K_KP_PLUS:  # keypad plus
                    self.speed += 3
                    update_title = True
                if event.key == pygame.K_KP_MINUS:  # keypad minus
                    self.speed -= 3
                    update_title = True
                    if self.speed<=0:
                        self.speed = 1
                if self.pause:
                    if event.key == pygame.K_UP:
                        self.score_win += 5
                        update_title = True
                    elif event.key == pygame.K_DOWN:
                        self.score_win -= 5
                        update_title = True
                        if self.score_win<5:
                            self.score_win = 5
                    elif event.key == pygame.K_LEFT:
                        if self.players == 2:
                            self.players = 1
                            self.reset()
                        update_title = True
                    elif event.key == pygame.K_RIGHT:
                        if self.players == 1:
                            self.players = 2
                            self.reset()
                        update_title = True
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_ESCAPE:
                        self.quit()
                if event.key == pygame.K_f:  # f
                    if self.fullscreen:
                        self.fullscreen = False
                        self.display = pygame.display.set_mode((self.w, self.h), pygame.RESIZABLE)
                    else:
                        self.fullscreen = True
                        self.display = pygame.display.set_mode((self.w, self.h), pygame.FULLSCREEN)
                pressed_keys.append(event)
        if update_title:
            self.update_title()
        return pressed_keys

    def update_game(self):
        pressed_keys = self.get_events()
        if not self.pause:
            for i in range(self.players):
                self.snakes[i].run(pressed_keys)
        # 5. update ui and clock
        self._update_ui(pressed_keys)
        self.clock.tick(self.speed)
