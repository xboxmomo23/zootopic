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


# ----- FONCTIONS -----

def setup_game():
    global colors, cards, revealed, matched

    colors = card_colors.copy()
    random.shuffle(colors)

    cards = []
    revealed = []
    matched = []

    for i in range(16):
        x = (i % COLS) * (CARD_SIZE + MARGIN) + MARGIN
        y = (i // COLS) * (CARD_SIZE + MARGIN) + START_Y

        rect = pygame.Rect(x, y, CARD_SIZE, CARD_SIZE)
        cards.append(rect)


def draw_background():
    screen.fill(BACKGROUND)
    pygame.draw.rect(screen, GREEN_SOFT, (0, 0, WIDTH, HEIGHT))


def draw_cards():
    for i, rect in enumerate(cards):
        if i in revealed or i in matched:
            pygame.draw.rect(screen, colors[i], rect)
        else:
            pygame.draw.rect(screen, GRAY, rect)


def get_card(pos):
    for i, rect in enumerate(cards):
        if rect.collidepoint(pos):
            return i
    return None


def draw_button():
    button_rect = pygame.Rect(200, 600, 200, 60)
    pygame.draw.rect(screen, WHITE, button_rect)
    pygame.draw.rect(screen, BLACK, button_rect, 2)

    font = pygame.font.SysFont(None, 40)
    text = font.render("Recommencer", True, BLACK)
    screen.blit(text, (button_rect.x + 25, button_rect.y + 15))

    return button_rect


# ----- INITIALISATION -----

setup_game()
wait_time = 0

# ----- BOUCLE DU JEU -----

running = True

while running:
    clock.tick(60)

    draw_background()
    draw_cards()

    all_found = len(matched) == 16

    if all_found:
        button = draw_button()

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:

            if all_found:
                if button.collidepoint(event.pos):
                    setup_game()
            else:
                if len(revealed) < 2:
                    clicked = get_card(event.pos)

                    if clicked is not None and clicked not in revealed and clicked not in matched:
                        revealed.append(clicked)

                        if len(revealed) == 2:
                            wait_time = pygame.time.get_ticks()

    if len(revealed) == 2:
        if pygame.time.get_ticks() - wait_time > 700:
            a, b = revealed

            if colors[a] == colors[b]:
                matched.extend([a, b])

            revealed = []

pygame.quit()
