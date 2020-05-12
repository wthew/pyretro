# -*- coding: utf-8 -*-
import pygame
import sys
import random
from os import path
from pygame.locals import *
from pygame.sprite import groupcollide, spritecollide
from util import *


pygame.display.set_caption('Race')
clock = pygame.time.Clock()

FPS = 60
SPEED = 8  # default 8
ANIMATION_SPEED = 0.1


class Car(pygame.sprite.Sprite):
    def __init__(self):

        self.sprites = {}

        for _ in glob.glob(path.join(PATH_TO_ASSETS, 'race', 'car-*-*.png')):
            self.sprites[path.basename(_)] = pygame.image.load(_)

        self.state = 'idle'
        self.sprite_i = 0
        self.image = self.sprites[
            f'car-{self.state}-{int(self.sprite_i)}.png']
        self.width, self.height = self.image.get_size()

        self.x = int(screen_size[0] * .5 - self.width * .5)
        self.y = int(screen_size[1] * .8)

        self.rect = Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.sprite_i = (self.sprite_i + ANIMATION_SPEED) % 2
        self.image = self.sprites[
            f'car-{self.state}-{int(self.sprite_i)}.png']

    def draw(self, surf):
        surf.blit(self.image, self.rect)


class Velocimetro:
    pass


class Road:
    def __init__(self):
        self.points = [
            (int(screen_size[0] * .25), screen_size[1]),
            (int(screen_size[0] * .40), int(screen_size[1] * .50)),
            (int(screen_size[0] * .60), int(screen_size[1] * .50)),
            (int(screen_size[0] * .75), screen_size[1])]

    def update(self):
        pass

    def draw(self, surf):
        pygame.draw.polygon(
            surf,
            (100, 100, 100),
            self.points)


class Game:
    def __init__(self):
        self.road = Road()

    def listen(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()

            if event.type == KEYDOWN and event.key == K_F4:

                if screen.get_flags() & FULLSCREEN:
                    pygame.display.set_mode(screen_size)
                else:
                    pygame.display.set_mode(screen_size, pygame.FULLSCREEN)

    def update(self):
        self.road.update()
        car.update()

    def draw(self, surf):
        self.road.draw(surf)
        car.draw(surf)
        pygame.display.flip()


game = Game()
car = Car()

while True:
    clock.tick(FPS)
    game.listen()
    game.update()
    game.draw(screen)
