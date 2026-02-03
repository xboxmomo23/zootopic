import pygame
import random
import sys
import os

pygame.init()

# ----- FENÊTRE -----
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory Zootopie")

clock = pygame.time.Clock()

# ----- COULEURS -----
BACKGROUND = (120, 190, 220)
GREEN_SOFT = (140, 210, 170)
GRAY = (170, 170, 170)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

CARD_SIZE = 100
MARGIN = 10
START_Y = 120  # décalage pour laisser de la place au titre

# ----- CHARGEMENT DES IMAGES -----
# Charger tes vraies images de personnages Zootopie
card_images_base = [
    pygame.image.load("images/lapin.png"),
    pygame.image.load("images/renard.png"),
    pygame.image.load("images/serpent.png"),
    pygame.image.load("images/paresseux.png"),
    pygame.image.load("images/benjamin.jpg"),
    pygame.image.load("images/bogo.jpg"),
    pygame.image.load("images/kitty.jpg"),
    pygame.image.load("images/gazelle.jpg"),

]

# Redimensionner toutes les images à la taille des cartes
card_images_base = [
    pygame.transform.scale(img, (CARD_SIZE, CARD_SIZE))
    for img in card_images_base
]

# Image pour le dos de la carte (gris)
card_back = pygame.Surface((CARD_SIZE, CARD_SIZE))
card_back.fill(GRAY)

# ----- VARIABLES -----
levels = [8, 16]  # facile puis moyen
current_level = 0

cards = []
images = []  # Contient les images mélangées pour cette partie
card_ids = []  # 🔧 NOUVEAU : Contient les IDs des cartes pour la comparaison
revealed = []
matched = []
errors = 0
start_time = 0
MAX_ERRORS = 3

phase = "shuffle"
phase_start = 0
wait_time = 0
game_over = False
game_won = False
level_completed = False
base_positions = []

