import pygame
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.velocity = random.randint(2, 5)
        self.health = 30
        
        # Charger l'image du serpent
        self.image = pygame.image.load('assets/snake.png')
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
    """Flammes qui tombent du ciel - obstacles à éviter"""
    def __init__(self):
        super().__init__()
        self.velocity = random.randint(3, 6)
        
        # Charger l'image de la flamme
        self.image = pygame.image.load('assets/flame.png')
        self.image = pygame.transform.scale(self.image, (50, 60))
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(100, 750)
        self.rect.y = -60  # Commence en haut de l'écran

    def update(self):
        self.rect.y += self.velocity
        # Supprimer si sort de l'écran
        if self.rect.y > 600:
            self.kill()






