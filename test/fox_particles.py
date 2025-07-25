import pygame
import random
import math

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Fox shape as a set of points (simplified silhouette)
fox_outline = [
    (400, 300), (390, 290), (410, 290),  # Head
    (385, 280), (415, 280),              # Ears
    (395, 310), (405, 310),              # Neck
    (380, 320), (420, 320),              # Shoulders
    (370, 340), (430, 340),              # Body
    (360, 360), (440, 360),              # Legs
    (350, 380), (450, 380),              # Tail base
    (340, 400), (460, 400),              # Tail tip
]

class Particle:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.2, 0.5)
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
        self.life = random.randint(60, 120)
        self.size = random.randint(2, 4)

    def update(self):
        self.pos += self.vel
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * (self.life / 120))
            particle = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle, (255, 150, 50, alpha), (self.size, self.size), self.size)
            surface.blit(particle, (self.pos.x - self.size, self.pos.y - self.size))

particles = []

def emit_from_fox():
    for point in fox_outline:
        if random.random() < 0.2:  # sparse emission
            particles.append(Particle(*point))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((10, 10, 20))
    emit_from_fox()

    for p in particles[:]:
        p.update()
        p.draw(screen)
        if p.life <= 0:
            particles.remove(p)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
