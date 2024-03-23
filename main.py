import pygame
import random
import math
from pygame.locals import (
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)


# Initialisierung von Pygame
pygame.init()

# Bildschirmgröße festlegen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Titel und Icon
pygame.display.set_caption("JO Astroid")

# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Spielvariablen
running = True
score = 0
player_size = 50
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 2 * player_size]
enemy_size = 50
enemy_pos = [random.randint(0, SCREEN_WIDTH-enemy_size), 0]
enemy_list = [enemy_pos]
SPEED = 10
clock = pygame.time.Clock()

# Spieler Schiff
ship_image = pygame.image.load('spaceship.png').convert_alpha() 
ship_image = pygame.transform.scale(ship_image, (player_size, player_size))
ship_rect = ship_image.get_rect(center=player_pos)

# Meteriod
metroid_image = pygame.image.load('metroid_small.png').convert_alpha()

# Bullet Klasse
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.surf = pygame.Surface((5, 10))
        self.surf.fill((255, 0, 0))
        self.rect = self.surf.get_rect(center=(x, y))
        
    def update(self):
        self.rect.move_ip(0, -10)
        if self.rect.bottom < 0:
            self.kill()

# Player Klasse
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = ship_image
        self.rect = self.surf.get_rect(center=player_pos)
        self.mask = pygame.mask.from_surface(self.surf)  # Create a mask for the image

    def update(self, pressed_keys):
        if pressed_keys[pygame.K_LEFT]:
            self.rect.move_ip(-5, 0)
        if pressed_keys[pygame.K_RIGHT]:
            self.rect.move_ip(5, 0)

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

# Enemy Klasse
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = random.randint(20, 100)
        # self.surf = pygame.Surface((self.size, self.size))
        # self.surf.fill(BLACK)
        self.surf = metroid_image
        self.surf = pygame.transform.scale(self.surf, (self.size, self.size))

        self.rect = self.surf.get_rect(
            center=(
                random.randint(0, SCREEN_WIDTH - self.size),
                -self.size,
            )
        )

        self.mask = pygame.mask.from_surface(self.surf)  # Create a mask for the image
        self.speed = random.randint(5, 10)

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Health Bar Klasse
class HealthBar:
    def __init__(self, x, y, max_health):
        self.max_health = max_health
        self.current_health = max_health
        self.surf = pygame.Surface((100, 10))  # Breite 100px, Höhe 10px
        self.rect = self.surf.get_rect(topleft=(x, y))
        
    def take_damage(self, damage):
        self.current_health -= damage
        if self.current_health < 0:
            self.current_health = 0

    def set_max_health(self, new_max_health):
        self.max_health = new_max_health

    def draw(self, screen):
        # Zeichne Hintergrund der Gesundheitsleiste
        pygame.draw.rect(screen, (0, 0, 0), self.rect)
        # Aktuellen Gesundheitsstand berechnen
        health_pct = max(self.current_health / self.max_health, 0)
        current_width = health_pct * self.rect.width
        # Zeichne aktuelle Gesundheit
        pygame.draw.rect(screen, (0, 255, 0), (self.rect.x, self.rect.y, current_width, self.rect.height))

# Setup für unsere Sprites
P1 = Player()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(P1)

# Platzieren der Healthbar Leiste
x_position = 50
y_position = 50

# Erstellung einer HealthBar-Instanz mit einem maximalen Gesundheitswert von 100
health_bar = HealthBar(x=x_position, y=y_position, max_health=200)

# Enemy hinzufügen Timer
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 250)

# Bullet schießen Timer
ADDBULLET = pygame.USEREVENT + 2
pygame.time.set_timer(ADDBULLET, 150)

# Calculate Damage Funktion
def calculate_damage(meteor_size):
    # Definiere die Logik zur Berechnung des Schadens basierend auf der Größe des Meteoriten
    damage = meteor_size * 1  # Beispiel für eine einfache Schadensberechnung
    return damage

# Spiel Loop
while running:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        
        elif event.type == QUIT:
            running = False
        
        elif event.type == ADDENEMY:
            new_enemy = Enemy()
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)
        
        elif event.type == ADDBULLET:
            new_bullet = Bullet(P1.rect.centerx, P1.rect.top)
            bullets.add(new_bullet)
            all_sprites.add(new_bullet)

    pressed_keys = pygame.key.get_pressed()
    
    # Spieler, Bullets und Enemies aktualisieren
    P1.update(pressed_keys)
    enemies.update()
    bullets.update()
    
    # Überprüfen ob Bullets die Enemies treffen
    for bullet in bullets:
        hits = pygame.sprite.spritecollide(bullet, enemies, True)
        # ToDo: Hit abhängig von Größe
        for hit in hits:
            score += hit.size  # Addieren der Größe des getroffenen Meteoriten zum Score.
            bullet.kill()

    # Kollosion mit Meteroiden
    collisions = pygame.sprite.spritecollide(P1, enemies, False, pygame.sprite.collide_mask)
    for meteor in collisions:
        damage = calculate_damage(meteor.size)  
        health_bar.take_damage(damage)
        meteor.kill()  # Meteor verschwindet nach der Kollision
    
    # Wenn Leben aufgebraucht, beendet das Spiel
    if health_bar.current_health <=0:
        running = False

    # Bildschirm weiß füllen
    screen.fill((0, 0, 255))

    # Alle Sprites auf den Bildschirm zeichnen
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)

    # Punktzahl anzeigen
    font = pygame.font.SysFont("monospace", 35)
    score_text = font.render("Score: {0}".format(score), 1, BLACK)
    screen.blit(score_text, (5, 10))

    # Zeichne die Healthbar
    health_bar.draw(screen)

    pygame.display.flip()

    clock.tick(30)

pygame.quit()