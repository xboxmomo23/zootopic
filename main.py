import pygame
import random
import sys
import os
import json
import subprocess

# Initialisation de Pygame
pygame.init()
pygame.mixer.init()

# Configuration de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory Zootopie")

clock = pygame.time.Clock()
volume = 0.3

# Charger le volume depuis la config
try:
    with open("config.json", "r") as f:
        config = json.load(f)
        volume = config.get("volume", 0.3)
        pygame.mixer.music.set_volume(volume)
except FileNotFoundError:
    volume = 0.3
    print("Fichier de configuration non trouvé, volume par défaut.")

# Couleurs du jeu
BACKGROUND = (120, 190, 220)
GREEN_SOFT = (140, 210, 170)
GRAY = (170, 170, 170)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 140, 0)
GOLD = (255, 215, 0)
SHADOW = (100, 100, 100)

button_font = pygame.font.SysFont('Comic Sans MS', 24)

# Taille des cartes
CARD_SIZE = 100
MARGIN = 10

# Dictionnaire des effets sonores
sounds = {}
sound_files = {
    'flip': 'sounds/flip.wav',
    'match': 'sounds/match.wav',
    'win': 'sounds/win.wav',
    'lose': 'sounds/lose.wav',
    'click': 'sounds/click.wav'
}

# Charger tous les sons
for sound_name, sound_path in sound_files.items():
    try:
        sounds[sound_name] = pygame.mixer.Sound(sound_path)
    except:
        sounds[sound_name] = None
        print(f"Son {sound_name} non trouvé, continuer sans son")

# Musique de fond
try:
    pygame.mixer.music.load('bransboynd.mp3')
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1)
    print("Musique de fond chargée !")
except:
    print("Musique de fond non trouvée, continuer sans musique")

def play_sound(sound_name):
    # Jouer un son s'il existe
    if sounds.get(sound_name):
        sounds[sound_name].play()

def save_volume():
    # Sauvegarder le volume dans config.json
    with open("config.json", "w") as f:
        json.dump({"volume": volume}, f)

def draw_text(text, font, color, x, y, center=False):
    # Afficher du texte
    surf = font.render(text, True, color)
    if center:
        rect = surf.get_rect(center=(x, y))
        screen.blit(surf, rect)
    else:
        screen.blit(surf, (x, y))

def draw_volume_control(x, y):
    global volume

    # Fond du contrôle de volume
    vol_rect = pygame.Rect(x, y, 230, 35)
    pygame.draw.rect(screen, WHITE, vol_rect, border_radius=15)

    # Texte SON
    draw_text("SON", button_font, BLACK, x + 140, y + 0)

    # Barre de progression
    vol_bar_rect = pygame.Rect(x + 25, y + 10, 100, 10)
    pygame.draw.rect(screen, SHADOW, vol_bar_rect.move(1, 1))
    pygame.draw.rect(screen, BLACK, (x + 25, y + 10, 100 * volume, 10))

    # Curseur
    vol_knob_rect = pygame.Rect(x + 25 + 100 * volume - 5, y + 5, 10, 20)
    pygame.draw.rect(screen, BLACK, vol_knob_rect, border_radius=3)

    # Détecter le clic sur la barre
    mouse_pos = pygame.mouse.get_pos()
    if vol_bar_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
        volume = (mouse_pos[0] - (x + 25)) / 100
        volume = max(0, min(1, volume))
        pygame.mixer.music.set_volume(volume)
        save_volume()

# Charger les images de fond
fonds = {}
bg_files = {
    'menu': 'images/backmenu2.png',
    'game': 'images/background.png',
    'pause': 'images/ZOO2.jpg',
}

for bg_name, bg_path in bg_files.items():
    try:
        bg_img = pygame.image.load(bg_path)
        fonds[bg_name] = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
        print(f"Fond {bg_name} chargé !")
    except:
        fonds[bg_name] = None
        print(f"Fond {bg_name} non trouvé, utiliser fond vert")

# Charger les images des personnages
imgs_persos = [
    pygame.image.load("images/lapin.png"),
    pygame.image.load("images/renard.png"),
    pygame.image.load("images/serpent.png"),
    pygame.image.load("images/paresseux.png"),
    pygame.image.load("images/benjamin.jpg"),
    pygame.image.load("images/bogo.jpg"),
    pygame.image.load("images/kitty.jpg"),
    pygame.image.load("images/gazelle.jpg"),
]

# Redimensionner toutes les cartes
imgs_persos = [
    pygame.transform.scale(img, (CARD_SIZE, CARD_SIZE))
    for img in imgs_persos
]

