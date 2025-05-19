import pygame
import sys
import random

pygame.init()

# Pantalla
width, height = 700, 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("ReciclaGame")

# Carga de imágenes
tacho_image = pygame.transform.scale(pygame.image.load("imgs/blanco.png"), (120, 180))  # Tacho reciclaje blanco
barrier_image = pygame.transform.scale(pygame.image.load("imgs/barrier.png"), (150, 30))
background_image = pygame.transform.scale(pygame.image.load("imgs/fondo.png"), (width, height))

# Lista de basura
recyclable_names = ['blanco1', 'blanco2', 'blanco3']
non_recyclable_names = ['negro1', 'negro2', 'negro3', 'verde1', 'verde2', 'verde3']
all_trash_names = recyclable_names + non_recyclable_names

# Jugador
player_rect = pygame.Rect(width // 2 - 40, height - 120, 80, 120)
player_speed = 15

# Basura
falling_trash = []
trash_speed = 5

# Reloj y puntuación
clock = pygame.time.Clock()
score = 0
lives = 3
barrier_uses = 3
correct_recyclables = 0
wrong_recyclables = 0

# Sonidos
pygame.mixer.music.load("music/fondo.mp3")
pygame.mixer.music.play(-1)

coin_sound = pygame.mixer.Sound("music/coin.mp3")
error_sound = pygame.mixer.Sound("music/error.mp3")
gameover_sound = pygame.mixer.Sound("music/gameover.mp3")
victory_sound = pygame.mixer.Sound("music/victoria.mp3")

error_sound.set_volume(1.0)

# Fuentes
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 80)

# Pantalla final
def show_end_screen(text, color):
    screen.fill((255, 255, 255))
    message = big_font.render(text, True, color)
    text_rect = message.get_rect(center=(width // 2, height // 2))
    screen.blit(message, text_rect)
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()

# Generar basura
def generate_trash():
    name = random.choice(all_trash_names)
    image = pygame.transform.scale(pygame.image.load(f"imgs/{name}.png"), (75, 75))
    trash_type = 'reciclable' if name in recyclable_names else 'no_reciclable'
    rect = image.get_rect()
    rect.x = random.randint(0, width - rect.width)
    rect.y = -50
    return {'name': name, 'type': trash_type, 'image': image, 'rect': rect, 'counted': False}

# Malla
barrier_active = False
barrier_rect = None
barrier_speed = 8

# Bucle principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movimiento
    keys = pygame.key.get_pressed()
    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player_rect.left > 0:
        player_rect.x -= player_speed
    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player_rect.right < width:
        player_rect.x += player_speed

    # Lanzar malla
    if keys[pygame.K_SPACE] and barrier_uses > 0 and not barrier_active:
        barrier_uses -= 1
        barrier_rect = pygame.Rect(player_rect.x + player_rect.width // 2 - 60, player_rect.y - 20, 120, 20)
        barrier_active = True

    if barrier_active:
        barrier_rect.y -= barrier_speed
        if barrier_rect.y < -20:
            barrier_active = False

    # Generar basura aleatoria
    if random.randint(0, 100) < 3:
        falling_trash.append(generate_trash())

    trash_to_remove = []

    for trash in falling_trash:
        trash['rect'].y += trash_speed

        if trash['rect'].colliderect(player_rect) and not trash['counted']:
            trash['counted'] = True
            if trash['type'] == 'reciclable':
                score += 5
                correct_recyclables += 1
                coin_sound.play()
            else:
                lives -= 1
                wrong_recyclables += 1
                error_sound.play()
            trash_to_remove.append(trash)

        if trash['rect'].y > height:
            trash_to_remove.append(trash)

        if barrier_active and trash['rect'].colliderect(barrier_rect):
            trash_to_remove.append(trash)
            barrier_active = False

    for trash in trash_to_remove:
        if trash in falling_trash:
            falling_trash.remove(trash)

    # Verificar victoria o derrota
    if correct_recyclables >= 5:
        pygame.mixer.music.stop()
        victory_sound.play()
        show_end_screen("¡Has ganado!", (0, 150, 0))

    if wrong_recyclables >= 3 or lives <= 0:
        pygame.mixer.music.stop()
        gameover_sound.play()
        show_end_screen("¡Has perdido!", (200, 0, 0))

    # Dibujar todo
    screen.blit(background_image, (0, 0))
    screen.blit(tacho_image, player_rect.topleft)

    if barrier_active:
        screen.blit(barrier_image, barrier_rect.topleft)

    for trash in falling_trash:
        screen.blit(trash['image'], trash['rect'].topleft)

    # UI
    screen.blit(font.render(f"Lanzamientos: {barrier_uses}/3", True, (0, 0, 150)), (10, 10))
    screen.blit(font.render(f"Basura reciclada: {correct_recyclables}/5", True, (0, 100, 0)), (10, 50))
    screen.blit(font.render(f"Basura no reciclada: {wrong_recyclables}/3", True, (150, 0, 0)), (width // 2 - 100, 10))
    screen.blit(font.render(f"Vidas: {lives}", True, (0, 0, 0)), (width - 120, 10))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()