# ----- FONCTIONS -----
def setup_game():
    global cards, images, card_ids, revealed, matched, errors
    global phase, phase_start, start_time, game_over, game_won, base_positions
    global MAX_ERRORS, level_completed

    # Définir erreurs max selon niveau
    MAX_ERRORS = 3 if current_level == 0 else 6

    num_cards = levels[current_level]
    num_pairs = num_cards // 2
    
    # 🔧 CORRECTION : Limiter au nombre d'images disponibles
    num_pairs = min(num_pairs, len(card_images_base))
    num_cards = num_pairs * 2
    
    # 🔧 NOUVEAU : Créer une liste d'IDs pour identifier les paires
    # Chaque paire a le même ID (0, 0, 1, 1, 2, 2, 3, 3, etc.)
    ids_list = list(range(num_pairs)) * 2
    random.shuffle(ids_list)
    
    card_ids.clear()
    card_ids.extend(ids_list)
    
    # Créer la liste d'images correspondante
    images_list = [card_images_base[id] for id in ids_list]
    
    images.clear()
    images.extend(images_list)

    cards.clear()
    revealed.clear()
    matched.clear()
    errors = 0
    game_over = False
    game_won = False
    level_completed = False
    base_positions.clear()

    # grille automatique
    rows, cols = (2, 4) if num_cards == 8 else (4, 4)

    # Calculer la largeur et hauteur totale de la grille
    grid_width = cols * CARD_SIZE + (cols - 1) * MARGIN
    grid_height = rows * CARD_SIZE + (rows - 1) * MARGIN
    
    # Centrer la grille horizontalement et verticalement (avec espace pour le titre)
    start_x = (WIDTH - grid_width) // 2
    # Calculer l'espace disponible sous le titre (titre à y=50, hauteur ~60px)
    available_height = HEIGHT - 120  # Espace sous le titre
    start_y = 120 + (available_height - grid_height) // 2
    
    for i in range(num_cards):
        x = start_x + (i % cols) * (CARD_SIZE + MARGIN)
        y = start_y + (i // cols) * (CARD_SIZE + MARGIN)
        rect = pygame.Rect(x, y, CARD_SIZE, CARD_SIZE)
        cards.append(rect)
        base_positions.append((x, y))

    phase = "shuffle"
    phase_start = pygame.time.get_ticks()
    start_time = pygame.time.get_ticks()

def draw_background():
    screen.fill(BACKGROUND)
    pygame.draw.rect(screen, GREEN_SOFT, (0,0,WIDTH,HEIGHT))

def draw_cards(show_all=False):
    for i, rect in enumerate(cards):
        # Si la carte doit être montrée, afficher l'image, sinon le dos gris
        if show_all or i in revealed or i in matched:
            screen.blit(images[i], rect)
        else:
            screen.blit(card_back, rect)
        
        # Bordure noire autour de chaque carte
        pygame.draw.rect(screen, BLACK, rect, 2)

def get_card(pos):
    for i, rect in enumerate(cards):
        if rect.collidepoint(pos):
            return i
    return None

# ----- INITIALISATION -----
setup_game()
running = True
button = None

while running:
    clock.tick(60)
    now = pygame.time.get_ticks()
    draw_background()

    # ---- TITRE ----
    title_font = pygame.font.SysFont(None, 60, bold=True)
    title_text = title_font.render("Mène ton enquête", True, BLACK)
    title_rect = title_text.get_rect(center=(WIDTH//2, 50))
    screen.blit(title_text, title_rect)

    # ---- PHASES ----
    if phase == "shuffle":
        for i in range(len(cards)):
            offset_x = random.randint(-5,5)
            offset_y = random.randint(-5,5)
            cards[i].x = base_positions[i][0] + offset_x
            cards[i].y = base_positions[i][1] + offset_y
        if now - phase_start > 1000:
            for i in range(len(cards)):
                cards[i].topleft = base_positions[i]
            phase = "show"
            phase_start = now

    elif phase == "show":
        draw_cards(show_all=True)
        if now - phase_start > 4000:
            phase = "play"
            phase_start = now
            start_time = now

    elif phase == "play":
        draw_cards()
        # 🔧 CORRECTION : Vérifier les paires après un délai
        if len(revealed) == 2 and not game_over and not game_won:
            if now - wait_time > 700:
                a, b = revealed
                # 🔧 CORRECTION : Comparer les IDs au lieu des objets Surface
                if card_ids[a] == card_ids[b]:
                    matched.extend([a, b])
                else:
                    errors += 1
                    if errors > MAX_ERRORS:
                        game_over = True
                # 🔧 CORRECTION : Toujours vider revealed après vérification
                revealed.clear()

    draw_cards(show_all=(phase=="show" or phase=="shuffle"))

    # ---- TIMER ET ERREURS ----
    elapsed = (now - start_time)//1000
    if game_over or game_won:
        elapsed = (phase_start - start_time)//1000
    font = pygame.font.SysFont(None,36)
    timer_text = font.render(f"Temps : {elapsed} s", True, BLACK)
    screen.blit(timer_text, (10, 10))
    error_text = font.render(f"Erreurs : {errors}/{MAX_ERRORS}", True, BLACK)
    screen.blit(error_text, (WIDTH-200, 10))

    # ---- BOUTON FIN DE NIVEAU ET MESSAGE ----
    button = None
    all_found = len(matched) == len(cards)
    msg = None

    # Si toutes les paires sont trouvées et qu'on n'a pas perdu
    if all_found and not game_over:
        if not level_completed:
            game_won = True
            level_completed = True
            phase_start = now
        
        button = pygame.Rect(250,500,300,60)
        pygame.draw.rect(screen, WHITE, button)
        pygame.draw.rect(screen, BLACK, button, 2)
        label = "Niveau suivant" if current_level < len(levels)-1 else "Recommencer"
        screen.blit(font.render(label, True, BLACK),(button.x+40, button.y+15))
        msg = font.render("Tu as gagné !", True, BLACK)

    if game_over and not game_won:
        button = pygame.Rect(250,500,300,60)
        pygame.draw.rect(screen, WHITE, button)
        pygame.draw.rect(screen, BLACK, button, 2)
        screen.blit(font.render("Recommencer", True, BLACK),(button.x+80, button.y+15))
        msg = font.render("Tu as perdu !", True, BLACK)

    if msg:
        screen.blit(msg, (WIDTH//2 - 100, 450))

    pygame.display.flip()

    # ---- ÉVÉNEMENTS ----
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type==pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            # clic bouton
            if button is not None and button.collidepoint(pos):
                if game_over:
                    setup_game()
                elif game_won:
                    if current_level < len(levels)-1:
                        current_level += 1
                    setup_game()
            # clic cartes uniquement phase play et partie en cours
            elif phase=="play" and not game_over and not game_won:
                clicked = get_card(pos)
                # 🔧 CORRECTION : Autoriser seulement 2 cartes max révélées
                if clicked is not None and clicked not in revealed and clicked not in matched and len(revealed) < 2:
                    revealed.append(clicked)
                    if len(revealed)==2:
                        wait_time = now