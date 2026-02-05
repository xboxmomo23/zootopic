import pygame

# Classe pour les projectiles (missiles)
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.velocity = 10
        self.image = pygame.image.load('assets/missile.png')
        self.image = pygame.transform.scale(self.image, (50, 30))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.x += self.velocity
        # Supprimer si sort de l'écran
        if self.rect.x > 850:
            self.kill()

# Création de la classe pour le joueur
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.health = 100
        self.max_health = 100
        self.attack = 30
        self.velocity = 6
        self.score = 0
        self.image = pygame.image.load('assets/Flash.png')
        # Rétrécir l'image car image trop grande
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 490
        
        # Système de triple saut et demi
        self.is_jumping = False
        self.jump_velocity = 0
        self.gravity = 0.8
        self.jump_strength  = -15         # Force du 1er saut
        self.jump2_strength = -14         # Force du 2ème saut
        self.jump3_strength = -13         # Force du 3ème saut
        self.half_jump_strength = -7      # Petit boost (le "demi-saut", 4ème pression)
        self.ground_y = 490
        self.jumps_remaining = 3          # 3 sauts complets disponibles
        self.max_jumps = 3
        self.half_jump_used = False       # Le demi-saut pas encore utilisé cette phase
        
        # Particules pour le double saut
        self.double_jump_particles = []
        
        # Projectiles
        self.all_projectiles = pygame.sprite.Group()
        self.last_shot = pygame.time.get_ticks()
        self.shoot_cooldown = 400  # millisecondes

    def move_right(self):
        # Vérifier qu'on ne sort pas de l'écran
        if self.rect.x < 720:
            self.rect.x += self.velocity
    
    def move_left(self):
        # Vérifier qu'on ne sort pas de l'écran
        if self.rect.x > 0:
            self.rect.x -= self.velocity

    def jump(self):
        # ── sauts complets (1er / 2ème / 3ème) ──
        if self.jumps_remaining > 0:
            if self.jumps_remaining == 3:
                self.jump_velocity = self.jump_strength          # 1er saut
            elif self.jumps_remaining == 2:
                self.jump_velocity = self.jump2_strength         # 2ème saut
                self._spawn_jump_particles('orange')
            else:                                                # 3ème saut
                self.jump_velocity = self.jump3_strength
                self._spawn_jump_particles('red')

            self.is_jumping = True
            self.jumps_remaining -= 1

        # ── demi-saut (4ème pression, petit boost vers le haut) ──
        elif not self.half_jump_used and self.is_jumping:
            self.jump_velocity = self.half_jump_strength
            self.half_jump_used = True
            self._spawn_jump_particles('white')

    def _spawn_jump_particles(self, theme='orange'):
        """Créer des particules visuelles — thème selon le niveau de saut"""
        import random
        palettes = {
            'orange': [(255, 200, 50), (255, 150, 0), (255, 100, 50)],
            'red':    [(255, 60, 60),  (220, 30, 30), (255, 80, 40)],
            'white':  [(255, 255, 255),(230, 230, 255),(200, 220, 255)],
        }
        colors = palettes.get(theme, palettes['orange'])
        count = 8 if theme == 'white' else 12          # moins de particules pour le demi-saut
        for _ in range(count):
            self.double_jump_particles.append({
                'x': self.rect.centerx + random.randint(-20, 20),
                'y': self.rect.bottom  + random.randint(-5, 5),
                'vx': random.uniform(-2.5, 2.5),
                'vy': random.uniform(-1, 2),
                'life': random.randint(15, 30),
                'max_life': 30,
                'size': random.randint(3, 7),
                'color_base': random.choice(colors)
            })

    def update_gravity(self):
        # Appliquer la gravité
        if self.is_jumping:
            self.jump_velocity += self.gravity
            self.rect.y += self.jump_velocity
            
            # Vérifier si on retombe au sol
            if self.rect.y >= self.ground_y:
                self.rect.y = self.ground_y
                self.is_jumping = False
                self.jump_velocity = 0
                self.jumps_remaining = self.max_jumps  # Réinitialiser les sauts au sol
                self.half_jump_used = False             # Réinitialiser le demi-saut aussi

        # Mettre à jour les particules du double saut
        self._update_particles()

    def _update_particles(self):
        """Mettre à jour et nettoyer les particules"""
        alive = []
        for p in self.double_jump_particles:
            p['life'] -= 1
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1  # gravité sur particules
            if p['life'] > 0:
                alive.append(p)
        self.double_jump_particles = alive

    def draw_particles(self, screen):
        """Dessiner les particules du double saut"""
        for p in self.double_jump_particles:
            ratio = p['life'] / p['max_life']
            size = max(1, int(p['size'] * ratio))
            # Couleur qui s'atténue avec le temps
            r = min(255, int(p['color_base'][0] * ratio + 50 * (1 - ratio)))
            g = min(255, int(p['color_base'][1] * ratio))
            b = min(255, int(p['color_base'][2] * ratio))
            alpha_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surf, (r, g, b, int(255 * ratio)), (size, size), size)
            screen.blit(alpha_surf, (int(p['x']) - size, int(p['y']) - size))

    def shoot(self):
        # Vérifier le cooldown
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_cooldown:
            self.last_shot = now
            projectile = Projectile(self.rect.x + 70, self.rect.y + 25)
            self.all_projectiles.add(projectile)

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def draw_health_bar(self, screen):
        # Arrière-plan de la barre
        pygame.draw.rect(screen, (255, 0, 0), (10, 10, 200, 20))
        # Barre de vie actuelle
        health_width = int((self.health / self.max_health) * 200)
        pygame.draw.rect(screen, (0, 255, 0), (10, 10, health_width, 20))
        # Bordure
        pygame.draw.rect(screen, (255, 255, 255), (10, 10, 200, 20), 2)

    def draw_jump_indicator(self, screen):
        """Afficher les sauts restants sous forme de points au-dessus du joueur"""
        if not self.is_jumping:
            return                                  # au sol → rien à montrer

        has_something = self.jumps_remaining > 0 or not self.half_jump_used
        if not has_something:
            return

        tick = pygame.time.get_ticks()
        # calcul de la largeur totale pour centrer
        total_dots  = self.jumps_remaining + (0 if self.half_jump_used else 1)
        spacing     = 14
        total_width = total_dots * spacing - spacing
        start_x     = self.rect.centerx - total_width // 2
        dot_y       = self.rect.top - 14

        idx = 0
        # ── points pour les sauts complets restants ──
        colors_full = [(255, 215, 0), (255, 140, 0), (255, 60, 60)]   # or / orange / rouge
        for i in range(self.jumps_remaining):
            x = start_x + idx * spacing
            # clignoter legèrement
            if (tick // 180) % 2 == 0:
                color = colors_full[min(i, len(colors_full) - 1)]
                pygame.draw.circle(screen, color,        (x, dot_y), 5)
                pygame.draw.circle(screen, (255,255,255),(x, dot_y), 5, 2)
            idx += 1

        # ── point pour le demi-saut restant (plus petit, blanc) ──
        if not self.half_jump_used:
            x = start_x + idx * spacing
            if (tick // 180) % 2 == 0:
                pygame.draw.circle(screen, (200, 220, 255), (x, dot_y), 3)
                pygame.draw.circle(screen, (255, 255, 255), (x, dot_y), 3, 1)