import pygame

# Initialize temporarily to grab screen info
pygame.init()
info = pygame.display.Info()

SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

CELL_SIZE = 20
MAZE_COLS = SCREEN_WIDTH // CELL_SIZE
MAZE_ROWS = SCREEN_HEIGHT // CELL_SIZE

PLAYER_SPEED = 4
BOT_SPEED = 3
FPS = 60
