import pygame
import random
import sys
import os

pygame.init()
pygame.mixer.init()

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
ORANGE = (255, 140, 0)
GOLD = (255, 215, 0)

CARD_SIZE = 100
MARGIN = 10

# ----- CHARGEMENT DES SONS -----
# Création de sons simples si les fichiers n'existent pas
sounds = {}
sound_files = {
    'flip': 'sounds/flip.wav',
    'match': 'sounds/match.wav',
    'win': 'sounds/win.wav',
    'lose': 'sounds/lose.wav',
    'click': 'sounds/click.wav'
}

# Charger les sons s'ils existent, sinon None
for sound_name, sound_path in sound_files.items():
    try:
        sounds[sound_name] = pygame.mixer.Sound(sound_path)
    except:
        sounds[sound_name] = None
        print(f"Son {sound_name} non trouvé, continuer sans son")

def play_sound(sound_name):
    """Joue un son si disponible"""
    if sounds.get(sound_name):
        sounds[sound_name].play()

# ----- CHARGEMENT DES IMAGES -----
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

# ----- VARIABLES GLOBALES -----
levels = [8, 16, 24]  # facile, moyen, difficile (bonus)
level_names = ["Niveau 1 - Facile", "Niveau 2 - Moyen", "Niveau 3 - L'Attaque !"]
current_level = 0
unlocked_levels = 1  # Nombre de niveaux déverrouillés (commence à 1)

game_state = "menu"  # États: "menu", "game", "pause"

cards = []
images = []
card_ids = []
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

