# player.py

import pygame
from utils.settings import CELL_SIZE, PLAYER_SPEED

class Player:
    def __init__(self, x=0, y=0):
        self.rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_UP]:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            self.rect.y += PLAYER_SPEED

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 255, 0), self.rect)
