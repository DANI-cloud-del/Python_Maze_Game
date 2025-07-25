import pygame
import random
import math

class Firefly:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.size = random.randint(2, 4)
        self.alpha = random.randint(150, 255)
        self.flicker_speed = random.uniform(0.02, 0.05)
        self.flicker_phase = random.uniform(0, math.pi * 2)

    def update(self):
        self.pos += self.vel
        self.alpha = 150 + 100 * math.sin(pygame.time.get_ticks() * self.flicker_speed + self.flicker_phase)
        self.wrap()

    def draw(self, surface):
        glow = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 255, 150, int(self.alpha)), (self.size * 2, self.size * 2), self.size)
        surface.blit(glow, (self.pos.x - self.size * 2, self.pos.y - self.size * 2))

    def wrap(self):
        w, h = pygame.display.get_surface().get_size()
        if self.pos.x < 0: self.pos.x = w
        if self.pos.x > w: self.pos.x = 0
        if self.pos.y < 0: self.pos.y = h
        if self.pos.y > h: self.pos.y = 0