# ----- CLASSES POUR LES BOUTONS -----
class Button:
    def __init__(self, x, y, width, height, text, color=WHITE, text_color=BLACK, font_size=36):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.SysFont(None, font_size)
        self.hovered = False
    
    def draw(self, surface):
        # Effet hover
        color = self.color if not self.hovered else GOLD
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 3)
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def is_hovered(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# ----- FONCTIONS -----
def setup_game():
    global cards, images, card_ids, revealed, matched, errors
    global phase, phase_start, start_time, game_over, game_won, base_positions
    global MAX_ERRORS, level_completed

    # Définir erreurs max selon niveau
    if current_level == 0:
        MAX_ERRORS = 3
    elif current_level == 1:
        MAX_ERRORS = 6
    else:
        MAX_ERRORS = 10  # Niveau bonus plus difficile

    num_cards = levels[current_level]
    num_pairs = num_cards // 2
    
    # Limiter au nombre d'images disponibles
    num_pairs = min(num_pairs, len(card_images_base))
    num_cards = num_pairs * 2
    
    # Créer une liste d'IDs pour identifier les paires
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

    # Grille automatique selon le nombre de cartes
    if num_cards == 8:
        rows, cols = 2, 4
    elif num_cards == 16:
        rows, cols = 4, 4
    else:
        rows, cols = 4, 6  # Pour le niveau bonus

    # Calculer la largeur et hauteur totale de la grille
    grid_width = cols * CARD_SIZE + (cols - 1) * MARGIN
    grid_height = rows * CARD_SIZE + (rows - 1) * MARGIN
    
    # Centrer la grille
    start_x = (WIDTH - grid_width) // 2
    available_height = HEIGHT - 120
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
    pygame.draw.rect(screen, GREEN_SOFT, (0, 0, WIDTH, HEIGHT))

def draw_cards(show_all=False):
    for i, rect in enumerate(cards):
        # Si la carte doit être montrée, afficher l'image
        if show_all or i in revealed or i in matched:
            screen.blit(images[i], rect)
        else:
            screen.blit(card_back, rect)
        
        # Bordure noire
        pygame.draw.rect(screen, BLACK, rect, 2)

def get_card(pos):
    for i, rect in enumerate(cards):
        if rect.collidepoint(pos):
            return i
    return None

def draw_menu():
    """Affiche le menu principal"""
    draw_background()
    
    # Titre
    title_font = pygame.font.SysFont(None, 80, bold=True)
    title_text = title_font.render("Memory Zootopie", True, BLACK)
    title_rect = title_text.get_rect(center=(WIDTH//2, 80))
    screen.blit(title_text, title_rect)
    
    # Sous-titre
    subtitle_font = pygame.font.SysFont(None, 40)
    subtitle = subtitle_font.render("Mène ton enquête !", True, BLACK)
    subtitle_rect = subtitle.get_rect(center=(WIDTH//2, 140))
    screen.blit(subtitle, subtitle_rect)
    
    # Boutons de sélection de niveau
    buttons = []
    for i in range(len(levels)):
        y_pos = 220 + i * 90
        
        # Vérifier si le niveau est déverrouillé
        if i < unlocked_levels:
            btn = Button(250, y_pos, 300, 60, level_names[i])
        else:
            btn = Button(250, y_pos, 300, 60, "🔒 " + level_names[i], color=GRAY)
        
        buttons.append(btn)
    
    # Bouton quitter
    quit_btn = Button(250, 500, 300, 50, "Quitter", font_size=32)
    buttons.append(quit_btn)
    
    return buttons

def draw_pause_menu():
    """Affiche le menu pause"""
    # Fond semi-transparent
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    # Titre
    title_font = pygame.font.SysFont(None, 70, bold=True)
    title = title_font.render("PAUSE", True, WHITE)
    title_rect = title.get_rect(center=(WIDTH//2, 150))
    screen.blit(title, title_rect)
    
    # Boutons
    resume_btn = Button(250, 250, 300, 60, "Continuer")
    menu_btn = Button(250, 340, 300, 60, "Menu principal")
    quit_btn = Button(250, 430, 300, 60, "Quitter")
    
    return [resume_btn, menu_btn, quit_btn]

# ----- INITIALISATION -----
running = True
menu_buttons = draw_menu()
pause_buttons = []

while running:
    clock.tick(60)
    now = pygame.time.get_ticks()
    mouse_pos = pygame.mouse.get_pos()
    
    # ========== MENU PRINCIPAL ==========
    if game_state == "menu":
        draw_background()
        
        # Titre
        title_font = pygame.font.SysFont(None, 80, bold=True)
        title_text = title_font.render("Memory Zootopie", True, BLACK)
        title_rect = title_text.get_rect(center=(WIDTH//2, 80))
        screen.blit(title_text, title_rect)
        
        # Sous-titre
        subtitle_font = pygame.font.SysFont(None, 40)
        subtitle = subtitle_font.render("Mène ton enquête !", True, BLACK)
        subtitle_rect = subtitle.get_rect(center=(WIDTH//2, 140))
        screen.blit(subtitle, subtitle_rect)
        
        # Dessiner les boutons
        for btn in menu_buttons:
            btn.is_hovered(mouse_pos)
            btn.draw(screen)
        
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Vérifier quel bouton est cliqué
                for i, btn in enumerate(menu_buttons[:-1]):  # Tous sauf "Quitter"
                    if btn.is_clicked(mouse_pos) and i < unlocked_levels:
                        play_sound('click')
                        current_level = i
                        setup_game()
                        game_state = "game"
                        break
                
                # Bouton Quitter
                if menu_buttons[-1].is_clicked(mouse_pos):
                    running = False
    
    # ========== JEU ==========
    elif game_state == "game":
        draw_background()
        
        # ---- TITRE ----
        title_font = pygame.font.SysFont(None, 60, bold=True)
        title_text = title_font.render("Mène ton enquête", True, BLACK)
        title_rect = title_text.get_rect(center=(WIDTH//2, 50))
        screen.blit(title_text, title_rect)
        
        # Bouton pause (petit)
        pause_btn = Button(WIDTH - 100, 10, 80, 35, "⏸ Menu", font_size=24)
        pause_btn.is_hovered(mouse_pos)
        pause_btn.draw(screen)
        
        # ---- PHASES ----
        if phase == "shuffle":
            for i in range(len(cards)):
                offset_x = random.randint(-5, 5)
                offset_y = random.randint(-5, 5)
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
            if len(revealed) == 2 and not game_over and not game_won:
                if now - wait_time > 700:
                    a, b = revealed
                    if card_ids[a] == card_ids[b]:
                        matched.extend([a, b])
                        play_sound('match')
                    else:
                        errors += 1
                        if errors > MAX_ERRORS:
                            game_over = True
                            play_sound('lose')
                    revealed.clear()

        draw_cards(show_all=(phase == "show" or phase == "shuffle"))

        # ---- TIMER ET ERREURS ----
        elapsed = (now - start_time) // 1000
        if game_over or game_won:
            elapsed = (phase_start - start_time) // 1000
        font = pygame.font.SysFont(None, 36)
        timer_text = font.render(f"Temps : {elapsed} s", True, BLACK)
        screen.blit(timer_text, (10, 10))
        error_text = font.render(f"Erreurs : {errors}/{MAX_ERRORS}", True, BLACK)
        screen.blit(error_text, (WIDTH - 200, 55))

        # ---- BOUTON FIN DE NIVEAU ET MESSAGE ----
        button = None
        all_found = len(matched) == len(cards)
        msg = None

        # Victoire
        if all_found and not game_over:
            if not level_completed:
                game_won = True
                level_completed = True
                phase_start = now
                play_sound('win')
                
                # Déverrouiller le niveau suivant
                if current_level + 1 >= unlocked_levels:
                    unlocked_levels = min(current_level + 2, len(levels))
            
            # Choisir le label du bouton selon le niveau
            if current_level == 0:
                label = "Niveau suivant"
            elif current_level == 1:
                label = "Passons à l'attaque !"
            else:
                label = "Menu principal"
            
            button = Button(250, 520, 300, 60, label)
            msg = font.render("Tu as gagné !", True, BLACK)

        # Défaite
        if game_over and not game_won:
            button = Button(250, 520, 300, 60, "Recommencer")
            msg = font.render("Tu as perdu !", True, BLACK)

        # Afficher le message
        if msg:
            msg_rect = msg.get_rect(center=(WIDTH//2, 90))
            screen.blit(msg, msg_rect)
        
        # Dessiner le bouton de fin
        if button:
            button.is_hovered(mouse_pos)
            button.draw(screen)

        # ---- ÉVÉNEMENTS ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                
                # Clic sur bouton pause
                if pause_btn.is_clicked(pos):
                    play_sound('click')
                    game_state = "pause"
                    pause_buttons = draw_pause_menu()
                
                # Clic bouton de fin
                elif button is not None and button.is_clicked(pos):
                    play_sound('click')
                    if game_over:
                        setup_game()
                    elif game_won:
                        if current_level < len(levels) - 1:
                            current_level += 1
                            setup_game()
                        else:
                            # Retour au menu après le dernier niveau
                            game_state = "menu"
                            menu_buttons = draw_menu()
                
                # Clic cartes uniquement en phase play
                elif phase == "play" and not game_over and not game_won:
                    clicked = get_card(pos)
                    if clicked is not None and clicked not in revealed and clicked not in matched and len(revealed) < 2:
                        revealed.append(clicked)
                        play_sound('flip')
                        if len(revealed) == 2:
                            wait_time = now
    
    # ========== MENU PAUSE ==========
    elif game_state == "pause":
        # Fond semi-transparent
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Titre
        title_font = pygame.font.SysFont(None, 70, bold=True)
        title = title_font.render("PAUSE", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, 150))
        screen.blit(title, title_rect)
        
        # Boutons
        resume_btn = Button(250, 250, 300, 60, "Continuer")
        menu_btn = Button(250, 340, 300, 60, "Menu principal")
        quit_btn = Button(250, 430, 300, 60, "Quitter")
        
        pause_buttons = [resume_btn, menu_btn, quit_btn]
        
        # Dessiner les boutons
        for btn in pause_buttons:
            btn.is_hovered(mouse_pos)
            btn.draw(screen)
        
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pause_buttons[0].is_clicked(mouse_pos):  # Continuer
                    play_sound('click')
                    game_state = "game"
                elif pause_buttons[1].is_clicked(mouse_pos):  # Menu
                    play_sound('click')
                    game_state = "menu"
                    menu_buttons = draw_menu()
                elif pause_buttons[2].is_clicked(mouse_pos):  # Quitter
                    running = False
    
    pygame.display.flip()

pygame.quit()
sys.exit()