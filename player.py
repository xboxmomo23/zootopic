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
        self.image = pygame.image.load('assets/player.png')
        # Rétrécir l'image car image trop grande
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 490
        
        # Système de saut
        self.is_jumping = False
        self.jump_velocity = 0
        self.gravity = 0.8
        self.jump_strength = -15
        self.ground_y = 490
        
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
        # Ne sauter que si on est au sol
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_velocity = self.jump_strength

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






