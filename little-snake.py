import pygame, sys, random
from pygame.locals import *

from util import *

# light mode (default)
playerLight, appleLight, bgLight = (25, 25, 25), (190, 0, 0), (222, 222, 222)

# dark mode
playerDark, appleDark, bgDark = (255, 255, 255), (190, 0, 0), (25, 25, 25)

# classic mode
playerClassic, appleClassic, bgClassic = (25, 25, 25), (120, 175, 50), (107, 142, 35)

# cyan mode
playerCyan, appleCyan, bgCyan = (255, 255, 255), (225, 225, 0), (0, 190, 222)

screen_size_X = 800
screen_size_Y = 600
block_size = 10
config = False

pygame.init()
pygame.display.init()
pygame.display.set_caption('Little Snake')
font = pygame.font.Font('Assets/pixel-font.ttf', 25)

screen = pygame.display.set_mode((screen_size_X, screen_size_Y))
clock = pygame.time.Clock()

class Canvas():
    def __init__(self):
        self.bg_color = bgLight
        self.btns = []
        self.lbls = []
        self.items = []
        self.fps = 20

    def update(self):
        screen.fill(self.bg_color)
        clock.tick(self.fps)
        for i in range(len(self.items)):
            if self.items[i][0] == easy_btn_bool:
                self.items[i][1] = world.dificuldade
            self.items[i][0].update(self.items[i][1])

    def changeColor(self, pcolor, acolor, bgcolor):
        player.color = pcolor
        apple.color = acolor
        for ele in [world, menu_canvas, over_canvas, config_canvas]:
            ele.bg_color = bgcolor

class World():
    def __init__(self):
        self.pristine = True
        self.score = 0
        self.bg_color = bgLight
        self.conter = Button(250, 45, 375, 10, flat = True)
        self.dificuldade = 'Facil' if True else 'Dificil'
        self.fps = 10 if self.dificuldade == 'Facil' else 20

    def start(self):
        self.score = 0
        self.fps = 10 if self.dificuldade == 'Facil' else 20
        player.alive = True
        apple.put_on_grid()
        self.pristine = False

    def update(self):
        self.pristine = False
        clock.tick(self.fps)
        screen.fill(self.bg_color)
        self.conter.update(str(self.score))
        player.update()
        apple.update()
        pygame.display.update()

class Button():
    def __init__(self, tamX, tamY, posX, posY, text = '', flat = False):
        self.tamX = tamX
        self.tamY = tamY
        self.posX = posX
        self.posY = posY
        self.text = text
        self.flat = flat

    def update(self, text):
        color_text = player.color if self.flat else world.bg_color
        color_bg = world.bg_color if self.flat else player.color
        pygame.draw.rect(screen, color_bg, [self.posX, self.posY, self.tamX, self.tamY])
        screen.blit(font.render(text, True, color_text), [self.posX + self.tamX * 0.10 , self.posY + 1])

    def isClicked(self, mouseX, mouseY):
        return (mouseX > self.posX and mouseX < self.posX + self.tamX and mouseY > self.posY and mouseY < self.posY + self.tamY)



''' Classes '''
class Player():
    def __init__(self):
        self.alive = False
        self.init_size = 7
        self.blocks = [[80, 300, block_size, block_size]]
        self.color = playerLight
        self.direction = 'UP'
        self.last_direction = 'UP'
        for i in range(self.init_size):
            self.blocks.append([- 10, - 10, block_size, block_size])

    def __dead__(self):
        self.alive = False
        self.init_size = self.init_size
        self.blocks = [[80, 300, block_size, block_size]]
        self.direction = 'UP'
        self.last_direction = 'UP'
        for i in range(self.init_size):
            self.blocks.append([- 10, - 10, block_size, block_size])

    def update(self):
        if self.direction == 'UP':
            new_head = [self.blocks[0][0], self.blocks[0][1] - block_size, self.blocks[0][2], self.blocks[0][3]]
        if self.direction == 'DOWN':
            new_head = [self.blocks[0][0], self.blocks[0][1] + block_size, self.blocks[0][2], self.blocks[0][3]]
        if self.direction == 'RIGHT':
            new_head = [self.blocks[0][0] + block_size, self.blocks[0][1], self.blocks[0][2], self.blocks[0][3]]
        if self.direction == 'LEFT':
            new_head = [self.blocks[0][0] - block_size, self.blocks[0][1], self.blocks[0][2], self.blocks[0][3]]

        for i in range(len(self.blocks) - 1):
            if self.blocks[i] == new_head:
                if self.blocks[i-1][0] == new_head[0]:
                    if self.last_direction == 'RIGHT':
                        new_head = [self.blocks[0][0] + block_size, self.blocks[0][1], self.blocks[0][2], self.blocks[0][3]]
                    if self.last_direction == 'LEFT':
                        new_head = [self.blocks[0][0] - block_size, self.blocks[0][1], self.blocks[0][2], self.blocks[0][3]]
                if self.blocks[i-1][1] == new_head[1]:
                    if self.last_direction == 'UP':
                        new_head = [self.blocks[0][0], self.blocks[0][1] - block_size, self.blocks[0][2], self.blocks[0][3]]
                    if self.last_direction == 'DOWN':
                        new_head = [self.blocks[0][0], self.blocks[0][1] + block_size, self.blocks[0][2], self.blocks[0][3]]

        self.blocks[0] = new_head

        if world.dificuldade == 'Dificil':
            if self.blocks[0][0] <= - block_size or self.blocks[0][0] >= screen_size_X or self.blocks[0][1] <= - block_size or self.blocks[0][1] >= screen_size_Y:
                pygame.draw.rect(screen, self.color, self.blocks[0])
                self.__dead__()
        if world.dificuldade == 'Facil':
            if self.blocks[0][0] <= - block_size:
                self.blocks[0][0] += screen_size_X
            if self.blocks[0][0] >= screen_size_X:
                self.blocks[0][0] += - screen_size_X
            if self.blocks[0][1] <= - block_size:
                self.blocks[0][1] += screen_size_Y
            if self.blocks[0][1] >= screen_size_Y:
                self.blocks[0][1] += - screen_size_Y

        for i in range(len(self.blocks) - 1, 0, -1):
            try:
                if self.blocks[i] == self.blocks[0]:
                    pygame.draw.rect(screen, self.color, self.blocks[i])
                    self.__dead__()
                else:
                    self.blocks[i] = self.blocks[i-1]
                    pygame.draw.rect(screen, self.color, self.blocks[i])
            except:
                self.__dead__()

    def animation(self):
        pos1 = [80, 300]
        pos2 = [80, 140]
        pos3 = [320, 140]
        pos4 = [320, 300]

        if self.blocks[0] == [pos1[0], pos1[1], block_size, block_size]:
            self.direction = 'UP'
        if self.blocks[0] == [pos2[0], pos2[1], block_size, block_size]:
            self.direction = 'RIGHT'
        if self.blocks[0] == [pos3[0], pos3[1], block_size, block_size]:
            self.direction = 'DOWN'
        if self.blocks[0] == [pos4[0], pos4[1], block_size, block_size]:
            self.direction = 'LEFT'

        self.update()

