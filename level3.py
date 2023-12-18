import pygame
from pygame import mixer
import os
import random
import csv
import button
from config import *

mixer.init()
pygame.init()


"""Imagenes para los botones"""
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
nivel1_img = pygame.image.load('img/nivel1.png').convert_alpha()
nivel2_img = pygame.image.load('img/nivel2.png').convert_alpha()
nivel3_img = pygame.image.load('img/nivel3.png').convert_alpha()

"""Inicializo lo que voy a utilizar"""
mixer.init()
pygame.init()

pygame.font.init()

"""Dibujo el background. Aplico un for dentro de mi función, para que recorra entre los 5 archivos que tengo. Les doy coordenadas para poder simular el background"""
def draw_bg():
    screen.fill(BG)
    width = ocean_img.get_width()
    for x in range(5):
        screen.blit(ocean_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(sand_img, ((x * width) - bg_scroll * 0.6, HEIGHT - sand_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, HEIGHT - pine1_img.get_height() - 150))
        screen.blit(palm_img, ((x * width) - bg_scroll * 0.8, HEIGHT - palm_img.get_height()))

"""Clase player, donde se le da forma al protagonita y al enemigo"""
class Player(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.fuente = pygame.font.Font(None,28)
        self.score = 0
        self.tiempo = 40

        self.evento_de_tiempo = pygame.USEREVENT +1
        pygame.time.set_timer(self.evento_de_tiempo,1000)

        self.level_completed = False

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

        if pygame.sprite.collide_rect(player, enemigo) and enemigo.vida > 0:
             player.vida -= 1

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
            if self.kieto == False and random.randint(1, 200) == 1:
                self.update_action(0)#0: idle
                self.kieto = True
                self.kieto_counter = 50
            #check if the ai in near the player
            if self.vision.colliderect(player.rect):
                #stop running and face the player
                self.update_action(0)#0: idle
                #disparar
                self.disparar()
            else:
                if self.kieto == False:
                    if self.direction == 1:
                        ai_mover_der = True
                    else:
                        ai_mover_der = False
                    ai_mover_izq = not ai_mover_der
                    self.move(ai_mover_izq, ai_mover_der)
                    self.update_action(1)#1: run
                    self.move_counter += 1
                    #update ai vision as the enemigo moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TAMAÑO_TILE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.kieto_contador -= 1
                    if self.kieto_contador <= 0:
                        self.kieto = False

        #scroll
        self.rect.x += screen_scroll


    def update_animation(self):
        
        ANIMATION_COOLDOWN = 100
        #update image depending on current frame
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

    def chequear_nivek(self):
        if self.score >=200:
            self.nivel_completo =  True
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class Mundo():
    def __init__(self):
        self.lista_obstaculo = []

    def procesar_data(self, data):
        self.level_length = len(data[0])
        """Itera sobre cada valor de la lista"""
        for y, fila in enumerate(data):
            for x, tile in enumerate(fila):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TAMAÑO_TILE
                    img_rect.y = y * TAMAÑO_TILE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.lista_obstaculo.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        agua = Agua(img, x * TAMAÑO_TILE, y * TAMAÑO_TILE)
                        agua_grupo.add(agua)
                    
                    elif tile == 15:#create player
                        player = Player('player', x * TAMAÑO_TILE, y * TAMAÑO_TILE, 1.65, 5)
                        barra_vida = BarraVida(10, 10, player.vida, player.vida)
                    elif tile == 16:#create enemies
                        enemigo = Player('enemigo', x * TAMAÑO_TILE, y * TAMAÑO_TILE, 1.65, 2)
                        grupo_enemigo.add(enemigo)
        
                    elif tile == 19:#create vida box
                        item_box = ItemBox('vida', x * TAMAÑO_TILE, y * TAMAÑO_TILE)
                        item_box_grupo.add(item_box)
                    

        return player, barra_vida


    
    def draw(self):
        for tile in self.lista_obstaculo:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])
        self.superficie_texto_score = player.fuente.render(f"{player.score:05d}", False, (0, 0, 0)) #####
        screen.blit(self.superficie_texto_score, (700, 16)) #####

        self.tiempo_baja = player.fuente.render(f"{player.tiempo}", False, (0, 0, 0)) #####
        screen.blit(self.tiempo_baja, (400, 16))


