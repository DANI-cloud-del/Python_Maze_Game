import pygame
from utils.settings import CELL_SIZE, PLAYER_SIZE

class Bullet:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.speed = 15
        self.radius = 5
        self.lifetime = 1000  # ms
        
        # Calculate direction vector
        dx = target_x - x
        dy = target_y - y
        distance = max(1, (dx**2 + dy**2)**0.5)
        self.vx = (dx / distance) * self.speed
        self.vy = (dy / distance) * self.speed

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 16  # Approximate frame time

    def draw(self, screen, camera):
        pos = camera.apply_pos((self.x, self.y))
        pygame.draw.circle(screen, (255, 200, 0), pos, self.radius)

class ShootingSystem:
    def __init__(self, player):
        self.player = player
        self.bullets = []
        self.cooldown = 300  # ms
        self.last_shot = 0
        self.max_ammo = 20
        self.ammo = 10

    def shoot(self, target_pos, current_time):
        if self.ammo > 0 and current_time - self.last_shot > self.cooldown:
            self.ammo -= 1
            self.last_shot = current_time
            self.bullets.append(
                Bullet(self.player.rect.centerx, 
                      self.player.rect.centery,
                      target_pos[0], target_pos[1])
            )

    def update(self, enemies):
        for bullet in self.bullets[:]:
            bullet.update()
            
            # Check enemy hits
            for enemy in enemies[:]:
                if (abs(bullet.x//CELL_SIZE - enemy.x) < 1 and 
                    abs(bullet.y//CELL_SIZE - enemy.y) < 1):
                    enemies.remove(enemy)
                    self.bullets.remove(bullet)
                    break
            
            # Remove expired bullets
            if bullet.lifetime <= 0:
                self.bullets.remove(bullet)

    def draw(self, screen, camera):
        for bullet in self.bullets:
            bullet.draw(screen, camera)