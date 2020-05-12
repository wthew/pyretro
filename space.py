# -*- coding: utf-8 -*-
import pygame
import sys
import random
from os import path
from pygame.locals import *
from pygame.sprite import groupcollide, spritecollide
from util import *


pygame.display.set_caption('Space')


FPS = 60
SPEED = 8  # default 12
DAMAGE = 50  # damage that player do in enemys
ANIMATION_SPEED = 0.02
FONT_COLOR = (225, 225, 255)

clock = pygame.time.Clock()

# Definindo eventos automaticos
BOT_SHOOT = pygame.event.Event(USEREVENT + 1)

pygame.time.set_timer(BOT_SHOOT.type, 512)

# load images
img_heart = load_image('space', "heart.png", 4)
img_heart_broken = load_image('space', "heart_broken.png", 4)
heart_width, heart_height = img_heart.get_size()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image('space', 'player_idle.png', 3)
        self.width, self.height = self.image.get_size()

        # estado inicial
        self.alive, self.direction = True, 'none'

        # posição inicial
        self.x = int(screen_size[0] * .5 - self.width * .5)
        self.y = int(screen_size[1] * .8)

        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.battery = Battery()

        # posicionar os coracoes no lugar certo
        self.hp = 15
        self.hearts = []
        y = int(screen_size[1] - heart_height * 2)

        for i in range(self.hp):

            step = ((heart_width*1.5) * self.hp)/2

            x = int(screen_size[0]/2 - step) + (heart_width * 1.5) * i

            self.hearts.append(
                Rect(int(x), int(y), int(heart_width), int(heart_height)))

    def move(self, direction):
        self.direction = direction

    def update(self):
        self.battery.update()

        if self.alive and self.hp <= 0:
            self.alive = False

        if self.x >= screen_size[0] - self.width * 2:
            self.x -= SPEED

        if self.x <= self.width:
            self.x += SPEED

        if self.direction == 'left':
            self.x -= SPEED

        if self.direction == 'right':
            self.x += SPEED

        self.rect = Rect(self.x, self.y, self.width, self.height)

    def draw(self, surf):
        self.battery.draw(surf)

        surf.blit(self.image, self.rect)

        for i_heart in range(len(self.hearts)):
            img = img_heart if self.hp > i_heart else img_heart_broken
            surf.blit(img, self.hearts[i_heart])

    def shoot(self):
        if not self.battery.blocked:
            self.battery.discharge()
            bullets_player_group.add(Bullet(self))

    def take_damage(self):
        self.hp -= 0


