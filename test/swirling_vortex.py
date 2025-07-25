import pygame
import random
import math

class VortexParticle:
    def __init__(self, center):
        self.angle = random.uniform(0, 2 * math.pi)
        self.radius = random.uniform(50, 150)
        self.speed = random.uniform(0.01, 0.03)
        self.size = random.randint(2, 4)
        self.center = center
        self.color = (150, 200, 255)

    def update(self):
        self.angle += self.speed

    def draw(self, surface):
        x = self.center[0] + math.cos(self.angle) * self.radius
        y = self.center[1] + math.sin(self.angle) * self.radius
        pygame.draw.circle(surface, self.color, (int(x), int(y)), self.size)

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
center = (400, 300)
vortex_particles = [VortexParticle(center) for _ in range(80)]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((10, 10, 20))
    for vortex in vortex_particles:
        vortex.update()
        vortex.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
