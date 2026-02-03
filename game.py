import pygame
from player import Player
from enemy import Enemy, Flame
import random
import json
import os

# Création de la classe qui va représenter notre jeu
class Game:
    def __init__(self):
        self.player = Player()
        self.all_enemies = pygame.sprite.Group()
        self.all_flames = pygame.sprite.Group()
        self.enemy_spawn_timer = 0
        self.flame_spawn_timer = 0
        self.spawn_delay = 100  # frames entre chaque spawn d'ennemi
        self.flame_spawn_delay = 80  # frames entre chaque flamme
        self.game_over = False
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.warning_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 28)
        
        # Système de temps et record
        self.game_duration = 60  # Durée de la partie en secondes
        self.start_time = pygame.time.get_ticks()
        self.remaining_time = self.game_duration
        self.best_score = self.load_best_score()
        self.game_finished = False
        self.serpents_killed = 0

    def spawn_enemy(self):
        enemy = Enemy()
        self.all_enemies.add(enemy)

    def spawn_flame(self):
        flame = Flame()
        self.all_flames.add(flame)

    def load_best_score(self):
        """Charger le meilleur score depuis un fichier"""
        try:
            if os.path.exists('best_score.json'):
                with open('best_score.json', 'r') as f:
                    data = json.load(f)
                    return data.get('best_score', 0)
        except:
            pass
        return 0

    def save_best_score(self):
        """Sauvegarder le meilleur score"""
        try:
            with open('best_score.json', 'w') as f:
                json.dump({'best_score': self.best_score}, f)
        except:
            pass

    def update_timer(self):
        """Mettre à jour le temps restant"""
        if not self.game_over and not self.game_finished:
            elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
            self.remaining_time = max(0, self.game_duration - elapsed_time)
            
            # Si le temps est écoulé
            if self.remaining_time <= 0:
                self.game_finished = True
                # Mettre à jour le meilleur score
                if self.serpents_killed > self.best_score:
                    self.best_score = self.serpents_killed
                    self.save_best_score()

    def check_collisions(self):
        # Collision projectiles - ennemis (serpents)
        for projectile in self.player.all_projectiles:
            enemies_hit = pygame.sprite.spritecollide(projectile, self.all_enemies, False)
            for enemy in enemies_hit:
                projectile.kill()
                if enemy.take_damage(self.player.attack):
                    self.player.score += 15
                    self.serpents_killed += 1  # Compter les serpents tués

        # Collision joueur - ennemis (serpents)
        enemies_collided = pygame.sprite.spritecollide(self.player, self.all_enemies, True)
        for enemy in enemies_collided:
            self.player.take_damage(25)
            if self.player.health <= 0:
                self.game_over = True

        # Collision joueur - flammes
        flames_collided = pygame.sprite.spritecollide(self.player, self.all_flames, True)
        for flame in flames_collided:
            self.player.take_damage(15)
            if self.player.health <= 0:
                self.game_over = True

    def update(self):
        if not self.game_over and not self.game_finished:
            # Mettre à jour le timer
            self.update_timer()
            
            # Spawn des ennemis (serpents)
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer >= self.spawn_delay:
                self.spawn_enemy()
                self.enemy_spawn_timer = 0

            # Spawn des flammes
            self.flame_spawn_timer += 1
            if self.flame_spawn_timer >= self.flame_spawn_delay:
                self.spawn_flame()
                self.flame_spawn_timer = 0

            # Mise à jour de la gravité du joueur
            self.player.update_gravity()

            # Mise à jour des sprites
            self.player.all_projectiles.update()
            self.all_enemies.update()
            self.all_flames.update()

            # Vérifier les collisions
            self.check_collisions()

    def draw(self, screen):
        # Dessiner les projectiles
        self.player.all_projectiles.draw(screen)
        
        # Dessiner les ennemis
        self.all_enemies.draw(screen)

        # Dessiner les flammes
        self.all_flames.draw(screen)

        # Dessiner la barre de vie
        self.player.draw_health_bar(screen)

        # Afficher le temps restant (en haut au centre avec effet)
        time_color = (255, 255, 255) if self.remaining_time > 10 else (255, 0, 0)
        time_text = self.font.render(f'Temps: {int(self.remaining_time)}s', True, time_color)
        # Fond noir pour le temps
        time_bg = pygame.Surface((180, 40))
        time_bg.set_alpha(150)
        time_bg.fill((0, 0, 0))
        screen.blit(time_bg, (310, 5))
        screen.blit(time_text, (320, 10))

        # Afficher les serpents tués (en haut à gauche sous la vie)
        kills_text = self.small_font.render(f'🐍 Serpents: {self.serpents_killed}', True, (255, 255, 255))
        kills_bg = pygame.Surface((200, 35))
        kills_bg.set_alpha(150)
        kills_bg.fill((0, 0, 0))
        screen.blit(kills_bg, (10, 40))
        screen.blit(kills_text, (15, 45))

        # Afficher le record (en haut à droite)
        record_text = self.small_font.render(f'Record: {self.best_score} 🏆', True, (255, 215, 0))
        record_bg = pygame.Surface((180, 35))
        record_bg.set_alpha(150)
        record_bg.fill((0, 0, 0))
        screen.blit(record_bg, (610, 10))
        screen.blit(record_text, (615, 15))

        # Afficher les instructions (en bas)
        controls_text = self.warning_font.render('ESPACE: Tirer | HAUT/Z: Sauter', True, (255, 255, 255))
        screen.blit(controls_text, (230, 570))

        # Afficher le game over (mort)
        if self.game_over:
            overlay = pygame.Surface((800, 600))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            game_over_text = self.big_font.render('GAME OVER', True, (255, 0, 0))
            kills_final = self.font.render(f'Serpents tués: {self.serpents_killed}', True, (255, 255, 255))
            record_info = self.font.render(f'Record: {self.best_score}', True, (255, 215, 0))
            restart_text = self.font.render('Appuyez sur R pour recommencer', True, (255, 255, 255))
            
            screen.blit(game_over_text, (250, 180))
            screen.blit(kills_final, (280, 260))
            screen.blit(record_info, (300, 310))
            screen.blit(restart_text, (180, 380))

        # Afficher l'écran de fin (temps écoulé)
        elif self.game_finished:
            overlay = pygame.Surface((800, 600))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            finished_text = self.big_font.render('TEMPS ÉCOULÉ!', True, (255, 215, 0))
            kills_final = self.font.render(f'Serpents tués: {self.serpents_killed}', True, (255, 255, 255))
            
            # Nouveau record ?
            if self.serpents_killed == self.best_score and self.serpents_killed > 0:
                record_info = self.big_font.render('NOUVEAU RECORD! 🏆', True, (0, 255, 0))
                screen.blit(record_info, (150, 340))
            else:
                record_info = self.font.render(f'Record: {self.best_score}', True, (255, 215, 0))
                screen.blit(record_info, (300, 310))
            
            restart_text = self.font.render('Appuyez sur R pour recommencer', True, (255, 255, 255))
            
            screen.blit(finished_text, (180, 180))
            screen.blit(kills_final, (260, 260))
            screen.blit(restart_text, (180, 420))

    def restart(self):
        self.player = Player()
        self.all_enemies.empty()
        self.all_flames.empty()
        self.enemy_spawn_timer = 0
        self.flame_spawn_timer = 0
        self.game_over = False
        self.game_finished = False
        self.start_time = pygame.time.get_ticks()
        self.remaining_time = self.game_duration
        self.serpents_killed = 0