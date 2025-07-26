import pygame
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

class HorrorStatic:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.noise_density = 10000  # More chaos
        self.flicker_alpha = 60
        self.flicker_timer = 0

    def update(self):
        self.surface.fill((0, 0, 0))
        # Raw white noise texture
        for _ in range(self.noise_density):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            b = random.randint(30, 255)
            color = (b, b, b)
            self.surface.set_at((x, y), color)

        # Every few frames, add a glitch pulse or shadow wipe
        self.flicker_timer += 1
        if self.flicker_timer % random.randint(40, 80) == 0:
            wipe = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            opacity = random.randint(50, 120)
            wipe.fill((0, 0, 0, opacity))
            self.surface.blit(wipe, (0, 0), special_flags=pygame.BLEND_MULT)

    def draw(self, screen):
        screen.blit(self.surface, (0, 0))

# Initialize static
static = HorrorStatic(800, 600)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    static.update()
    static.draw(screen)

    pygame.display.flip()
    clock.tick(30)  # Less smooth = more disturbing

pygame.quit()
