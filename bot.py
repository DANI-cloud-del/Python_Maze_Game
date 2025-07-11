import pygame
from utils.settings import BOT_SPEED

class Bot:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)

    def chase(self, target):
        if self.rect.x < target.rect.x:
            self.rect.x += BOT_SPEED
        elif self.rect.x > target.rect.x:
            self.rect.x -= BOT_SPEED
        if self.rect.y < target.rect.y:
            self.rect.y += BOT_SPEED
        elif self.rect.y > target.rect.y:
            self.rect.y -= BOT_SPEED

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)
