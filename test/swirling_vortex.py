import pygame
import random
import math

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

class ElegantVortexParticle:
    def __init__(self, center):
        self.angle = random.uniform(0, 2 * math.pi)
        self.radius = random.uniform(60, 180)
        self.speed = random.uniform(0.001, 0.004)  # Much slower
        self.base_size = random.uniform(1.5, 3.5)
        self.size = self.base_size
        self.center = center

        # Moody color palette (blue-purple)
        hue = random.uniform(0.58, 0.75)
        self.color = self.hsv_to_rgb(hue, 0.7, 0.9)

        # Subtle pulsing
        self.pulse_speed = random.uniform(0.007, 0.015)
        self.pulse_range = random.uniform(0.3, 1.0)
        self.phase_offset = random.uniform(0, math.pi * 2)

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
        time = pygame.time.get_ticks()
        self.size = self.base_size + math.sin(time * self.pulse_speed + self.phase_offset) * self.pulse_range

    def draw(self, surface):
        x = self.center[0] + math.cos(self.angle) * self.radius
        y = self.center[1] + math.sin(self.angle) * self.radius

        # Soft glow effect
        glow = pygame.Surface((int(self.size * 4), int(self.size * 4)), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 50), (int(self.size * 2), int(self.size * 2)), int(self.size * 2))
        surface.blit(glow, (x - self.size * 2, y - self.size * 2))

        # Core particle
        pygame.draw.circle(surface, self.color, (int(x), int(y)), max(1, int(self.size)))

# Setup
center = (400, 300)
vortex_particles = [ElegantVortexParticle(center) for _ in range(100)]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((8, 8, 15))  # Deep twilight background
    for vortex in vortex_particles:
        vortex.update()
        vortex.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
