import pygame
from game import Game

pygame.init()
pygame.mixer.init()

# Générer la fenêtre de jeu
pygame.display.set_caption("LABO")
screen = pygame.display.set_mode((800, 600))

# Charger le jeu (le fond est maintenant généré procéduralement dans Game)
game = Game()

# Clock pour gérer le FPS
clock = pygame.time.Clock()

running = True

# Dictionnaire pour les touches pressées
keys_pressed = {}

# Création de boucle tant que la condition est vraie
while running:
    # Limiter à 60 FPS
    clock.tick(60)

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            print("Fermeture du jeu")
            break

        # Détecter si un joueur appuie sur une touche
        elif event.type == pygame.KEYDOWN:
            keys_pressed[event.key] = True
            
            # Tirer avec ESPACE
            if event.key == pygame.K_SPACE and not game.game_over and not game.game_finished and not game.paused:
                game.player.shoot()
                if event.key == pygame.K_SPACE and not game.paused:
                    game.player.shoot()
                    game.sound_shoot.play()  # Jouer le son de tir

                if (event.key == pygame.K_UP or event.key == pygame.K_z) and not game.paused:
                    if game.player.jumps_remaining > 0:  # Si le joueur peut encore sauter
                        game.sound_jump.play()
                    game.player.jump()
            
            # Sauter avec FLÈCHE HAUT ou Z
            if (event.key == pygame.K_UP or event.key == pygame.K_z) and not game.game_over and not game.game_finished and not game.paused:
                game.player.jump()
            
            # Recommencer avec R
            if event.key == pygame.K_r and (game.game_over or game.game_finished):
                game.restart()
            
            # Toggle pause avec P
            if event.key == pygame.K_p:
                game.toggle_pause()
            
            # Toggle menu avec M
            if event.key == pygame.K_m:
                game.toggle_menu()
            
            # Fermer menu/historique avec ESC
            if event.key == pygame.K_ESCAPE:
                if game.show_history:
                    game.show_history = False
                elif game.show_menu:
                    game.show_menu = False

        # Détecter si un joueur relâche une touche
        elif event.type == pygame.KEYUP:
            keys_pressed[event.key] = False

        # Détection des clics souris
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # clic gauche
                mouse_pos = pygame.mouse.get_pos()
                
                # Clic sur le bouton pause
                if game.pause_button_rect.collidepoint(mouse_pos):
                    game.toggle_pause()
                
                # Clic sur le bouton menu
                elif game.menu_button_rect.collidepoint(mouse_pos):
                    game.toggle_menu()
                
                # Clics dans le menu principal
                elif game.show_menu:
                    # Bouton Historique
                    if hasattr(game, 'menu_history_btn') and game.menu_history_btn.collidepoint(mouse_pos):
                        game.show_menu = False
                        game.show_history = True
                    # Bouton Reprendre
                    elif hasattr(game, 'menu_resume_btn') and game.menu_resume_btn.collidepoint(mouse_pos):
                        game.show_menu = False
                        game.toggle_pause()  # dépauser

    # Mouvement continu du joueur si une touche est pressée
    if not game.game_over and not game.game_finished and not game.paused and not game.show_history and not game.show_menu:
        if keys_pressed.get(pygame.K_RIGHT, False):
            game.player.move_right()
        if keys_pressed.get(pygame.K_LEFT, False):
            game.player.move_left()

    # Mise à jour du jeu
    game.update()

    # Dessiner tout (fond + éléments + joueur inclus dans game.draw)
    game.draw(screen)

    # Mise à jour de l'écran
    pygame.display.flip()

    # Vérifier si running est toujours True (après pygame.quit())
    if not running:
        break