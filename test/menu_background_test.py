import pygame
import random
import math

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

class GhostParticle:
    def __init__(self, width, height):
        self.center = pygame.Vector2(random.uniform(0, width), random.uniform(0, height))
        self.radius = random.uniform(30, 120)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(0.0005, 0.0015)
        self.size = random.uniform(2, 5)
        self.alpha = random.randint(60, 120)
        self.hue = random.uniform(0.55, 0.7)  # Blue-purple
        self.color = self.hsv_to_rgb(self.hue, 0.5, 1.0)

    def hsv_to_rgb(self, h, s, v):
        i = int(h * 6)
        f = h * 6 - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        r, g, b = {
            0: (v, t, p), 1: (q, v, p), 2: (p, v, t),
            3: (p, q, v), 4: (t, p, v), 5: (v, p, q)
        }[i % 6]
        return (int(r * 255), int(g * 255), int(b * 255))

    def update(self):
        self.angle += self.speed
        self.center.x += math.sin(self.angle * 0.3) * 0.2
        self.center.y += math.cos(self.angle * 0.3) * 0.2

    def draw(self, surface):
        x = self.center.x + math.cos(self.angle) * self.radius
        y = self.center.y + math.sin(self.angle) * self.radius
        glow = pygame.Surface((int(self.size * 4), int(self.size * 4)), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, self.alpha), (int(self.size * 2), int(self.size * 2)), int(self.size * 2))
        surface.blit(glow, (x - self.size * 2, y - self.size * 2))

# Initialize particles
ghost_particles = [GhostParticle(800, 600) for _ in range(120)]

def draw_ghost_background(surface):
    fog = pygame.Surface((800, 600), pygame.SRCALPHA)
    fog.fill((5, 5, 15, 30))  # Semi-transparent dark fog layer
    surface.blit(fog, (0, 0))

    for particle in ghost_particles:
        particle.update()
        particle.draw(surface)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((10, 10, 20))  # Deep dark background
    draw_ghost_background(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