class Battery():
    def __init__(self):
        self.sprites = {}

        for _ in glob.glob(path.join(PATH_TO_ASSETS, 'space', 'battery?.png')):
            self.sprites[path.basename(_)] = pygame.image.load(_)

        self.img = self.sprites['battery0.png']
        self.height, self.width = self.img.get_size()
        self.charge = 0
        self.blocked = True
        self.x, self.y = int(screen_size[0] * .9), int(screen_size[1] * .9)

        self.rect = Rect(self.x, self.y, self.width, self.height)

    def discharge(self):
        self.charge -= 10

    def update(self):
        if self.charge < 100:
            self.charge += 1

        if self.charge >= 100:
            self.img = self.sprites['battery3.png']
            self.blocked = False

        elif self.charge >= 75:
            self.img = self.sprites['battery2.png']

        elif self.charge > 25:
            self.img = self.sprites['battery1.png']

        elif self.charge > 0:
            self.img = self.sprites['battery0.png']

        else:
            self.blocked = True

    def draw(self, surf):
        dimensions = (self.height * 4, self.width * 4)
        surf.blit(pygame.transform.scale(self.img, dimensions), self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, src, enemy=False):
        pygame.sprite.Sprite.__init__(self)

        sfx['bullet.wav'].play()

        self.image = load_image('space', 'bullet.png', 2)
        self.width, self.height = self.image.get_size()

        if enemy:
            self.image = pygame.transform.flip(self.image, False, True)

        self.x = src.x + src.width // 2 - self.width // 2
        self.y = src.y + src.height // 2 - self.height // 2
        self.direction = 'down' if enemy else 'up'

        self.rect = Rect(
            int(self.x), int(self.y),
            int(self.width), int(self.height))

        self.acc = 1

    def update(self):
        if self.y > screen_size[1] or self.y < 0:
            self.kill()

        self.acc += .1

        if self.direction == 'down':
            self.y = self.y + SPEED * self.acc
        else:
            self.y = self.y - SPEED * self.acc

        self.rect = Rect(
            int(self.x), int(self.y), int(self.width), int(self.height))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)

        self.init_x, self.init_y = x, y
        self.x, self.y = x, y

        self.sprites = {}
        self.sprite_i = 0

        for i in glob.glob(path.join(PATH_TO_ASSETS, 'space', 'enemy?.png')):
            key = path.basename(i)
            self.sprites[key] = load_image('space', key, 4)

        self.image = self.sprites[f'enemy{self.sprite_i}.png']

        self.width, self.height = self.image.get_size()

        self.rect = Rect(
            self.x - self.width // 2,
            self.y,
            self.width + self.width // 2,
            self.height)

        self.hp = 50

        self.direction = direction

    def update(self, boss=False):
        self.sprite_i = (self.sprite_i + ANIMATION_SPEED) % 2
        self.image = self.sprites[f'enemy{int(self.sprite_i)}.png']

        if self.direction == 'right':
            self.x += SPEED

        if self.direction == 'left':
            self.x -= SPEED

        if self.direction == 'right' and self.x > self.init_x + self.width * 2:
            self.direction = 'left'

        if self.direction == 'left' and self.x < self.init_x - self.width * 2:
            self.direction = 'right'

        self.rect = Rect(
            int(self.x), int(self.y),
            int(self.width), int(self.height))

    def draw(self, surf):
        screen.blit(self.image, self.rect)

    def shoot(self):
        bullets_enemy_group.add(Bullet(self, enemy=True))

    def take_damage(self):
        self.hp -= DAMAGE


