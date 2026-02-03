import pygame
import random
import sys

pygame.init()

# ----- FENÊTRE -----
WIDTH, HEIGHT = 600, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory Zootopie")

clock = pygame.time.Clock()

# ----- COULEURS (style Zootopie) -----
BACKGROUND = (120, 190, 220)   # bleu ciel
GREEN_SOFT = (140, 210, 170)
GRAY = (170, 170, 170)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ----- GRILLE -----
ROWS, COLS = 4, 4
CARD_SIZE = 100
MARGIN = 10
START_Y = 50

# ----- COULEURS DES CARTES (paires) -----
card_colors = [
    (255, 100, 100),
    (100, 255, 100),
    (100, 100, 255),
    (255, 255, 100),
    (255, 150, 50),
    (180, 100, 200),
    (100, 255, 255),
    (255, 120, 180)
] * 2

MAX_ERRORS = 3  # nombre d'erreurs autorisées

# ----- FONCTIONS -----

def setup_game():
    global colors, cards, revealed, matched, errors, start_time, show_start

    colors = card_colors.copy()
    random.shuffle(colors)

    cards = []
    revealed = []
    matched = []
    errors = 0

    for i in range(16):
        x = (i % COLS) * (CARD_SIZE + MARGIN) + MARGIN
        y = (i // COLS) * (CARD_SIZE + MARGIN) + START_Y
        rect = pygame.Rect(x, y, CARD_SIZE, CARD_SIZE)
        cards.append(rect)

    start_time = pygame.time.get_ticks()
    show_start = True  # toutes les cartes visibles pendant 2 secondes au début


def draw_background():
    screen.fill(BACKGROUND)
    pygame.draw.rect(screen, GREEN_SOFT, (0, 0, WIDTH, HEIGHT))


def draw_cards():
    for i, rect in enumerate(cards):
        if show_start or i in revealed or i in matched:
            pygame.draw.rect(screen, colors[i], rect)
        else:
            pygame.draw.rect(screen, GRAY, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)


def get_card(pos):
    for i, rect in enumerate(cards):
        if rect.collidepoint(pos):
            return i
    return None


def draw_button(text, y_pos):
    button_rect = pygame.Rect(150, y_pos, 300, 60)
    pygame.draw.rect(screen, WHITE, button_rect)
    pygame.draw.rect(screen, BLACK, button_rect, 2)
    font = pygame.font.SysFont(None, 40)
    label = font.render(text, True, BLACK)
    screen.blit(label, (button_rect.x + 40, button_rect.y + 15))
    return button_rect


def draw_timer():
    elapsed = (pygame.time.get_ticks() - start_time) // 1000
    font = pygame.font.SysFont(None, 36)
    timer_text = font.render(f"Temps : {elapsed} s", True, BLACK)
    screen.blit(timer_text, (10, 10))


def draw_errors():
    font = pygame.font.SysFont(None, 36)
    error_text = font.render(f"Erreurs : {errors}/{MAX_ERRORS}", True, BLACK)
    screen.blit(error_text, (WIDTH - 200, 10))


# ----- INITIALISATION -----
setup_game()
wait_time = 0
game_over = False
game_won = False

# ----- BOUCLE DU JEU -----
running = True
while running:
    clock.tick(60)
    draw_background()
    draw_cards()
    draw_timer()
    draw_errors()

    all_found = len(matched) == 16

    if all_found:
        game_won = True
        button = draw_button("Recommencer", 600)

    if game_over and not game_won:
        button = draw_button("Recommencer", 600)

    pygame.display.flip()

    # ---- ÉVÉNEMENTS ----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if (all_found or game_over) and button.collidepoint(event.pos):
                setup_game()
                game_over = False
                game_won = False

            elif not all_found and not game_over and not show_start:
                if len(revealed) < 2:
                    clicked = get_card(event.pos)
                    if clicked is not None and clicked not in revealed and clicked not in matched:
                        revealed.append(clicked)

                        if len(revealed) == 2:
                            wait_time = pygame.time.get_ticks()

    # ---- LOGIQUE ----
    if show_start:
        if pygame.time.get_ticks() - start_time > 2000:
            show_start = False
            start_time = pygame.time.get_ticks()  # reset timer après la phase de visibilité

    if len(revealed) == 2 and not show_start:
        if pygame.time.get_ticks() - wait_time > 700:
            a, b = revealed
            if colors[a] == colors[b]:
                matched.extend([a, b])
            else:
                errors += 1
                if errors > MAX_ERRORS:
                    game_over = True
            revealed = []
