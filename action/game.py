import pygame
from player import Player
from enemy import Enemy, Flame, FlameRain
import random
import json
import os
import math

# ---------- Génération procédurale du fond d'écran ----------
def generate_background(width, height):
    """
    Génère un fond d'écran magnifique avec :
    - un ciel dégradé du bleu profond au rose/orange (crépuscule)
    - des nuages moelleux
    - des collines en arrière-plan (parallax)
    - un sol herbeux
    """
    surface = pygame.Surface((width, height))

    # --- 1) Dégradé du ciel : bleu nuit → violet → rose → orange (crépuscule) ---
    for y in range(height):
        ratio = y / height
        # Couleurs clés du crépuscule
        if ratio < 0.25:
            # Haut : bleu profond vers violet
            t = ratio / 0.25
            r = int(20 + (80 - 20) * t)
            g = int(10 + (30 - 10) * t)
            b = int(60 + (100 - 60) * t)
        elif ratio < 0.5:
            # Milieu-haut : violet vers rose
            t = (ratio - 0.25) / 0.25
            r = int(80 + (180 - 80) * t)
            g = int(30 + (80 - 30) * t)
            b = int(100 + (120 - 100) * t)
        elif ratio < 0.7:
            # Milieu : rose vers orange chaud
            t = (ratio - 0.5) / 0.2
            r = int(180 + (230 - 180) * t)
            g = int(80 + (140 - 80) * t)
            b = int(120 + (80 - 120) * t)
        elif ratio < 0.85:
            # Bas-milieu : orange vers jaune doré
            t = (ratio - 0.7) / 0.15
            r = int(230 + (240 - 230) * t)
            g = int(140 + (190 - 140) * t)
            b = int(80 + (60 - 80) * t)
        else:
            # Bas : jaune doré vers vert sombre (horizon)
            t = (ratio - 0.85) / 0.15
            r = int(240 + (80 - 240) * t)
            g = int(190 + (140 - 190) * t)
            b = int(60 + (60 - 60) * t)
        
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

    # --- 2) Cercle du soleil (grand, doré, dans l'horizon) ---
    sun_x, sun_y = width // 2, int(height * 0.72)
    # Rayons lumineaux (cercles concentriques translucides)
    for i in range(4, 0, -1):
        alpha_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        alpha = 30 - i * 6
        pygame.draw.circle(alpha_surf, (255, 230, 100, alpha), (sun_x, sun_y), 55 + i * 18)
        surface.blit(alpha_surf, (0, 0))
    # Soleil principal
    pygame.draw.circle(surface, (255, 240, 150), (sun_x, sun_y), 55)
    pygame.draw.circle(surface, (255, 255, 200), (sun_x, sun_y), 42)

    # --- 3) Nuages (forme arrondies, semi-translucides) ---
    cloud_data = [
        # (x, y, [(rayon, offset_x, offset_y), ...], couleur_base)
        (100, 80,  [(35,0,0),(25,40,5),(28,-35,3),(20,60,-2)], (220, 210, 230)),
        (350, 55,  [(40,0,0),(30,45,8),(32,-40,2),(22,70,-5),(18,-60,4)], (240, 225, 240)),
        (580, 100, [(30,0,0),(22,38,4),(26,-30,2),(18,55,-3)], (210, 200, 225)),
        (750, 60,  [(28,0,0),(20,35,3),(24,-28,5)], (230, 220, 235)),
        (200, 140, [(22,0,0),(16,30,3),(18,-25,2)], (255, 240, 245)),
        (500, 130, [(34,0,0),(26,42,6),(29,-38,3),(19,65,-4)], (245, 235, 245)),
        (680, 145, [(25,0,0),(18,32,4),(21,-28,3)], (235, 225, 240)),
        (50,  160, [(20,0,0),(15,28,2),(17,-24,4)], (240, 230, 240)),
    ]
    for cx, cy, circles, base_color in cloud_data:
        cloud_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        for radius, ox, oy in circles:
            # Légère variation de couleur pour chaque cercle
            cr = min(255, base_color[0] + random.randint(-8, 8))
            cg = min(255, base_color[1] + random.randint(-8, 8))
            cb = min(255, base_color[2] + random.randint(-8, 8))
            pygame.draw.circle(cloud_surf, (cr, cg, cb, 160), (cx + ox, cy + oy), radius)
        surface.blit(cloud_surf, (0, 0))

    # --- 4) Collines en arrière-plan (parallax, 3 couches) ---
    # Colline arrière (plus sombre, plus éloignée)
    hill_back_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    points_back = [(0, height)]
    for x in range(0, width + 10, 5):
        # Onde sinusoïdale pour créer des collines
        y_val = int(height * 0.68 + 40 * math.sin(x * 0.008 + 1.2) + 25 * math.sin(x * 0.015 + 3.0))
        points_back.append((x, y_val))
    points_back.append((width, height))
    pygame.draw.polygon(hill_back_surf, (55, 75, 60, 200), points_back)
    surface.blit(hill_back_surf, (0, 0))

    # Colline milieu (plus verte)
    hill_mid_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    points_mid = [(0, height)]
    for x in range(0, width + 10, 5):
        y_val = int(height * 0.74 + 30 * math.sin(x * 0.011 + 0.5) + 18 * math.sin(x * 0.02 + 2.1))
        points_mid.append((x, y_val))
    points_mid.append((width, height))
    pygame.draw.polygon(hill_mid_surf, (60, 100, 55, 220), points_mid)
    surface.blit(hill_mid_surf, (0, 0))

    # Colline avant (la plus claire, la plus proche)
    hill_front_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    points_front = [(0, height)]
    for x in range(0, width + 10, 5):
        y_val = int(height * 0.80 + 22 * math.sin(x * 0.014 + 4.0) + 14 * math.sin(x * 0.025 + 0.8))
        points_front.append((x, y_val))
    points_front.append((width, height))
    pygame.draw.polygon(hill_front_surf, (75, 125, 65, 230), points_front)
    surface.blit(hill_front_surf, (0, 0))

    # --- 5) Sol principal (gazon) avec dégradé vert ---
    ground_top = int(height * 0.835)
    for y in range(ground_top, height):
        ratio = (y - ground_top) / (height - ground_top)
        r = int(55 + (40 - 55) * ratio)
        g = int(110 + (80 - 110) * ratio)
        b = int(50 + (45 - 50) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

    # Ligne d'herbe (bord plus clair du sol)
    pygame.draw.line(surface, (90, 140, 70), (0, ground_top), (width, ground_top), 3)

    # --- 6) Petites herbes décoratives sur le sol ---
    random.seed(42)  # seed fixe pour que l'herbe soit toujours au même endroit
    for _ in range(180):
        gx = random.randint(0, width)
        gy = ground_top + random.randint(0, 8)
        gh = random.randint(5, 14)
        gcolor = (random.randint(70, 110), random.randint(130, 170), random.randint(50, 80))
        pygame.draw.line(surface, gcolor, (gx, gy), (gx + random.randint(-3, 3), gy - gh), 1)
    random.seed()  # re-randomiser

    # --- 7) Étoiles faintly dans le ciel (haut) ---
    random.seed(77)
    for _ in range(40):
        sx = random.randint(0, width)
        sy = random.randint(0, int(height * 0.3))
        brightness = random.randint(180, 255)
        size = random.choice([1, 1, 1, 2])
        star_surf = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(star_surf, (brightness, brightness, brightness, 140), (size + 1, size + 1), size)
        surface.blit(star_surf, (sx, sy))
    random.seed()

    return surface


# Création de la classe qui va représenter notre jeu
class Game:
    def __init__(self):
        self.player = Player()
        self.all_enemies = pygame.sprite.Group()
        self.flame_rain = FlameRain()  # Nouveau système de pluie de flammes
        self.enemy_spawn_timer = 0
        self.spawn_delay = 100  # frames entre chaque spawn d'ennemi
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

        # Génération du fond d'écran procédural
        # Chargement du fond d'écran LABO
        self.background = pygame.image.load('assets/LABO.png')
        self.background = pygame.transform.scale(self.background, (800, 600))

        # ── Système de pause ──
        self.paused = False
        self.pause_time = 0  # temps total en pause (pour ajuster le timer)

        # ── Menu principal ──
        self.show_menu = False

        # ── Menu historique ──
        self.show_history = False
        self.history_data = self.load_history()

        # ── Rectangles des boutons (en haut à droite) ──
        self.pause_button_rect = pygame.Rect(720, 10, 30, 30)
        self.menu_button_rect = pygame.Rect(760, 10, 30, 30)

        # 1. Charger et lancer la musique de fond
        pygame.mixer.music.load('assets/sounds/ROCK.mp3')
        pygame.mixer.music.set_volume(0.5)  # Volume à 50%
        pygame.mixer.music.play(-1)  # -1 pour boucler à l'infini

        # 2. Charger les effets sonores
        self.sound_shoot = pygame.mixer.Sound('assets/sounds/GUN.wav')
        self.sound_jump = pygame.mixer.Sound('assets/sounds/VOX.wav')
        self.sound_hit = pygame.mixer.Sound('assets/sounds/JUMP.wav')

        # Ajuster le volume des effets si besoin
        self.sound_shoot.set_volume(0.3)

    def spawn_enemy(self):
        enemy = Enemy()
        self.all_enemies.add(enemy)

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

    def load_history(self):
        """Charger l'historique des parties"""
        try:
            if os.path.exists('game_history.json'):
                with open('game_history.json', 'r') as f:
                    return json.load(f)
        except:
            pass
        return []

    def save_history(self, kills, duration, outcome):
        """Sauvegarder une partie dans l'historique (max 10 dernières parties)"""
        try:
            from datetime import datetime
            entry = {
                'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'kills': kills,
                'duration': int(duration),
                'outcome': outcome  # 'victoire' ou 'défaite'
            }
            self.history_data.insert(0, entry)  # ajouter en tête
            self.history_data = self.history_data[:10]  # garder seulement 10 dernières
            with open('game_history.json', 'w') as f:
                json.dump(self.history_data, f, indent=2)
        except:
            pass

    def update_timer(self):
        """Mettre à jour le temps restant"""
        if not self.game_over and not self.game_finished and not self.paused:
            elapsed_time = (pygame.time.get_ticks() - self.start_time - self.pause_time) / 1000
            self.remaining_time = max(0, self.game_duration - elapsed_time)
            
            # Si le temps est écoulé
            if self.remaining_time <= 0:
                self.game_finished = True
                # Mettre à jour le meilleur score
                if self.serpents_killed > self.best_score:
                    self.best_score = self.serpents_killed
                    self.save_best_score()
                # Sauvegarder dans l'historique
                self.save_history(self.serpents_killed, self.game_duration, 'victoire')

    def check_collisions(self):
        # Collision projectiles - ennemis (serpents)
        for projectile in self.player.all_projectiles:
            enemies_hit = pygame.sprite.spritecollide(projectile, self.all_enemies, False)
            for enemy in enemies_hit:
                projectile.kill()
                if enemy.take_damage(self.player.attack):
                    self.sound_hit.play()  # Son quand un ennemi meurt

            # Collision joueur - ennemis
        enemies_collided = pygame.sprite.spritecollide(self.player, self.all_enemies, True)
        if enemies_collided:
            self.sound_hit.play()  # Son quand le joueur prend un coup

        # Collision joueur - ennemis (serpents)
        enemies_collided = pygame.sprite.spritecollide(self.player, self.all_enemies, True)
        for enemy in enemies_collided:
            self.player.take_damage(25)
            if self.player.health <= 0:
                self.game_over = True
                # Sauvegarder dans l'historique (défaite)
                elapsed = (pygame.time.get_ticks() - self.start_time - self.pause_time) / 1000
                self.save_history(self.serpents_killed, elapsed, 'défaite')

        # Collision joueur - flammes (depuis le FlameRain)
        flames_collided = pygame.sprite.spritecollide(self.player, self.flame_rain.flames, True)
        for flame in flames_collided:
            self.player.take_damage(15)
            if self.player.health <= 0:
                self.game_over = True
                # Sauvegarder dans l'historique (défaite)
                elapsed = (pygame.time.get_ticks() - self.start_time - self.pause_time) / 1000
                self.save_history(self.serpents_killed, elapsed, 'défaite')

    def update(self):
        if self.paused or self.show_history or self.show_menu:
            return  # Ne rien mettre à jour si en pause, menu ou historique
        
        if not self.game_over and not self.game_finished:
            # Mettre à jour le timer
            self.update_timer()
            
            # Spawn des ennemis (serpents)
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer >= self.spawn_delay:
                self.spawn_enemy()
                self.enemy_spawn_timer = 0

            # Mettre à jour la pluie de flammes
            self.flame_rain.update()

            # Mise à jour de la gravité du joueur (inclut aussi les particules)
            self.player.update_gravity()

            # Mise à jour des sprites
            self.player.all_projectiles.update()
            self.all_enemies.update()

            # Vérifier les collisions
            self.check_collisions()

    def draw(self, screen):
        # Dessiner le fond d'écran procédural
        screen.blit(self.background, (0, 0))

        # Dessiner les flammes (derrière les ennemis pour la profondeur)
        self.flame_rain.draw(screen)

        # Dessiner les projectiles
        self.player.all_projectiles.draw(screen)
        
        # Dessiner les ennemis
        self.all_enemies.draw(screen)

        # Dessiner les particules du double saut
        self.player.draw_particles(screen)

        # Dessiner le joueur
        screen.blit(self.player.image, self.player.rect)

        # Indicateur de double saut
        self.player.draw_jump_indicator(screen)

        # Dessiner la barre de vie
        self.player.draw_health_bar(screen)

        # Afficher le temps restant (en haut au centre avec effet)
        time_color = (255, 255, 255) if self.remaining_time > 10 else (255, 50, 50)
        time_text = self.font.render(f'Temps: {int(self.remaining_time)}s', True, time_color)
        time_bg = pygame.Surface((180, 40), pygame.SRCALPHA)
        time_bg.fill((0, 0, 0, 150))
        screen.blit(time_bg, (310, 5))
        screen.blit(time_text, (320, 10))

        # Afficher les serpents tués (en haut à gauche sous la vie)
        kills_text = self.small_font.render(f'🐍 Serpents: {self.serpents_killed}', True, (255, 255, 255))
        kills_bg = pygame.Surface((200, 35), pygame.SRCALPHA)
        kills_bg.fill((0, 0, 0, 150))
        screen.blit(kills_bg, (10, 40))
        screen.blit(kills_text, (15, 45))

        # Afficher le record (en haut à droite)
        record_text = self.small_font.render(f'Record: {self.best_score} 🏆', True, (255, 215, 0))
        record_bg = pygame.Surface((180, 35), pygame.SRCALPHA)
        record_bg.fill((0, 0, 0, 150))
        screen.blit(record_bg, (610, 10))
        screen.blit(record_text, (615, 15))

        # ── Bouton PAUSE ──
        pause_color = (100, 180, 255) if not self.paused else (255, 100, 100)
        pygame.draw.rect(screen, pause_color, self.pause_button_rect, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), self.pause_button_rect, 2, border_radius=5)
        # Icône pause (2 barres) ou play (triangle)
        if not self.paused:
            # Barres de pause
            pygame.draw.rect(screen, (255, 255, 255), (725, 15, 6, 20))
            pygame.draw.rect(screen, (255, 255, 255), (735, 15, 6, 20))
        else:
            # Triangle play
            points = [(727, 15), (727, 35), (743, 25)]
            pygame.draw.polygon(screen, (255, 255, 255), points)

        # ── Bouton MENU (hamburger icon) ──
        menu_color = (150, 100, 255) if not self.show_menu else (255, 150, 100)
        pygame.draw.rect(screen, menu_color, self.menu_button_rect, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), self.menu_button_rect, 2, border_radius=5)
        # Icône hamburger (3 lignes)
        for i in range(3):
            y = 17 + i * 7
            pygame.draw.line(screen, (255, 255, 255), (765, y), (785, y), 3)



        # Afficher les instructions (en bas)
        controls_text = self.warning_font.render('ESPACE: Tirer | HAUT/Z: Saut (x3½)', True, (255, 255, 255))
        controls_bg = pygame.Surface((320, 25), pygame.SRCALPHA)
        controls_bg.fill((0, 0, 0, 130))
        screen.blit(controls_bg, (240, 572))
        screen.blit(controls_text, (245, 575))

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

        # ── Overlay de pause ──
        if self.paused and not self.game_over and not self.game_finished and not self.show_menu:
            overlay = pygame.Surface((800, 600))
            overlay.set_alpha(160)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            pause_title = self.big_font.render('PAUSE', True, (100, 180, 255))
            resume_text = self.font.render('Cliquez le bouton pause ou P pour reprendre', True, (255, 255, 255))
            menu_text = self.font.render('Cliquez le bouton menu pour les options', True, (200, 200, 200))
            
            screen.blit(pause_title, (280, 220))
            screen.blit(resume_text, (140, 300))
            screen.blit(menu_text, (170, 350))

        # ── Menu Principal ──
        if self.show_menu:
            overlay = pygame.Surface((800, 600))
            overlay.set_alpha(180)
            overlay.fill((25, 20, 45))
            screen.blit(overlay, (0, 0))
            
            title = self.big_font.render('MENU', True, (150, 100, 255))
            screen.blit(title, (320, 80))
            
            close_text = self.warning_font.render('Appuyez sur ESC ou M pour fermer', True, (180, 180, 180))
            screen.blit(close_text, (230, 560))
            
            # Bouton Historique (centré)
            history_btn_rect = pygame.Rect(250, 220, 300, 60)
            history_hover = history_btn_rect.collidepoint(pygame.mouse.get_pos())
            btn_color = (180, 130, 255) if history_hover else (120, 80, 200)
            pygame.draw.rect(screen, btn_color, history_btn_rect, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), history_btn_rect, 3, border_radius=10)
            
            history_btn_text = self.font.render('📊 HISTORIQUE', True, (255, 255, 255))
            text_rect = history_btn_text.get_rect(center=history_btn_rect.center)
            screen.blit(history_btn_text, text_rect)
            
            # Bouton Reprendre (centré, sous l'historique)
            resume_btn_rect = pygame.Rect(250, 310, 300, 60)
            resume_hover = resume_btn_rect.collidepoint(pygame.mouse.get_pos())
            resume_color = (100, 200, 150) if resume_hover else (60, 140, 100)
            pygame.draw.rect(screen, resume_color, resume_btn_rect, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), resume_btn_rect, 3, border_radius=10)
            
            resume_btn_text = self.font.render('▶ REPRENDRE', True, (255, 255, 255))
            text_rect2 = resume_btn_text.get_rect(center=resume_btn_rect.center)
            screen.blit(resume_btn_text, text_rect2)
            
            # Stocker les rectangles pour la détection de clic
            self.menu_history_btn = history_btn_rect
            self.menu_resume_btn = resume_btn_rect

        # ── Menu Historique ──
        if self.show_history:
            overlay = pygame.Surface((800, 600))
            overlay.set_alpha(190)
            overlay.fill((20, 20, 40))
            screen.blit(overlay, (0, 0))
            
            title = self.big_font.render('HISTORIQUE', True, (255, 215, 0))
            screen.blit(title, (220, 30))
            
            close_text = self.warning_font.render('Appuyez sur ESC pour fermer', True, (180, 180, 180))
            screen.blit(close_text, (230, 560))
            
            if not self.history_data:
                no_data_text = self.font.render('Aucune partie enregistrée', True, (150, 150, 150))
                screen.blit(no_data_text, (230, 280))
            else:
                # Définir les positions X des colonnes
                col_date = 70
                col_kills = 350
                col_duration = 480
                col_outcome = 600
                
                y_offset = 110
                
                # En-têtes de colonnes
                header_date = self.small_font.render('Date & Heure', True, (200, 200, 200))
                header_kills = self.small_font.render('Serpents', True, (200, 200, 200))
                header_duration = self.small_font.render('Durée', True, (200, 200, 200))
                header_outcome = self.small_font.render('Résultat', True, (200, 200, 200))
                
                screen.blit(header_date, (col_date, y_offset))
                screen.blit(header_kills, (col_kills, y_offset))
                screen.blit(header_duration, (col_duration, y_offset))
                screen.blit(header_outcome, (col_outcome, y_offset))
                
                y_offset += 40
                
                # Lignes de données
                for i, entry in enumerate(self.history_data[:10]):
                    date_str = entry.get('date', '?')
                    kills = entry.get('kills', 0)
                    duration = entry.get('duration', 0)
                    outcome = entry.get('outcome', '?')
                    
                    outcome_color = (100, 255, 100) if outcome == 'victoire' else (255, 100, 100)
                    
                    # Rendre chaque colonne séparément
                    date_surf = self.warning_font.render(date_str, True, (220, 220, 220))
                    kills_surf = self.warning_font.render(str(kills), True, (220, 220, 220))
                    duration_surf = self.warning_font.render(f"{duration}s", True, (220, 220, 220))
                    outcome_surf = self.warning_font.render(outcome.upper(), True, outcome_color)
                    
                    screen.blit(date_surf, (col_date, y_offset))
                    screen.blit(kills_surf, (col_kills, y_offset))
                    screen.blit(duration_surf, (col_duration, y_offset))
                    screen.blit(outcome_surf, (col_outcome, y_offset))
                    
                    y_offset += 35

    def toggle_pause(self):
        """Basculer l'état de pause"""
        if not self.game_over and not self.game_finished:
            self.paused = not self.paused
            if self.paused:
                self.pause_start = pygame.time.get_ticks()
            else:
                self.pause_time += pygame.time.get_ticks() - self.pause_start
                # Fermer le menu et l'historique si on reprend
                self.show_menu = False
                self.show_history = False

    def toggle_menu(self):
        """Basculer l'affichage du menu"""
        if not self.game_over and not self.game_finished:
            self.show_menu = not self.show_menu
            # Si on ouvre le menu, mettre en pause automatiquement
            if self.show_menu:
                if not self.paused:
                    self.paused = True
                    self.pause_start = pygame.time.get_ticks()
                # Fermer l'historique si ouvert
                self.show_history = False
            # Si on ferme le menu, on reste en pause (l'utilisateur peut cliquer pause pour reprendre)

    def toggle_history(self):
        """Basculer l'affichage de l'historique"""
        self.show_history = not self.show_history
        # Si on ouvre l'historique en jeu, mettre en pause automatiquement
        if self.show_history and not self.game_over and not self.game_finished:
            if not self.paused:
                self.paused = True
                self.pause_start = pygame.time.get_ticks()
            # Fermer le menu si ouvert
            self.show_menu = False

    def restart(self):
        self.player = Player()
        self.all_enemies.empty()
        self.flame_rain = FlameRain()  # Réinitialiser la pluie de flammes
        self.enemy_spawn_timer = 0
        self.game_over = False
        self.game_finished = False
        self.start_time = pygame.time.get_ticks()
        self.remaining_time = self.game_duration
        self.serpents_killed = 0
        self.paused = False
        self.pause_time = 0
        self.show_menu = False
        self.show_history = False
        self.history_data = self.load_history()  # recharger l'historique