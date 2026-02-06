import pygame
import sys
import math
import os
import subprocess
import json

def save_volume():
    with open("config.json", "w") as f:
        json.dump({"volume": volume}, f)

# Initialisation de Pygame pour le son
pygame.init()
pygame.mixer.init()

# Constante
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (15, 15, 25)
GREEN = (80, 200, 120)
RED = (220, 80, 80)
LIGHT_GREEN = (120, 240, 160)
LIGHT_RED = (255, 120, 120)
SHADOW = (10, 10, 10)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Menu Start")
clock = pygame.time.Clock()

# Variable globale pour le volume
volume = 1

# Image de fond
image_path = "ZOO2.jpg"
try:
    if os.path.exists(image_path):
        background = pygame.image.load(image_path).convert()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    else:
        print("Image de fond introuvable. Utilisation d'un fond noir.")
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill(BLACK)
except Exception as e:
    print(f"Erreur chargement image: {e}. Utilisation d'un fond noir.")
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(BLACK)

# Chargement et lecture de la musique
try:
    pygame.mixer.music.load("MUSICNUL.mp3")
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1)  # Lecture en boucle
except Exception as e:
    print(f"Erreur chargement musique: {e}. Pas de musique.")

overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
overlay.fill((0, 0, 0, 110))

# Police
title_font = pygame.font.SysFont('Comic Sans MS', 70, bold=True)
button_font = pygame.font.SysFont('Comic Sans MS', 40)

def draw_text(text, font, color, x, y, shadow=False):
    if shadow:
        shadow_surface = font.render(text, True, SHADOW)
        shadow_rect = shadow_surface.get_rect(center=(x+3, y+3))
        screen.blit(shadow_surface, shadow_rect)

    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def draw_button(rect, base_color, hover_color, text):
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos)

    pygame.draw.rect(screen, SHADOW, rect.move(5, 5), border_radius=12)
    color = hover_color if is_hovered else base_color
    pygame.draw.rect(screen, color, rect, border_radius=12)

    draw_text(text, button_font, BLACK, rect.centerx, rect.centery)
    return is_hovered

def draw_volume_control():
    global volume

    # Rectangle de fond pour le volume
    vol_rect = pygame.Rect(20, HEIGHT - 40, 230, 35)
    pygame.draw.rect(screen, WHITE, vol_rect, border_radius=15)

    # Texte dans la barre de volume son
    draw_text("                 SON", button_font, BLACK, 95, HEIGHT - 25)

    # Barre de volume
    vol_bar_rect = pygame.Rect(25, HEIGHT - 30, 100, 10)
    pygame.draw.rect(screen, SHADOW, vol_bar_rect.move(1, 1))
    pygame.draw.rect(screen, BLACK, (25, HEIGHT - 30, 100 * volume, 10))

    # Bouton de réglage du son
    vol_knob_rect = pygame.Rect(25 + 100 * volume - 5, HEIGHT - 35, 10, 20)
    pygame.draw.rect(screen, BLACK, vol_knob_rect, border_radius=3)

    # Gestion du clic sur la barre de volume
    mouse_pos = pygame.mouse.get_pos()
    if vol_bar_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
        volume = (mouse_pos[0] - 25) / 100
        volume = max(0, min(1, volume))  # Limite entre 0 et 1
        pygame.mixer.music.set_volume(volume)

def start_game():
    global volume
    print("Lancement de main.py...")
    pygame.mixer.music.stop()
    subprocess.run(["python", "main.py"])
    pygame.quit()
    sys.exit()
def main_menu():
    global volume
    pulse = 0
    zoom = 1.0

    while True:
        clock.tick(FPS)
        pulse += 0.03
        zoom += 0.0003
        if zoom > 1.01:
            zoom = 1.0

        # Affichage du fond
        bg_width = int(WIDTH * zoom)
        bg_height = int(HEIGHT * zoom)
        scaled_bg = pygame.transform.scale(background, (bg_width, bg_height))
        screen.blit(scaled_bg, ((WIDTH - bg_width) // 2, (HEIGHT - bg_height) // 2))
        screen.blit(overlay, (0, 0))

        # Titre
        title_y = HEIGHT // 4 + int(8 * math.sin(pulse))
        draw_text("MENU PRINCIPAL", title_font, WHITE, WIDTH // 2, title_y, shadow=True)

        # Boutons
        play_button = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 - 40, 240, 60)
        quit_button = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 60, 240, 60)

        play_hover = draw_button(play_button, GREEN, LIGHT_GREEN, "JOUER")
        quit_hover = draw_button(quit_button, RED, LIGHT_RED, "QUITTER")

        # Contrôle du volume
        draw_volume_control()

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_hover:
                    start_game()
                if quit_hover:
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()

main_menu()
