import pygame
from pygame import mixer
import os
import random
import csv
import button

mixer.init()
pygame.init()



WIDTH = 800
HEIGHT = int(WIDTH * 0.8)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('APRUEBEME PORFAS')

#set framerate
clock = pygame.time.Clock()
FPS = 60

#define game variables
GRAVEDAD = 0.75
SCROLL = 200
FILAS = 16
COLS = 150
TAMAÑO_TILE = HEIGHT // FILAS
TIPO_TILES = 21
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
level_2 = 2
level_3 = 3
start = False

#define player action variables
mover_izq = False
mover_der = False
disparar = False

#load music and sounds
pygame.mixer.music.load('audio/Don.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0, 5000)


jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.05)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.05)

enemigo_lastimado = pygame.mixer.Sound('audio/dog_hurt.mp3.mp3')
enemigo_lastimado.set_volume(0.05)

game_over_musica = pygame.mixer.Sound('audio/game_over.mp3')



#load images
#button images

#background
pine1_img = pygame.image.load('img/Background/sand.png').convert_alpha()
palm_img = pygame.image.load('img/Background/palm.png').convert_alpha()
sand_img = pygame.image.load('img/Background/sandos.png').convert_alpha()
ocean_img = pygame.image.load('img/Background/Ocean.png').convert_alpha()

img_list = []
for x in range(TIPO_TILES):
	img = pygame.image.load(f'img/Tile/{x}.png')
	img = pygame.transform.scale(img, (TAMAÑO_TILE, TAMAÑO_TILE))
	img_list.append(img)
#banana
banana_img = pygame.image.load('img/icons/banana.png').convert_alpha()

#pick up boxes
sandia = pygame.image.load('img/icons/sandia.png').convert_alpha()
# cereza = pygame.image.load('img/icons/cereza.png').convert_alpha()
# manzana = pygame.image.load('img/icons/manzana.png').convert_alpha()



	
cajita = {
	'vida'	: sandia
}

#define colours
BG = (205,163,115)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)