# Créer le dos de carte
card_back = pygame.Surface((CARD_SIZE, CARD_SIZE))
card_back.fill(GRAY)

# Variables du jeu
levels = [8, 16, 24]
level_names = ["Niveau 1 - Facile", "Niveau 2 - Moyen", "Niveau 3 - L'Attaque !"]
current_level = 0
unlocked_levels = 1

game_state = "menu"

# Variables pour les cartes
cards = []
images = []
card_ids = []
revealed = []
cartes_trouvees = []
errors = 0
temps_debut = 0
MAX_ERRORS = 3

# Variables des phases
phase = "shuffle"
phase_start = 0
wait_time = 0
game_over = False
game_won = False
level_completed = False
base_positions = []

# Classe pour les boutons
class Button:
    def __init__(self, x, y, width, height, text, color=WHITE, text_color=BLACK, font_size=36):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.SysFont(None, font_size)
        self.hovered = False

    def draw(self, surface):
        # Changer de couleur au survol
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

# Classe pour les cartes
class Card:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, CARD_SIZE, CARD_SIZE)

    @property
    def topleft(self):
        return (self.x, self.y)

    @topleft.setter
    def topleft(self, pos):
        self.x, self.y = pos
        self.rect.topleft = pos

def launch_action_game():
    # Lancer le jeu de tir (niveau 3)
    print("\n" + "="*50)
    print("TENTATIVE DE LANCEMENT DU JEU D'ACTION")
    print("="*50)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Répertoire actuel: {current_dir}")
    
    # Chemin vers le jeu de tir
    action_game_path = os.path.join(current_dir, "action", "main.py")
    normalized_path = os.path.normpath(action_game_path)
    
    print(f"Test du chemin: {normalized_path}")
    
    if os.path.exists(normalized_path):
        print(f"✓ JEU D'ACTION TROUVÉ : {normalized_path}")
        
        try:
            print(f"\n→ Lancement du jeu d'action...")
            pygame.mixer.music.stop()
            print("→ Musique arrêtée")
            
            action_dir = os.path.dirname(normalized_path)
            print(f"→ Répertoire du jeu d'action: {action_dir}")
            
            # Lancer le jeu de tir
            print(f"→ Commande: {sys.executable} main.py dans {action_dir}")
            subprocess.Popen([sys.executable, "main.py"], cwd=action_dir)
            print("→ Processus lancé !")
            
            # Fermer le jeu de cartes
            print("→ Fermeture de pygame...")
            pygame.quit()
            print("→ Appel de sys.exit()...")
            sys.exit(0)
            
        except Exception as e:
            print(f"\n✗ ERREUR lors du lancement : {e}")
            import traceback
            traceback.print_exc()
            pygame.init()
            pygame.mixer.init()
            return False
    else:
        print(f"\n✗ FICHIER DU JEU D'ACTION NON TROUVÉ : {normalized_path}")
        print("Vérifiez que le fichier action/main.py existe !")
        return False

