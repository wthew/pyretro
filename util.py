import pygame, glob, os
from pygame.locals import  *

screen_size = (800, 600)

# caminhos importantes
PATH_TO_ASSETS = os.path.join(os.path.dirname(__file__), 'assets')
PATH_TO_SFX = os.path.join(PATH_TO_ASSETS, 'soundtracks', 'sfx')

# inicialização geral do pygame
pygame.init()
pygame.display.init()
pygame.mixer.init()
screen = pygame.display.set_mode((screen_size))

# carrega todos os sfx para a memoria
sfx = {}
for file in glob.glob(os.path.join(PATH_TO_SFX, '*.wav')):
    sfx[os.path.basename(file)] = pygame.mixer.Sound(file)

# funcoes para ajudar
def draw_text(surf, text, x, y, align="topleft", size=20, color=(225, 225, 225)):
    font = pygame.font.Font(os.path.join(PATH_TO_ASSETS, 'pixel-font.ttf'), size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(**{align: (x, y)})
    surf.blit(text_surface, text_rect)

def load_image(path, filename, scale=2):
    img = pygame.image.load(os.path.join(PATH_TO_ASSETS, path, filename))
    height, width = img.get_size()
    return pygame.transform.scale(img, (height * scale, width * scale))

# cores
color_text = (0, 0, 0)
color_bg = (225, 225, 225)

class Button():
    def __init__(self, tamX, tamY, posX, posY, text = '', flat = False):
        self.tamX = tamX
        self.tamY = tamY
        self.posX = screen_size[0] / 2 - self.tamX / 2 if posX == 'center' else posX
        self.posY = posY
        self.text = text
        self.flat = flat
        self.rect = Rect(self.posX, self.posY, self.tamX, self.tamY)
        self.surf = pygame.Surface((self.tamX, self.tamY))

    def update(self, surf, text):
        self.surf.fill(color_bg)
        pygame.draw.rect(surf, color_bg, self.rect)
        draw_text(surf, text, self.posX + self.tamX / 2, self.posY + self.tamY / 2, align='center', size=25, color=color_text)

    def isClicked(self, mouseX, mouseY):
        return (mouseX > self.posX and mouseX < self.posX + self.tamX and mouseY > self.posY and mouseY < self.posY + self.tamY)
