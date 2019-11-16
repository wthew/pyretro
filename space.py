# -*- coding: utf-8 -*-
import pygame, sys, random
from os import path
from pygame.locals import  *
from util import *


pygame.display.set_caption('Space')

# Variaveis importantes

# windows 60 - 3 / linux 60 6
FPS = 60 # taxa de atualizacao
SPEED = FPS/12 # velocidade dos movimentos em 'pixel por FPS' sendo o recomendavel 12
BG = pygame.image.load(path.join(PATH_TO_ASSETS,'backgrounds','space.png'))
FONT_COLOR = (225, 225 ,255)

bullets = []

clock = pygame.time.Clock()

# Definindo eventos automaticos
BOT_SHOOT = pygame.event.Event(USEREVENT + 1)
BOT_DIE = pygame.event.Event(USEREVENT + 2)
NEXT_STAGE = pygame.event.Event(USEREVENT + 3)

# pygame.time.set_timer(BOT_SHOOT.type, 240)
pygame.time.set_timer(BOT_SHOOT.type, 512)

# load images
heart_image = load_image('space', "heart.png", 4)
heart_broken_image = load_image('space', "heart_broken.png", 4)
heart_width, heart_height = heart_image.get_size()


# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        # posição inicial
        self.x, self.y = screen_size[0]/2,  int(screen_size[1] * .8)

        self.image = load_image('space', 'space_player.png', 3)

        self.width, self.height = self.image.get_size()
        self.rect = Rect(self.x, self.y, self.width, self.height)

        self.alive, self.shooting, self.direction = True, False, 'none'
        self.hp = 15
        self.battery = Battery()

        self.hearts = [
            Rect(i, int(screen_size[1] - heart_height * 2), heart_width, heart_height) for i in range( int(screen_size[0] * .05), int(self.hp * (heart_width * 1.55) ), int(heart_width * 1.5))
        ]

    def move(self, direction):
        self.direction = direction

    def goto(self, x):
        self.x = x - self.width // 2

    def update(self):
        self.battery.update()

        if self.alive and self.hp <= 0:
            self.alive = False

        if self.x >= screen_size[0] - self.width * 1.5:
            self.x -= 5

        if self.x <= self.width * 1.5:
            self.x += 5

        if self.direction == 'left':
            self.x -= SPEED

        if self.direction == 'right':
            self.x += SPEED

        self.rect = Rect(self.x, self.y, self.width, self.height)


    def draw(self, surf):

        surf.blit(self.image, self.rect)
        # self.bar.draw(surf)
        self.battery.draw(surf)

        for i_heart in range(len(self.hearts)):
            surf.blit( (heart_image if self.hp > i_heart else heart_broken_image), self.hearts[i_heart])


    def shoot(self, list):
        if not self.battery.blocked:
            # self.battery.charge -= 3
            list.append(Bullet(self))

class Battery:
    def __init__(self):
        self.sprites = {}

        self.charge = 0

        for i in glob.glob(path.join(PATH_TO_ASSETS, 'space', 'battery?.png')):
            self.sprites[path.basename(i)] = pygame.image.load(i)

        self.img = self.sprites['battery0.png']
        self.height, self.width = self.img.get_size()

        self.rect = Rect(screen_size[0]*.9, screen_size[1] * .9, self.width, self.height)

    def update(self):
        if self.charge <= 25: self.charge += .2

        if self.charge >= 24:
            self.img = self.sprites[f'battery{3}.png']
            self.blocked = False

        elif self.charge > 16:
            self.img = self.sprites[f'battery{2}.png']

        elif self.charge > 8:
            self.img = self.sprites[f'battery{1}.png']

        elif self.charge > 4:
            self.img = self.sprites[f'battery{0}.png']

        else:
            self.blocked = True


    def draw(self, surf):
        surf.blit(pygame.transform.scale(self.img, (self.height * 4, self.width * 4)), self.rect)

class Bullet(Rect):
    def __init__(self, src, enemy=False):
        sfx['bullet.wav'].play()
        self.x = src.x + src.width // 2 - 5 // 2
        self.y = src.y + src.height // 2 - 5 // 2
        self.color = FONT_COLOR
        self.direction = 'down' if enemy else 'up'
        self.alive = True
        self.rect = Rect(self.x, self.y, 5, 10)
        self.damage = 50
        self.acc = 1

    def update(self):
        if self.alive:
            self.acc += .1
            self.y = self.y + SPEED * self.acc if self.direction is 'down' else self.y - SPEED * self.acc
            self.rect = Rect(self.x, self.y, 5, 10)

            if self.y <= - 0 or self.y >= screen_size[1]:
                self.alive = False

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)