class Agua(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TAMAÑO_TILE // 2, y + (TAMAÑO_TILE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class ItemBox(pygame.sprite.Sprite): ##DARLE UNA FRUTA
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = cajita[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TAMAÑO_TILE // 2, y + (TAMAÑO_TILE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
        """Chequea si el prota comio frutita"""
        if self.rect.colliderect(player.rect):
            player.score += 50 #####
            player.vida +=10
            player.vida_max = 100
            print(player.score) #####
            self.kill()


class BarraVida():
    def __init__(self, x, y, vida, vida_max):
        self.x = x
        self.y = y
        self.vida = vida
        self.vida_max = vida_max

    def draw(self, vida):
        self.vida = vida
        prop = self.vida / self.vida_max
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * prop, 20))


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


grupo_enemigo = pygame.sprite.Group()
banana_grupo = pygame.sprite.Group()
item_box_grupo = pygame.sprite.Group()
agua_grupo = pygame.sprite.Group()

"""Mis botones"""
start_button = button.Button(WIDTH // 4 - 130, HEIGHT // 2 - 300, start_img, 0.5)
exit_button = button.Button(WIDTH // 4 - 110, HEIGHT // 2 - 200, exit_img, 0.5)
restart_button = button.Button(WIDTH // 4 - 100, HEIGHT // 2 - 50, restart_img, 0.5)

nivel1_button = button.Button(3 * WIDTH // 4 - 130, HEIGHT // 2 + 50, nivel1_img, 0.5)
nivel2_button = button.Button(3 * WIDTH // 4 - 130, HEIGHT // 2 + 120, nivel2_img, 0.5)
nivel3_button = button.Button(3 * WIDTH // 4 - 130, HEIGHT // 2 + 190, nivel3_img, 0.5)

def mostrar_texto(texto, x, y, color, tamaño=32, centrar=False):
    fuente = pygame.font.Font(None, tamaño)
    texto_surface = fuente.render(texto, True, color)
    texto_rect = texto_surface.get_rect()
    if centrar:
        texto_rect.center = (x, y)
    else:
        texto_rect.topleft = (x, y)
    screen.blit(texto_surface, texto_rect)


"""Se crea una lista bidimensional que representa el diseño del invel. La lista tiene filas y columnas."""
world_data = []
for fila in range(FILAS):
    r = [-1] * COLS
    world_data.append(r)

"""Carga los datos del nivel desde el CSV"""
"""Abre el archivo CSV correspondiente al nivel actual (level). Este archivo contiene información sobre los tipos de tiles en cada posición del nivel.
Utiliza un lector de CSV para iterar sobre las filas y columnas del archivo CSV.
Convierte cada valor leído a entero (int(tile)) y lo asigna a la posición correspondiente en la lista world_data."""


with open(f'level{level_3}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, fila in enumerate(reader):
        for y, tile in enumerate(fila):
            world_data[x][y] = int(tile)
world = Mundo()
player, barra_vida= world.procesar_data(world_data)

def game_over_menu():
    game_over = True

    while game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_over = False
                    player.vida = 100
                    player.score = 0
        pygame.mixer.music.stop()
        game_over_musica.play()
        screen.fill(BLACK)
        mostrar_texto("Game Over", WIDTH // 2, HEIGHT // 4, RED, tamaño=48, centrar=True)
        mostrar_texto(f"Puntaje: {player.score}", WIDTH // 2, HEIGHT // 2, WHITE, tamaño=32, centrar=True)
        mostrar_texto("Presiona R para reiniciar", WIDTH // 2, HEIGHT * 3 // 4, WHITE, tamaño=24, centrar=True)
        pygame.display.flip()
        clock.tick(FPS)

def ganaste_menu():
    ganaste = True
    while ganaste:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()

        screen.fill(BLACK)
        mostrar_texto("¡GANASTE!", WIDTH // 2, HEIGHT // 4, WHITE, tamaño=48, centrar=True)
        mostrar_texto(f"Puntaje: {player.score}", WIDTH // 2, HEIGHT // 2, WHITE, tamaño=32, centrar=True)
        mostrar_texto("Presiona Q para salir", WIDTH // 2, HEIGHT * 3 // 4, WHITE, tamaño=32, centrar=True)
        pygame.display.flip()
        clock.tick(FPS)


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
        if player.score >= 500:
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
                            pass
        
            
    

        
    pygame.display.update()

pygame.quit()