def setup_game():
    global cards, images, card_ids, revealed, cartes_trouvees, errors
    global phase, phase_start, temps_debut, game_over, game_won, base_positions
    global MAX_ERRORS, level_completed

    # Définir le nombre d'erreurs selon le niveau
    MAX_ERRORS = 3 if current_level == 0 else 6

    num_cards = levels[current_level]
    num_pairs = num_cards // 2
    
    # Créer les paires d'images
    images_list = imgs_persos[:num_pairs]
    card_ids_list = list(range(num_pairs)) * 2
    
    # Mélanger les cartes
    combined = list(zip(images_list * 2, card_ids_list))
    random.shuffle(combined)
    images_list, card_ids_list = zip(*combined)
    
    images.clear()
    images.extend(images_list)
    card_ids.clear()
    card_ids.extend(card_ids_list)

    # Réinitialiser les variables
    cards.clear()
    revealed.clear()
    cartes_trouvees.clear()
    errors = 0
    game_over = False
    game_won = False
    level_completed = False
    base_positions.clear()

    # Calculer la grille
    rows, cols = (2, 4) if num_cards == 8 else (4, 4) if num_cards == 16 else (4, 6)
    
    grid_width = cols * CARD_SIZE + (cols - 1) * MARGIN
    grid_height = rows * CARD_SIZE + (rows - 1) * MARGIN
    
    start_x = (WIDTH - grid_width) // 2
    start_y = 120
    
    # Créer les cartes
    for i in range(num_cards):
        x = start_x + (i % cols) * (CARD_SIZE + MARGIN)
        y = start_y + (i // cols) * (CARD_SIZE + MARGIN)
        card = Card(x, y)
        cards.append(card)
        base_positions.append((x, y))

    phase = "shuffle"
    phase_start = pygame.time.get_ticks()
    temps_debut = pygame.time.get_ticks()

def draw_background(bg_type):
    # Afficher le fond d'écran
    if fonds.get(bg_type):
        screen.blit(fonds[bg_type], (0, 0))
    else:
        screen.fill(GREEN_SOFT)

def draw_cards(show_all=False):
    # Dessiner toutes les cartes
    for i, card in enumerate(cards):
        if show_all or i in revealed or i in cartes_trouvees:
            screen.blit(images[i], (card.x, card.y))
        else:
            screen.blit(card_back, (card.x, card.y))
        
        pygame.draw.rect(screen, BLACK, (card.x, card.y, CARD_SIZE, CARD_SIZE), 2)

def get_card(pos):
    # Trouver quelle carte a été cliquée
    for i, card in enumerate(cards):
        if card.rect.collidepoint(pos):
            return i
    return None

def draw_menu():
    # Créer les boutons du menu
    menu_buttons = []
    button_y = 250
    
    for i, level_name in enumerate(level_names):
        # Vérifier si le niveau est déverrouillé
        if i < unlocked_levels:
            color = WHITE
            text = level_name
        else:
            color = GRAY
            text = f"{level_name} (verrouillé)"
        
        btn = Button(200, button_y, 400, 50, text, color=color)
        menu_buttons.append(btn)
        button_y += 70
    
    # Bouton quitter
    quit_btn = Button(200, button_y + 20, 400, 50, "Quitter")
    menu_buttons.append(quit_btn)
    
    return menu_buttons

def draw_pause_menu():
    # Créer les boutons du menu pause
    resume_btn = Button(250, 250, 300, 60, "Continuer")
    menu_btn = Button(250, 340, 300, 60, "Menu principal")
    quit_btn = Button(250, 430, 300, 60, "Quitter")
    return [resume_btn, menu_btn, quit_btn]

# Lancer le premier niveau
setup_game()
running = True
menu_buttons = draw_menu()

# Boucle principale du jeu
while running:
    clock.tick(60)
    now = pygame.time.get_ticks()
    mouse_pos = pygame.mouse.get_pos()

    # Menu principal
    if game_state == "menu":
        draw_background('menu')

        # Titre
        title_font = pygame.font.SysFont("Comic Sans MS", 60, bold=True)
        title = title_font.render("MEMORY ZOOTOPIE", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, 120))
        screen.blit(title, title_rect)

        # Afficher les boutons
        for btn in menu_buttons:
            btn.is_hovered(mouse_pos)
            btn.draw(screen)

        # Contrôle du volume
        draw_volume_control(20, HEIGHT - 50)

        # Gérer les clics
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, btn in enumerate(menu_buttons[:-1]):
                    if btn.is_clicked(mouse_pos) and i < unlocked_levels:
                        play_sound('click')
                        current_level = i
                        
                        # Si niveau 3, lancer le jeu d'action
                        if current_level == 2:
                            if not launch_action_game():
                                setup_game()
                                game_state = "game"
                        else:
                            setup_game()
                            game_state = "game"
                        break

                # Bouton quitter
                if menu_buttons[-1].is_clicked(mouse_pos):
                    running = False

    # Phase de jeu
    elif game_state == "game":
        draw_background('game')

        # Titre
        title_font = pygame.font.SysFont("Comic Sans MS", 40, bold=True)
        title_text = title_font.render("Mène ton enquête", True, BLACK)
        title_rect = title_text.get_rect(center=(WIDTH//2, 50))
        screen.blit(title_text, title_rect)

        # Bouton pause
        pause_btn = Button(WIDTH - 100, 10, 80, 35, "⏸ Menu", font_size=24)
        pause_btn.is_hovered(mouse_pos)
        pause_btn.draw(screen)

        # Phase de mélange
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

        # Phase de visualisation
        elif phase == "show":
            draw_cards(show_all=True)
            if now - phase_start > 4000:
                phase = "play"
                phase_start = now
                temps_debut = now

        # Phase de jeu
        elif phase == "play":
            draw_cards()
            if len(revealed) == 2 and not game_over and not game_won:
                if now - wait_time > 700:
                    a, b = revealed
                    if card_ids[a] == card_ids[b]:
                        cartes_trouvees.extend([a, b])
                        play_sound('match')
                    else:
                        errors += 1
                        if errors > MAX_ERRORS:
                            game_over = True
                            play_sound('lose')
                    revealed.clear()

        draw_cards(show_all=(phase == "show" or phase == "shuffle"))

        # Afficher le temps et les erreurs
        elapsed = (now - temps_debut) // 1000
        if game_over or game_won:
            elapsed = (phase_start - temps_debut) // 1000
        font = pygame.font.SysFont("Comic Sans MS", 30, bold=True)
        timer_text = font.render(f"Temps : {elapsed} s", True, BLACK)
        screen.blit(timer_text, (10, 10))
        error_text = font.render(f"Erreurs : {errors}/{MAX_ERRORS}", True, BLACK)
        screen.blit(error_text, (WIDTH - 200, 55))

        # Boutons de fin de niveau
        button = None
        all_found = len(cartes_trouvees) == len(cards)
        msg = None

        # Victoire
        if all_found and not game_over:
            if not level_completed:
                game_won = True
                level_completed = True
                phase_start = now
                play_sound('win')

                # Débloquer le niveau suivant
                if current_level + 1 >= unlocked_levels:
                    unlocked_levels = min(current_level + 2, len(levels))

            # Texte du bouton selon le niveau
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

        # Afficher le bouton
        if button:
            button.is_hovered(mouse_pos)
            button.draw(screen)

        # Gérer les événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                # Clic sur pause
                if pause_btn.is_clicked(pos):
                    play_sound('click')
                    game_state = "pause"
                    pause_buttons = draw_pause_menu()

                # Clic sur bouton de fin
                elif button is not None and button.is_clicked(pos):
                    play_sound('click')
                    if game_over:
                        setup_game()
                    elif game_won:
                        # Niveau 2 terminé = lancer le jeu d'action
                        if current_level == 1:
                            print("Lancement du jeu d'action après victoire niveau 2...")
                            launch_action_game()
                            print("Échec du lancement, continuation normale...")
                            current_level += 1
                            setup_game()
                        elif current_level < len(levels) - 1:
                            current_level += 1
                            setup_game()
                        else:
                            game_state = "menu"
                            menu_buttons = draw_menu()

                # Clic sur une carte
                elif phase == "play" and not game_over and not game_won:
                    clicked = get_card(pos)
                    if clicked is not None and clicked not in revealed and clicked not in cartes_trouvees and len(revealed) < 2:
                        revealed.append(clicked)
                        play_sound('flip')
                        if len(revealed) == 2:
                            wait_time = now

    # Menu pause
    elif game_state == "pause":
        # Redessiner le jeu en arrière-plan
        draw_background('game')
        
        title_font = pygame.font.SysFont("Comic Sans MS", 40, bold=True)
        title_text = title_font.render("Mène ton enquête", True, BLACK)
        title_rect = title_text.get_rect(center=(WIDTH//2, 50))
        screen.blit(title_text, title_rect)

        draw_cards(show_all=(phase == "show" or phase == "shuffle"))
        
        # Afficher le temps et les erreurs
        elapsed = (now - temps_debut) // 1000
        if game_over or game_won:
            elapsed = (phase_start - temps_debut) // 1000
        font = pygame.font.SysFont("Comic Sans MS", 30, bold=True)
        timer_text = font.render(f"Temps : {elapsed} s", True, BLACK)
        screen.blit(timer_text, (10, 10))
        error_text = font.render(f"Erreurs : {errors}/{MAX_ERRORS}", True, BLACK)
        screen.blit(error_text, (WIDTH - 200, 55))
        
        # Overlay sombre
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        # Titre PAUSE
        title_font = pygame.font.SysFont("Comic Sans MS", 60, bold=True)
        title = title_font.render("PAUSE", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, 150))
        screen.blit(title, title_rect)

        # Boutons
        resume_btn = Button(250, 250, 300, 60, "Continuer")
        menu_btn = Button(250, 340, 300, 60, "Menu principal")
        quit_btn = Button(250, 430, 300, 60, "Quitter")

        pause_buttons = [resume_btn, menu_btn, quit_btn]

        # Afficher les boutons
        for btn in pause_buttons:
            btn.is_hovered(mouse_pos)
            btn.draw(screen)

        # Contrôle du volume
        draw_volume_control(20, HEIGHT - 50)

        # Gérer les clics
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pause_buttons[0].is_clicked(mouse_pos):
                    play_sound('click')
                    game_state = "game"
                elif pause_buttons[1].is_clicked(mouse_pos):
                    play_sound('click')
                    game_state = "menu"
                    menu_buttons = draw_menu()
                elif pause_buttons[2].is_clicked(mouse_pos):
                    running = False

    pygame.display.flip()

pygame.quit()
sys.exit()