class Enemy():
    def __init__(self, x, y):
        self.init_x, self.init_y = x, y
        self.x, self.y = x, y
        self.image = self.image = load_image('space', 'SPACE_Enemy.png', 4)
        self.width, self.height = self.image.get_size()
        self.rect = Rect(self.x - self.width // 2, self.y, self.width + self.width // 2, self.height)
        self.alive = True
        self.hp = 50 # nem tao facil nem tao dificil de matar os inimigos
        self.direction = 'left' if self.y in [i for i in range((self.height * 2), (screen_size[1] // 2), (self.height * 4))] else 'right'

    def update(self, boss=False):
        if self.hp <= 0:
            self.alive = False
            pygame.event.post(BOT_DIE)

        if self.direction is 'right': self.x += SPEED
        if self.direction is 'left': self.x -= SPEED
        if self.direction is 'down': self.y += SPEED
        if self.direction is 'up': self.y -= SPEED

        if self.direction is 'right' and self.x >= self.init_x + self.width * 2: self.direction = 'left'

        if self.direction is 'left' and self.x <= self.init_x - self.width * 2: self.direction = 'right'

        if self.x >= screen_size[0] - self.width * 2: self.x -= 10

        if self.x <= self.width: self.x += 10

        if self.y >= screen_size[1] * .5: self.direction = 'up'

        if self.y <= 50: self.direction = 'down'

        self.rect = Rect(self.x, self.y, self.width, self.height)


    def draw(self, surf):
    	screen.blit(self.image, self.rect)

    def cd(self):
        if self.direction is 'right':
            self.direction = 'left'

        else:
            self.direction = 'right'

        self.acc = 1


class Boss(Enemy):
    def __init__(self):
        self.image = self.image = load_image('space', 'boss.png', 8)
        self.width, self.height = self.image.get_size()
        self.x, self.y = screen_size[0] / 2 - self.width / 2, screen_size[1] / 2 - self.width / 2
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.alive = True
        self.hp = 1000
        self.direction = 'none'
        self.acc = 1
        self.bar = Bar_Horizontal(self.hp, screen_size[0]*.25, 15, screen_size[0]*.5, 20)

    def update(self):
        super().update()
        self.bar.update(self.hp)
        if pygame.time.get_ticks() % 50 == 0:
            self.direction = random.choice(['up', 'down', 'left', 'right'])

    def draw(self, surf):
        super().draw(surf)
        self.bar.draw(surf)


class Platform():
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.width, self.height = 100, 10
        self.color = FONT_COLOR # Definindo a cor como 'Quase Branco'
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.hp = 5000 # tem que ser dificil quebrar a parede
        self.alive = True

    def update(self):
        if self.alive:
            if self.hp <= 250:
                self.color = (150, 150, 150)

            if self.hp <= 0: # somente quando ela qubrar
                self.alive = False
                self.x, self.y = screen_size[0], screen_size[1]
                self.rect = Rect(self.x, self.y, self.width, self.height)
                self.memento_mori = pygame.time.get_ticks()
                print(self.memento_mori)
        else:
            print(f'{self.memento_mori} || {pygame.time.get_ticks()}')


    def draw(self, surf):
        pygame.draw.rect(screen, self.color, self.rect)



class Space():
    def __init__(self, c=1):
        self.stage()
        self.bg_color = (0, 0, 0)
        self.score = 0
        self.counter = c
        self.player = Player()
        self.platforms = list()
        self.numb_platforms = 5

        # variavel auxiliar para o alocamento das plataformas
        espaco = (screen_size[0] - self.numb_platforms * 100)/(self.numb_platforms + 1)

        # Definindo posicoes das plataformas, com o maximo (recomendavel) sendo 5
        for i in range(self.numb_platforms):
            self.platforms.append(Platform(espaco * (i+1) + (i*100), screen_size[1] * 0.75))


    def update(self):
        screen.fill(self.bg_color)
        self.player.update()

        for bullet in bullets:
            bullet.update() if bullet.alive else bullets.remove(bullet)

            for platform in self.platforms:
                platform.update() if platform.alive else self.platforms.remove(platform)
                if bullet.rect.colliderect(platform):
                    platform.hp -= bullet.damage
                    bullets.remove(bullet)

            for enemy in self.enemys:
                if bullet.rect.colliderect(enemy.rect) and bullet.direction == 'up':
                    enemy.hp -= bullet.damage
                    bullets.remove(bullet)

            if bullet.rect.colliderect(self.player.rect) and bullet.direction == 'down':
                bullets.remove(bullet)
                self.player.hp -= 1
                sfx['damage.wav'].play()

        if len(bullets) > 100: bullets.remove(bullets[0])

        if not self.player.alive:
            self.stage()
            self.player.__init__()
            self.score = 0
            return False

        if len(self.enemys) == 0:
            self.counter += 1
            pygame.event.post(NEXT_STAGE)
            self.player.x, self.player.direction = screen_size[0] * .5, 'none'

            if self.counter in [i for i in range(0, 50, 5)] or self.counter >= 50:
                self.stage(boss=True)
            else:
                self.stage()

        [enemy.update() if enemy.alive else self.enemys.remove(enemy) for enemy in self.enemys]
        return True

    def stage(self, boss=False):
        self.enemys = []
        self.bullets = bullets

        if boss: self.enemys.append(Boss())

        else:
            enemy_model = Enemy(screen_size[0], screen_size[1])

            for y in range((enemy_model.height * 2), (screen_size[1] // 2), (enemy_model.height * 2)):
                for x in range((enemy_model.width * 4), (screen_size[0] - enemy_model.width * 4), (enemy_model.width * 2)):
                    self.enemys.append(Enemy(x, y))

            del(enemy_model)

    def shoot(self, who, enemy=False):
        bullets.append(Bullet(who, enemy=enemy))


    def draw(self, surf):
        draw_text(screen, 'SCORE:', int(screen_size[0] * 0.80), 10, size=25, color=(225,225,255))
        draw_text(screen, str(self.score), int(screen_size[0] * 0.95), 10, size=25)
        [bullet.draw(surf) for bullet in bullets]
        [platform.draw(surf) for platform in self.platforms]
        [enemy.draw(surf) for enemy in self.enemys]
        self.player.draw(surf)
        if len(self.enemys) == 0: surf.fi


class Game():
    def __init__(self):
        self.on_menu, self.on_space, self.on_load, self.on_end = True, False, False, False
        self.btn_start = Button(250, 45, 'center', 15)
        self.btn_end = Button(250, 45, 'center', screen_size[1]/4)
        self.space = Space()


    def update(self):
        if self.on_space: # no 'espaco'
            self.space.update()
            if not self.on_space: self.on_end = True

        if self.on_load:
            let_b = pygame.time.get_ticks()
            if let_b - self.let_a >= 2500:
                self.on_load = False
                self.on_space = True



    def draw(self, surf):
        if self.on_menu:
            surf.blit(BG, (0, 0))
            self.btn_start.update(surf, 'Start Game')
            draw_text(surf, 'SPACE v1.6', screen_size[0]/4 * 3, screen_size[1] - 150, size=20, color=FONT_COLOR)
            draw_text(surf, 'by: TheW', screen_size[0]/4 * 3, screen_size[1] - 100, size=20, color=FONT_COLOR)

        if self.on_load:
            surf.blit(pygame.Surface(screen_size), (0, 0))
            draw_text(surf, 'Loading...', screen_size[0] * .1, screen_size[1] * .9, size=20, color=FONT_COLOR)


        elif self.on_space:
            self.space.draw(surf)

        elif self.on_end:# no game over
            surf.blit(BG, (0, 0))
            self.btn_end.update(surf, 'Try Again')
            draw_text(surf, 'Game Over', screen_size[0] / 2, screen_size[1] / 8, align='center', size=25, color=FONT_COLOR)


        pygame.display.flip()

    def listen(self):
        for event in pygame.event.get():
            # Eventos Disparados em Qualquer Momento
            if event.type == QUIT:
                sys.exit()

            if event.type == KEYDOWN and event.key == K_F4:
                pygame.display.set_mode((screen_size[0], screen_size[1])) if screen.get_flags() & FULLSCREEN else pygame.display.set_mode((screen_size[0], screen_size[1]), pygame.FULLSCREEN)

            # Eventos So Disparados enquanto no menu
            if self.on_menu:
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    sys.exit()

                if event.type == KEYDOWN and event.key == K_RETURN:
                    pygame.mixer.music.stop()
                    self.on_menu, self.on_space = False, True

                if event.type == MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if self.btn_start.isClicked(mouse_x, mouse_y):
                        pygame.mixer.music.stop()
                        self.on_menu, self.on_space = False, True

            # Eventos So Disparados enquanto no 'espaco'

            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.on_space = False
                self.on_menu = True

            if self.on_space:
                if event.type == KEYDOWN and (event.key == K_a or event.key == K_SPACE):
                     self.space.player.shoot(bullets)
                if event.type == KEYDOWN and (event.key == K_a or event.key == K_LEFT):
                     self.space.player.move('left')
                if event.type == KEYDOWN and (event.key == K_d or event.key == K_RIGHT):
                     self.space.player.move('right')
                if event.type == KEYUP:
                    if (event.key == K_a or event.key == K_d) or (event.key == K_LEFT or event.key == K_RIGHT):
                         self.space.player.direction = 'none'

                if event.type == NEXT_STAGE.type:
                    self.on_space = False
                    self.on_load = True
                    self.let_a = pygame.time.get_ticks()

                if event.type == BOT_SHOOT.type:
                    try: self.space.shoot(random.choice(self.space.enemys), enemy=True)
                    except: pass

                if event.type == BOT_DIE.type:
                    sfx['dead_enemy.wav'].play()
                    self.space.score += 1

            # Eventos So Disparados enquanto morto
            if self.on_end:
                if event.type == KEYDOWN and event.key == K_RETURN:
                    pygame.mixer.music.stop()
                    self.on_end, self.on_space = False, True

                if event.type == MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if self.btn_end.isClicked(mouse_x, mouse_y):
                        pygame.mixer.music.stop()
                        self.on_end, self.on_space = False, True


# começa a partir daqui:
game = Game()

while True:
    clock.tick(FPS)
    game.listen()
    game.update()
    game.draw(screen)
