import pygame

# Screen settings
pygame.init()
info = pygame.display.Info()
SCREEN_WIDTH = 800  # Fixed window size for consistent zoom
SCREEN_HEIGHT = 600
FPS = 60

# Maze settings
CELL_SIZE = 64  # Larger cells for better visibility
PATH_WIDTH = 48  # Visible spacing between character and walls
WALL_THICKNESS = 6
PLAYER_SIZE = 30
MAZE_COLS = 30
MAZE_ROWS = 30
MAZE_COMPLEXITY = 0.7  # 0.1-1.0 (simple to complex)

# Camera settings
CAMERA_ZOOM = 0.8  # 0.5-1.0 (zoomed out to normal)
CAMERA_SMOOTHNESS = 0.1  # Lower = smoother
VISIBLE_RADIUS = 3  # Cells visible around player

# Lighting settings
LIGHT_RADIUS = 150  # Pixels
LIGHT_INTENSITY = 220  # 0-255
FOG_COLOR = (10, 10, 15)  # Dark blue-gray

PLAYER_SPEED = 3  # Slightly slower for better control