import pygame
import random

class Ember:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.uniform(-0.5, 0.5), random.uniform(-2, -1))
        self.size = random.randint(2, 4)
        self.alpha = 255
        self.fade_rate = random.uniform(2, 4)

    def update(self):
        self.pos += self.vel
        self.alpha -= self.fade_rate

    def draw(self, surface):
        if self.alpha > 0:
            ember = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(ember, (255, 100, 50, int(self.alpha)), (self.size, self.size), self.size)
            surface.blit(ember, (self.pos.x - self.size, self.pos.y - self.size))

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
embers = []

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    embers.append(Ember(400, 550))  # spawn from bottom center
    screen.fill((10, 10, 10))

    for ember in embers[:]:
        ember.update()
        ember.draw(screen)
        if ember.alpha <= 0:
            embers.remove(ember)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
