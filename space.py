# -*- coding: utf-8 -*-
import pygame
import sys
import random
from os import path
from time import sleep
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


class Screen():
    def __init__(self, **kwargs):
        self.navigate = kwargs.get('navigate', lambda: 0)

    def update(self):
        pass
    
    def listen(self):
        pass

    def draw(self, surf):
        pass


class Menu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg = load_image('space', 'bg-menu.png', 1)

        self.buttons = {
            'start': Button('center', 15, 'Play!', lambda: self.navigate('space')),
            'game_over': Button('center', screen_size[1]/4, 'Try Again')
        }

        self.keys = {
            'start': [K_RETURN, K_SPACE],
            'exit': [K_ESCAPE, K_BACKSPACE]
        }

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

        # draw_text(
        #     surf,
        #     f'Desenvolvido por Wellington',
        #     screen_size[0] * .5,
        #     screen_size[1] - 100,
        #     size=20, color=FONT_COLOR, align='center')

        # draw_text(
        #     surf,
        #     f'Testado por Samuel',
        #     screen_size[0] * .5,
        #     screen_size[1] - 50,
        #     size=20, color=FONT_COLOR, align='center')


class Space(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bg_image = load_image('space', 'bg-space.png', 1)
        self.bg_size = self.bg_image.get_size()
        self.bg_x = self.bg_size[0] // 2 - screen_size[0]
        self.bg_shift = 0
        self.bg_color = (0, 0, 0)

        self.platforms = 5

        self.boss = kwargs.get('boss')

        self.update_score = kwargs.get('update_score', lambda: 0)

        self.actions_keys = {
            # action: [trigger keys list], callback

            'attack': ([K_SPACE], lambda: player.shoot()),
            'left': ([K_a, K_LEFT], lambda: player.move('left')),
            'right': ([K_d, K_RIGHT], lambda: player.move('right')),
        }


        espaco = int(screen_size[0] - self.platforms * 100) / (self.platforms + 1)

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
    
        if event.type == KEYDOWN:
            for action in self.actions_keys.keys():
                if event.type in self.actions_keys[action][0]: self.actions_keys[action][1]()


        if event.type == KEYUP:
            if event.key in self.actions_keys['left'][0] or event.key in self.actions_keys['right'][0]:
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

        if len(enemy_group.sprites()) == 0:
            self.update_score(10)
            player.move('none')

        if player.hp <= 0:
            self.update_score(0)
            self.navigate('end')

        
        if len(bullets_player_group.sprites()) > 30:
            to_remove = bullets_player_group.sprites()[0]
            bullets_player_group.remove(to_remove)

    def draw(self, surf):
        screen.fill(self.bg_color)
        surf.blit(self.bg_image, (self.bg_x + self.bg_shift, 0))
        enemy_group.draw(surf)
        player.draw(surf)
        platform_group.draw(surf)
        bullets_enemy_group.draw(surf)
        bullets_player_group.draw(surf)


class Scoreboard(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = kwargs.get('score', 0)
        self.done = False
        self.wait = 5

    def update(self):
        
        self.wait -= 1
        sleep(2)

        if self.wait <= 0:
            boss = True if self.score in [
                i for i in range(0, 100000, 1000)
            ] or self.score > 100000 else False

            self.navigate('space', boss=True)

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


class End(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update(self):
        pass

    def draw(self, surf):
        surf.blit(BG, (0, 0))
        self.buttons['game_over'].draw(surf)
        # self.btn_end.update(surf, 'Try Again')

        draw_text(
            surf,
            'Game Over',
            screen_size[0] / 2,
            screen_size[1] / 8,
            align='center', size=25, color=FONT_COLOR)


class Game():
    def __init__(self):

        self.state = {
            'score': 0
        }

        self.make_screens()

        self.state['on'] = self.menu
    
    def _set_score(self, s):
        self.state['score'] = s

    def update(self):
        self.state['on'].update()

    def draw(self, surf):
        self.state['on'].draw(surf)
        pygame.display.flip()

    def listen(self):
        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit()

            if event.type == KEYDOWN and event.key == K_F4:
                if screen.get_flags() & FULLSCREEN:
                    pygame.display.set_mode(screen_size)
                else:
                    pygame.display.set_mode(screen_size, pygame.FULLSCREEN)

            self.state['on'].listen(event)


    def navigate(self, to, **kwargs):
        self.make_screens(**kwargs)
        self.state['on'] = to
        reset_sprite_groups()

    def make_screens(self, boss=False):
        self.menu = Menu(
            navigate=self.navigate,
        )
        self.space = Space(
            boss,
            navigate=self.navigate,
            update_score=self._set_score
        )
        self.scoreboard = Scoreboard(
            score=self.state['score'],
            navigate=self.navigate,
        )



# start
player = Player()

# make sprites groups
enemy_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
bullets_player_group = pygame.sprite.Group()
bullets_enemy_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
player_group.add(player)

def reset_sprite_groups():
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


reset_sprite_groups()

game = Game()

while True:
    clock.tick(FPS)
    game.listen()
    game.update()
    game.draw(screen)