class Boss(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = load_image('space', 'boss.png', 8)
        self.width, self.height = self.image.get_size()
        self.x = screen_size[0] / 2 - self.width / 2
        self.y = screen_size[1] / 2 - self.height / 2
        self.rect = Rect(
            int(self.x), int(self.y),
            int(self.width), int(self.height))

        self.alive = True
        self.hp = 1000
        self.direction = random.choice(['left', 'right'])
        self.acc = 1

    def update(self):

        if self.y >= screen_size[1] // 2 - self.height:
            self.y -= SPEED
            self.direction = random.choice(['left', 'right'])

        if self.y <= self.height:
            self.y += SPEED
            self.direction = random.choice(['left', 'right'])

        if self.x >= screen_size[0] - self.width * 2:
            self.x -= SPEED
            self.direction = random.choice(['up', 'down'])

        if self.x <= self.width:
            self.x += SPEED
            self.direction = random.choice(['up', 'down'])

        if self.direction == 'up':
            self.y -= SPEED

        if self.direction == 'down':
            self.y += SPEED

        if self.direction == 'right':
            self.x += SPEED

        if self.direction == 'left':
            self.x -= SPEED

        if pygame.time.get_ticks() % 25 == 0:
            self.direction = random.choice(['up', 'down', 'left', 'right'])
            self.shoot()

        self.rect = Rect(
            int(self.x), int(self.y),
            int(self.width), int(self.height))

    def shoot(self):
        bullets_enemy_group.add(Bullet(self, enemy=True))

    def draw(self, surf):
        screen.blit(self.image, self.rect)

    def take_damage(self):
        self.hp -= DAMAGE


class Platform(pygame.sprite.Sprite):
    def __init__(self, x):
        pygame.sprite.Sprite.__init__(self)
        self.x, self.y = x, screen_size[1] * 0.75
        self.image = load_image('space', 'platform.png', 4)
        self.width, self.height = self.image.get_size()
        self.rect = Rect(
            int(self.x), int(self.y), int(self.width), int(self.height))
        self.hp = 1000
        self.alive = True


class Menu():
    def __init__(self, callbacks={}):
        self.bg = load_image('space', 'bg-menu.png', 1)

        self.buttons = {
            'start': Button('center', 15, 'Play!', callbacks['start_space']),
            'game_over': Button('center', screen_size[1]/4, 'Try Again')}

        self.keys = {
            'start': [K_RETURN, K_SPACE],
            'exit': [K_ESCAPE, K_BACKSPACE]}

    def listen(self, event):
        if event.type == KEYDOWN:
            if event.key in self.keys['exit']:
                sys.exit()

            if event.key in self.keys['start']:
                self.buttons['start'].callback()

        if event.type == MOUSEBUTTONDOWN:
            if self.buttons['start'].clicked():
                self.buttons['start'].callback()

    def update(self):
        pass

    def draw(self, surf):
        surf.blit(self.bg, (0, 0))

        self.buttons['start'].draw(surf)

        draw_text(
            surf,
            f'SPACE v2.1',
            screen_size[0] * .5,
            screen_size[1] - 150,
            size=20, color=FONT_COLOR, align='center')

        draw_text(
            surf,
            f'Desenvolvido por Wellington',
            screen_size[0] * .5,
            screen_size[1] - 100,
            size=20, color=FONT_COLOR, align='center')

        draw_text(
            surf,
            f'Testado por Samuel',
            screen_size[0] * .5,
            screen_size[1] - 50,
            size=20, color=FONT_COLOR, align='center')


class Space():
    def __init__(self, boss=False, callbacks={}):
        self.bg_image = load_image('space', 'bg-space.png', 1)
        self.bg_size = self.bg_image.get_size()
        self.bg_x = self.bg_size[0] // 2 - screen_size[0]
        self.bg_shift = 0
        self.bg_color = (0, 0, 0)
        self.platforms = 5
        self.callbacks = callbacks
        self.boss = boss

        espaco = int(
            screen_size[0] - self.platforms * 100) / (self.platforms + 1)

        for i in range(self.platforms):
            platform_group.add(Platform(espaco * (i+1) + (i*100)))

        if self.boss:
            enemy_group.add(Boss())

        else:
            d = random.choice(['left', 'right'])
            enemy_model = Enemy(screen_size[0], screen_size[1], d)

            y_iterator = range(
                (enemy_model.height * 2), (screen_size[1] // 2),
                (enemy_model.height * 2))

            x_iterator = range(
                (enemy_model.width * 4),
                (screen_size[0] - enemy_model.width * 4),
                (enemy_model.width * 2))

            for y in y_iterator:
                d = 'left' if d == 'right' else 'right'
                for x in x_iterator:
                    enemy_group.add(Enemy(x, y, d))

            del(enemy_model)

    def listen(self, event):
        keys = {
            'attack': [K_SPACE],
            'left': [K_a, K_LEFT],
            'right': [K_d, K_RIGHT],
            'exit': [K_ESCAPE]}

        if event.type == KEYDOWN:
            if event.key in keys['attack']:
                player.shoot()

            if event.key in keys['left']:
                player.move('left')

            if event.key in keys['right']:
                player.move('right')

            if event.key in keys['exit']:
                self.callbacks['pause_space']()

        if event.type == KEYUP:
            if event.key in keys['left'] or event.key in keys['right']:
                player.direction = 'none'

        if event.type == BOT_SHOOT.type:
            random.choice(enemy_group.sprites()).shoot()

    def update(self):

        player_group.update()
        enemy_group.update()
        platform_group.update()
        bullets_enemy_group.update()
        bullets_player_group.update()

        # bullets cant pass through platforms!
        groupcollide(bullets_enemy_group, platform_group, True, False)
        groupcollide(bullets_player_group, platform_group, True, False)

        # player must take damage!
        if groupcollide(bullets_enemy_group, player_group, True, False):
            player.take_damage()
            sfx['damage.wav'].play()

        # hited enemy
        hited_enemys = groupcollide(
            bullets_player_group,
            enemy_group,
            True, False,
            pygame.sprite.collide_mask)

        for bullet, enemy in hited_enemys.items():
            enemy[0].take_damage()

            if enemy[0].hp <= 0:
                sfx['dead_enemy.wav'].play()
                enemy_group.remove(enemy[0])

        # compute how many moves the backgound
        self.bg_shift = int((player.x - screen_size[0] // 2) * .25)

    def draw(self, surf):
        screen.fill(self.bg_color)
        surf.blit(self.bg_image, (self.bg_x + self.bg_shift, 0))
        enemy_group.draw(surf)
        player.draw(surf)
        platform_group.draw(surf)
        bullets_enemy_group.draw(surf)
        bullets_player_group.draw(surf)


class Scoreboard():
    def __init__(self, score=0):
        self.score = score
        self.done = False
        self.wait = 0

    def update(self):
        if self.wait >= 250:
            self.done = True

        self.wait += 1

    def draw(self, surf):
        surf.blit(pygame.Surface(screen_size), (0, 0))

        draw_text(
            surf,
            f'SCORE:{self.score}',
            screen_size[0] // 2,
            screen_size[1] // 2,
            align='center', size=20, color=FONT_COLOR)

        draw_text(
            surf,
            'Loading...',
            screen_size[0] * .1,
            screen_size[1] * .9,
            size=20, color=FONT_COLOR)


class Game():
    def __init__(self):
        self.on_menu = True
        self.on_space = False
        self.on_scoreboard = False
        self.on_end = False
        self.score = 0

        self.make_screens()

    def update(self):
        # clean memory
        self.optimize()

        if self.on_menu:
            self.menu.update()

        if self.on_space:
            self.space.update()

            if len(enemy_group.sprites()) == 0:
                self.score += 100
                self.on_space = False
                self.make_screens(score=self.score)
                self.on_scoreboard = True
                player.move('none')
                make_groups()

            if player.hp <= 0:
                self.on_space = False
                self.on_menu = True
                self.score = 0
                self.make_screens()

        if self.on_scoreboard:
            self.scoreboard.update()

            if self.scoreboard.done:
                self.on_scoreboard = False
                boss = True if self.score in [
                    i for i in range(0, 100000, 1000)
                ] or self.score > 100000 else False

                self.make_screens(boss=boss)
                self.on_space = True

    def draw(self, surf):
        if self.on_menu:
            self.menu.draw(surf)

        if self.on_scoreboard:
            self.scoreboard.draw(surf)

        if self.on_space:
            self.space.draw(surf)

        if self.on_end:
            surf.blit(BG, (0, 0))
            self.buttons['game_over'].draw(surf)
            # self.btn_end.update(surf, 'Try Again')

            draw_text(
                surf,
                'Game Over',
                screen_size[0] / 2,
                screen_size[1] / 8,
                align='center', size=25, color=FONT_COLOR)

        pygame.display.flip()

    def listen(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_F4:

                if screen.get_flags() & FULLSCREEN:
                    pygame.display.set_mode(screen_size)
                else:
                    pygame.display.set_mode(screen_size, pygame.FULLSCREEN)

            if self.on_menu:
                self.menu.listen(event)

            if self.on_space:
                self.space.listen(event)

            if self.on_end:
                pass
                # if event.type == KEYDOWN and event.key == K_RETURN:
                #     pygame.mixer.music.stop()
                #     self.on_end, self.on_space = False, True

                # if event.type == MOUSEBUTTONDOWN:
                #     mouse_x, mouse_y = pygame.mouse.get_pos()
                #     if self.btn_end.isClicked(mouse_x, mouse_y):
                #         pygame.mixer.music.stop()
                #         self.on_end, self.on_space = False, True

    def callback_start_space(self):
        pygame.mixer.music.stop()
        self.on_menu, self.on_space = False, True

    def callback_pause_space(self):
        self.on_menu, self.on_space = True, False

    def make_screens(self, boss=False, score=0):
        self.menu = Menu(callbacks={
            'start_space': self.callback_start_space
        })
        self.space = Space(boss, callbacks={
            'pause_space': self.callback_pause_space
        })
        self.scoreboard = Scoreboard(score)

    def optimize(self):
        if len(bullets_player_group.sprites()) > 30:
            to_remove = bullets_player_group.sprites()[0]
            bullets_player_group.remove(to_remove)


# start
player = Player()


def make_groups():
    global enemy_group
    global platform_group
    global bullets_player_group
    global bullets_enemy_group
    global player_group

    enemy_group = pygame.sprite.Group()
    platform_group = pygame.sprite.Group()
    bullets_player_group = pygame.sprite.Group()
    bullets_enemy_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    player_group.add(player)


make_groups()

game = Game()

while True:
    clock.tick(FPS)
    game.listen()
    game.update()
    game.draw(screen)