class Apple():
    def __init__(self):
        self.color = appleLight
        self.put_on_grid()

    def put_on_grid(self):
        x = random.randint(0, screen_size_X - block_size)
        y = random.randint(0, screen_size_Y - block_size)
        self.block = [x//10 * 10, y//10 * 10, block_size, block_size]

    def update(self):

        pygame.draw.rect(screen, self.color, self.block)

player = Player()
apple = Apple()

world = World()
menu_canvas = Canvas()
over_canvas = Canvas()
config_canvas = Canvas()

"""  parametros: tamX, tamY, posX, posY, text  """
play_btn = Button(250, 45, 12, 15)
config_btn = Button(250, 45, 12, 70)

easy_btn = Button(250, 45, 275, 15)
easy_btn_bool = Button(250, 45, 537.5, 15)

menu_canvas.items.append([play_btn, 'Play'])
menu_canvas.items.append([config_btn, 'Configurar'])

over_canvas.items.append([play_btn, 'Try'])
over_canvas.items.append([config_btn, 'Configurar'])

config_canvas.items.append([play_btn, 'Back'])
config_canvas.items.append([config_btn, 'Tela Cheia (F4)'])
config_canvas.items.append([easy_btn, 'Dificuldade'])
config_canvas.items.append([easy_btn_bool, world.dificuldade])


while True:
    if config:
        config_canvas.update()

    elif world.pristine:
        menu_canvas.update()

    else:
        over_canvas.update()

    player.animation()

    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()

        if event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit()

        if event.type == KEYDOWN and event.key == K_F4:
            size = (screen_size_X, screen_size_Y)
            pygame.display.set_mode(size if screen.get_flags() & FULLSCREEN else size, pygame.FULLSCREEN)

        if event.type == KEYDOWN:
            if config:
                if event.key == K_KP1:
                    Canvas().changeColor(playerLight, appleLight, bgLight)

                if event.key == K_KP2:
                    Canvas().changeColor(playerClassic, appleClassic, bgClassic)

                if event.key == K_KP3:
                    Canvas().changeColor(playerDark, appleDark, bgDark)

                if event.key == K_KP4:
                    Canvas().changeColor(playerCyan, appleCyan, bgCyan)
            else:
                if event.key == K_RETURN:
                    world.start()

        if event.type == MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if play_btn.isClicked(x, y):
                if config:
                    config = False

                else:
                    world.start()

            if config_btn.isClicked(x, y):
                if config:
                    size = (screen_size_X, screen_size_Y)
                    pygame.display.set_mode(size) if screen.get_flags() & FULLSCREEN else pygame.display.set_mode(size, pygame.FULLSCREEN)

                else:
                    config = True

            if easy_btn.isClicked(x, y):
                if config:
                    world.dificuldade = 'Facil' if world.dificuldade == 'Dificil' else 'Dificil'

    while player.alive:

        if (player.blocks[0][0] == apple.block[0]) and (player.blocks[0][1] == apple.block[1]):
            world.score += 1
            apple.put_on_grid()
            player.blocks.append([-10, -10, block_size, block_size])
            for i in [5, 10, 15, 20, 25, 30, 40, 60]:
                if world.score == i:
                    if world.dificuldade == 'Facil': world.fps += 1 if world.fps < 60 else 0
                    else: world.fps += 5 if world.fps < 60 else 0

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()

            elif event.type == KEYDOWN:
                keys_up = [K_w, K_UP]
                keys_down = [K_s, K_DOWN]
                keys_left = [K_a, K_LEFT]
                keys_right = [K_d, K_RIGHT]

                if (event.key in keys_up) and player.direction != 'DOWN':
                    player.last_direction = player.direction
                    player.direction = 'UP'

                if (event.key in keys_down) and player.direction != 'UP':
                    player.last_direction = player.direction
                    player.direction = 'DOWN'

                if (event.key in keys_left) and player.direction != 'RIGHT':
                    player.last_direction = player.direction
                    player.direction = 'LEFT'

                if (event.key keys_right) and player.direction != 'LEFT':
                    player.last_direction = player.direction
                    player.direction = 'RIGHT'

                if event.key == K_ESCAPE:
                    player.alive = False

        world.update()

    pygame.display.update()
