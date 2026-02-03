import pygame
import random
import sys

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

card_colors = [
    (255, 100, 100),
    (100, 255, 100),
    (100, 100, 255),
    (255, 255, 100),
    (255, 150, 50),
    (180, 100, 200),
    (100, 255, 255),
    (255, 120, 180)
]

# ----- VARIABLES -----
levels = [8, 16]  # facile puis moyen
current_level = 0

cards = []
colors = []
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
base_positions = []

# ----- FONCTIONS -----
def setup_game():
    global cards, colors, revealed, matched, errors
    global phase, phase_start, start_time, game_over, game_won, base_positions
    global MAX_ERRORS

    # Définir erreurs max selon niveau
    MAX_ERRORS = 3 if current_level == 0 else 6

    num_cards = levels[current_level]
    num_pairs = num_cards // 2
    colors_list = card_colors[:num_pairs] * 2
    random.shuffle(colors_list)
    colors.clear()
    colors.extend(colors_list)

    cards.clear()
    revealed.clear()
    matched.clear()
    errors = 0
    game_over = False
    game_won = False
    base_positions.clear()

    # grille automatique
    rows, cols = (2, 4) if num_cards == 8 else (4, 4)

    for i in range(num_cards):
        x = (i % cols) * (CARD_SIZE + MARGIN) + MARGIN
        y = (i // cols) * (CARD_SIZE + MARGIN) + START_Y
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
        color = colors[i] if show_all or i in revealed or i in matched else GRAY
        pygame.draw.rect(screen, color, rect)
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
        if len(revealed) == 2 and not game_over:
            if now - wait_time > 700:
                a, b = revealed
                if colors[a] == colors[b]:
                    matched.extend([a,b])
                else:
                    errors +=1
                    if errors > MAX_ERRORS:
                        game_over = True
                revealed = []

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

    if all_found:
        game_won = True
        phase_start = phase_start or now
        button = pygame.Rect(150,600,300,60)
        pygame.draw.rect(screen, WHITE, button)
        pygame.draw.rect(screen, BLACK, button, 2)
        label = "Niveau suivant" if current_level < len(levels)-1 else "Recommencer"
        screen.blit(font.render(label, True, BLACK),(button.x+40, button.y+15))
        msg = font.render("Tu as gagné !", True, BLACK)

    if game_over and not game_won:
        button = pygame.Rect(150,600,300,60)
        pygame.draw.rect(screen, WHITE, button)
        pygame.draw.rect(screen, BLACK, button, 2)
        screen.blit(font.render("Recommencer", True, BLACK),(button.x+40, button.y+15))
        msg = font.render("Tu as perdu !", True, BLACK)

    if msg:
        screen.blit(msg, (WIDTH//2 - 100, HEIGHT - 50))

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
                if clicked is not None and clicked not in revealed and clicked not in matched:
                    revealed.append(clicked)
                    if len(revealed)==2:
                        wait_time = now
