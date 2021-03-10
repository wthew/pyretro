import pygame
import glob
import os

from pygame.locals import *

screen_size = (800, 600)

PATH_TO_ASSETS = os.path.join(os.path.dirname(__file__), 'assets')

WHITE = (255, 255, 255)

# init pygame
pygame.init()
pygame.display.init()
pygame.mixer.init()
screen = pygame.display.set_mode((screen_size))

font_path = os.path.join(PATH_TO_ASSETS, 'pixel-font.ttf')

# loads all sfx
sfx_path = os.path.join(PATH_TO_ASSETS, 'soundtracks', 'sfx', '*.wav')
sfx = {}
for file in glob.glob(sfx_path):
    sfx[os.path.basename(file)] = pygame.mixer.Sound(file)
    sfx[os.path.basename(file)].set_volume(.1)


def draw_text(surf, text, x, y, align='topleft', size=20, color=WHITE):
    font = pygame.font.Font(font_path, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(**{align: (x, y)})
    surf.blit(text_surface, text_rect)


def load_image(path, filename, scale=2):
    img = pygame.image.load(os.path.join(PATH_TO_ASSETS, path, filename))
    height, width = img.get_size()
    return pygame.transform.scale(img, (height * scale, width * scale))


# colors
color_text = (0, 0, 0)
color_bg = (225, 225, 225)


class Button():
    def __init__(self, posX, posY, text='', callback=None):
        """position in Xaxis, Yaxis, text, and function"""
        self.tamX = 250
        self.tamY = 45

        self.callback = callback

        self.posX = screen_size[0] / 2 - self.tamX / 2 if posX == 'center' else posX
        self.posY = screen_size[1] / 2 - self.tamY / 2 if posY == 'center' else posY

        self.text = text

        self.rect = Rect(self.posX, self.posY, self.tamX, self.tamY)
        self.surf = pygame.Surface((self.tamX, self.tamY))

    def draw(self, surf):
        self.surf.fill(color_bg)
        pygame.draw.rect(surf, color_bg, self.rect)

        textPosX = self.posX + self.tamX / 2
        textPosY = self.posY + self.tamY / 2

        draw_text(
            surf,
            self.text,
            textPosX,
            textPosY,
            align='center',
            size=25,
            color=color_text)

    def clicked(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        return \
            mouse_x > self.posX and \
            mouse_x < self.posX + self.tamX and \
            mouse_y > self.posY and \
            mouse_y < self.posY + self.tamY
