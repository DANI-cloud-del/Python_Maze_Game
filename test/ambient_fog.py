import pygame
import random

class FogParticle:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.uniform(-0.2, 0.2), random.uniform(-0.1, 0.1))
        self.size = random.randint(30, 60)
        self.alpha = random.randint(30, 80)

    def update(self):
        self.pos += self.vel
        self.wrap()

    def draw(self, surface):
        fog = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(fog, (200, 200, 255, self.alpha), (self.size // 2, self.size // 2), self.size // 2)
        surface.blit(fog, (self.pos.x - self.size // 2, self.pos.y - self.size // 2))

    def wrap(self):
        w, h = pygame.display.get_surface().get_size()
        if self.pos.x < 0: self.pos.x = w
        if self.pos.x > w: self.pos.x = 0
        if self.pos.y < 0: self.pos.y = h
        if self.pos.y > h: self.pos.y = 0

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
fog_particles = [FogParticle(random.randint(0, 800), random.randint(0, 600)) for _ in range(40)]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((20, 30, 40))
    for fog in fog_particles:
        fog.update()
        fog.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
