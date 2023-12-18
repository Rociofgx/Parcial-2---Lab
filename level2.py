import pygame
from pygame import mixer
import os
import random
import csv
import button
from config import *
from level1 import *

mixer.init()
pygame.init()

class Player(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.fuente = pygame.font.Font(None,28)
        self.score = 0
        self.tiempo = 40
        self.level_completed = False
        self.evento_de_tiempo = pygame.USEREVENT +1
        pygame.time.set_timer(self.evento_de_tiempo,1000)

        self.vida = True
        self.char_type = char_type
        self.speed = speed
        self.disparar_cooldown = 10
        self.vida = 100
        self.vida_max = self.vida
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        #variables para el IA
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.kieto= False  #kieto
        self.kieto_contador = 0 #contador de kieto
        
        """Se cargan las animaciones. Van a ser recorridas mediante un for."""
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            #Se crea una lista temporal para almacenar las imágenes de la animación actual.
            temp_list = []
            #Se cuenta el número de archivos en la carpeta
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
                #la lista temporal se agrega a la lista original, de animación.
            self.animation_list.append(temp_list)

        """Ordena las imágenes asociadas con diferentes tipos de animaciones depende el fotograma actual de la animación."""
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()


    def update(self):
        self.update_animation()
        self.check_vida()
        ##Cooldown del disparo
        if self.disparar_cooldown > 0:
            self.disparar_cooldown -= 1


    def move(self, mover_izq, mover_der):
        """Se resetean las variables de movimiento"""
        screen_scroll = 0
        dx = 0
        dy = 0

        """Se asignan las variables si se mueve a la izquierda o derecha"""
        if mover_izq:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if mover_der:
            dx = self.speed
            self.flip = False
            self.direction = 1

        """Salto"""
        if self.jump == True and self.in_air == False:
            self.vel_y = -13
            self.jump = False
            self.in_air = True

        """Se aplica gravedad para que el personaje baje"""
        self.vel_y += GRAVEDAD
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        """Se empiezan a chequear las colisiones"""
        for tile in world.lista_obstaculo:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            """Se chequean el eje Y, que sería las plataformas"""
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom


        """Colision con el agua. Se muere porque es otaku"""
        if pygame.sprite.spritecollide(self, agua_grupo, False):
            self.vida = 0

        """"Si se salió del mapa"""
        if self.rect.bottom > HEIGHT:
            self.vida = 0


        """Si se salio de los esquinas"""
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > WIDTH:
                dx = 0

        """Se actualiza el rectángulo"""
        self.rect.x += dx
        self.rect.y += dy

        """Se updatea el scroll basado en la posocion del player. Esto comprueba si el jugador está cerca del borde derecho del nivel y si hay más nivel para desplazarse hacia adelante."""
        if self.char_type == 'player':
            if (self.rect.right > WIDTH - SCROLL and bg_scroll < (world.level_length * TAMAÑO_TILE) - WIDTH)\
                or (self.rect.left < SCROLL and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll


    """Para disparar.Permite que mi player dispare bananas. Se le da la posicion para que arranque SIEMPRE desde el gato banana"""
    def disparar(self):
        if self.disparar_cooldown == 0:
            self.disparar_cooldown = 20
            banana_instance = Banana(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            banana_grupo.add(banana_instance)	
            
            shot_fx.play()
    

    """Propiedades del enemigo. Primero chequea que ambos estén vivos."""
    def perro(self):
        if self.vida and player.vida:
            if self.kieto== False and random.randint(1, 200) == 1:
                self.update_action(0)#kieto
                self.kieto= True
                self.kieto_contador = 50
            
            #Se verifica que si está quiero, cambie su posicion a caminar. Se le da un rango random para que lo haga.	
            else:
                if self.kieto== False:
                    if self.direction == 1:
                        perro_mover_der = True
                    else:
                        perro_mover_der = False
                    perro_mover_izq = not perro_mover_der
                    self.move(perro_mover_izq, perro_mover_der)
                    self.update_action(1)#1: run
                    self.move_counter += 1
                    
            #El límite que tiene el perro para caminar, es el tamaño del tile en el que vaya a aparecer.
                    if self.move_counter > TAMAÑO_TILE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.kieto_contador -= 1
                    if self.kieto_contador <= 0:
                        self.kieto= False

        #El scroll no va a hacer que desaparezca el perro.
        self.rect.x += screen_scroll

    """Cambia la animación dependiendo el frame."""
    def update_animation(self):
        
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        #hequea si pasó mucho tiempo del ultimo frame.
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #si se acabaron los frames, que se reinicie.
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0



    def update_action(self, new_action):
        #Chequea si la accion es distinta a la anterior
        if new_action != self.action:
            self.action = new_action
            #Cambia los frames
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()



    def check_vida(self):
        if self.vida <= 0:
            self.vida = 0
            self.speed = 0
            self.vida = False
            self.update_action(3)


    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class Banana(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.original_image = banana_img 
        self.image = pygame.transform.scale(self.original_image, (20, 20))
        self.rect = self.image.get_rect(center=(x, y)).inflate(-10, -10)  # Reduce el tamaño del rectángulo de colisión)
        self.direction = direction
        

    def update(self):
        # Acá empezamos a mover la bananita
        self.rect.x += (self.direction * self.speed) + screen_scroll
        
        #Se verifica que si la banana sale de la pantalla, se muera
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()
        # Verifica colisión con los obstaculos
        for tile in world.lista_obstaculo:
            if tile[1].colliderect(self.rect):
                self.kill()

        # Verificar colisión con personajes
        if pygame.sprite.spritecollide(player, banana_grupo, False):
            if player.vida:
                player.vida -= 5
                self.kill()
        for enemigo in grupo_enemigo:
            if pygame.sprite.spritecollide(enemigo, banana_grupo, False, pygame.sprite.collide_rect):
                if enemigo.vida:
                    enemigo.vida -= 25
                    self.kill()
                    if enemigo.vida <= 0: #####
                        player.score += 50 #####
                        print(player.score) #####
                        enemigo_lastimado.play()
                    
        screen.blit(self.image, self.rect)

"""Se crea una lista bidimensional que representa el diseño del invel. La lista tiene filas y columnas."""
world_data = []
for fila in range(FILAS):
	r = [-1] * COLS
	world_data.append(r)

"""Carga los datos del nivel desde el CSV"""
"""Abre el archivo CSV correspondiente al nivel actual (level). Este archivo contiene información sobre los tipos de tiles en cada posición del nivel.
Utiliza un lector de CSV para iterar sobre las filas y columnas del archivo CSV.
Convierte cada valor leído a entero (int(tile)) y lo asigna a la posición correspondiente en la lista world_data."""


with open(f'level{level_2}_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, fila in enumerate(reader):
		for y, tile in enumerate(fila):
			world_data[x][y] = int(tile)
world = Mundo()
player, barra_vida= world.procesar_data(world_data)



run = True
while run:
    clock.tick(FPS)

    if start == False:
        screen.fill(BG)
        if start_button.draw(screen):
            start = True
            start_intro = True

        """Intento de niveles"""
        if nivel1_button.draw(screen):
            level
            start = True
            start_intro = True

        if nivel2_button.draw(screen):
            level_2 = 2
            start = True
            start_intro = True

        if nivel3_button.draw(screen):
            level_3 = 3
            start = True
            start_intro = True

        if exit_button.draw(screen):
            run = False
    else:
        draw_bg()
        world.draw()
        barra_vida.draw(player.vida)
        player.update()
        player.draw()

        for enemigo in grupo_enemigo:
            enemigo.perro()
            enemigo.update()
            enemigo.draw()
        banana_grupo.update()
        item_box_grupo.update()
        agua_grupo.update()
        banana_grupo.draw(screen)
        item_box_grupo.draw(screen)
        agua_grupo.draw(screen)
        if player.vida:
            if disparar:
                player.disparar()
            if player.in_air:
                player.update_action(2)  # 2: saltar
            elif mover_izq or mover_der:
                player.update_action(1)  # 1: correr
            else:
                player.update_action(0)  # 0: inactivo
            screen_scroll = player.move(mover_izq, mover_der)
            bg_scroll -= screen_scroll
        if player.vida <= 0:
            game_over_menu()
        if player.score >= 350:
            ganaste_menu()

    for event in pygame.event.get():
       
        if event.type == pygame.QUIT:
            run = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                mover_izq = True
            if event.key == pygame.K_d:
                mover_der = True
            if event.key == pygame.K_SPACE:
                disparar = True
            if event.key == pygame.K_w and player.vida:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False
            # if event.key == pygame.K_p:
            #     pausa_menu()


        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                mover_izq = False
            if event.key == pygame.K_d:
                mover_der = False
            if event.key == pygame.K_SPACE:
                disparar = False
        
        if event.type == player.evento_de_tiempo: #####
                    if player.tiempo >= 0: #####
                        print(player.tiempo) #####
                        player.tiempo -= 1 #####
                        if player.tiempo == 0:
                            game_over_menu()
                            
        
            
    

        
    pygame.display.update()

pygame.quit()