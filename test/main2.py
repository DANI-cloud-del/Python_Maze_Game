import pygame
import random
from fireflies import Firefly

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

fireflies = [Firefly(random.randint(0, 800), random.randint(0, 600)) for _ in range(60)]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((10, 20, 30))  # dark background

    for f in fireflies:
        f.update()
        f.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
