import pygame

# Screen settings (these remain constant)
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Default cell settings (can be overridden by menu)
CELL_SIZE = 64  # Larger cells for better visibility
PATH_WIDTH = 48  # Visible spacing between character and walls
WALL_THICKNESS = 6
PLAYER_SIZE = 30

# Camera settings (keep if used elsewhere)
CAMERA_ZOOM = 0.8  # 0.5-1.0 (zoomed out to normal)
CAMERA_SMOOTHNESS = 0.1  # Lower = smoother
VISIBLE_RADIUS = 3  # Cells visible around player

# Lighting settings
LIGHT_RADIUS = 150
LIGHT_INTENSITY = 220
FOG_COLOR = (10, 10, 15)

PLAYER_SPEED = 3

# Shooting
BULLET_SPEED = 15
BULLET_RADIUS = 5
PLAYER_AMMO = 10
MAX_AMMO = 20
SHOOT_COOLDOWN = 300  # ms

# Doors
# DOOR_OPEN_TIME = 5000  # ms
# DOOR_CLOSED_TIME = 10000  # ms