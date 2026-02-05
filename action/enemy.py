import pygame
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.velocity = random.randint(2, 5)
        self.health = 30
        
        # Charger l'image de l'ours
        self.image = pygame.image.load('assets/OURS.png')
        self.image = pygame.transform.scale(self.image, (80, 80))
        
        self.rect = self.image.get_rect()
        self.rect.x = 850
        self.rect.y = random.randint(100, 500)

    def update(self):
        self.rect.x -= self.velocity
        # Supprimer si sort de l'écran
        if self.rect.x < -80:
            self.kill()

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True
        return False


class Flame(pygame.sprite.Sprite):
    """Flammes qui tombent du ciel - obstacles à éviter (plus nombreuses et variées)"""
    def __init__(self):
        super().__init__()
        self.velocity = random.randint(3, 7)  # Vitesse plus variable
        
        # Tailles aléatoires pour plus de variété visuelle
        self.flame_size = random.choice(['small', 'medium', 'large'])
        if self.flame_size == 'small':
            w, h = 30, 38
        elif self.flame_size == 'medium':
            w, h = 50, 60
        else:
            w, h = 65, 78
        
        # Charger l'image de la fleur du mal
        self.image = pygame.image.load('assets/Fleursdumal.png')
        self.image = pygame.transform.scale(self.image, (w, h))
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(50, 750)
        self.rect.y = -h  # Commence en haut de l'écran selon sa taille

    def update(self):
        self.rect.y += self.velocity
        # Supprimer si sort de l'écran
        if self.rect.y > 620:
            self.kill()


class FlameRain:
    """Gestionnaire qui spawn des flammes en rafale pour créer une pluie de feu"""
    def __init__(self):
        self.flames = pygame.sprite.Group()
        self.timer = 0
        # Intervalle de base entre les flammes (en frames) — plus grand = moins de flammes
        self.base_interval = 70
        # Légère variation aléatoire pour que ça ne soit pas trop mécanique
        self.next_spawn = self.base_interval + random.randint(-12, 12)
        
        # Parfois on lance une rafale de 2 flammes
        self.burst_mode = False
        self.burst_count = 0
        self.burst_timer = 0
        self.burst_delay = 12  # frames entre chaque flamme d'une rafale

    def update(self):
        self.timer += 1
        
        # Mode rafale actif
        if self.burst_mode:
            self.burst_timer += 1
            if self.burst_timer >= self.burst_delay:
                flame = Flame()
                self.flames.add(flame)
                self.burst_count -= 1
                self.burst_timer = 0
                if self.burst_count <= 0:
                    self.burst_mode = False
        
        # Spawn normal
        if self.timer >= self.next_spawn:
            flame = Flame()
            self.flames.add(flame)
            self.timer = 0
            self.next_spawn = self.base_interval + random.randint(-8, 8)
            
            # 12% de chance de déclencher une petite rafale après un spawn normal
            if random.random() < 0.12:
                self.burst_mode = True
                self.burst_count = 2
                self.burst_timer = 0
        
        self.flames.update()

    def draw(self, screen):
        self.flames.draw(screen)