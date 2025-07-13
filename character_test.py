import pygame
import os
from loader import slice_sprite_sheet
from utils.settings import SCREEN_WIDTH, SCREEN_HEIGHT

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Top-Down Character Tester")
clock = pygame.time.Clock()

# === CONFIG ===
SPRITE_SHEET = os.path.join("assets", "sprites", "character", "character1_walk.png")
COLUMNS = 3  # Frames per row
ROWS = 4     # Directions: up, down, left, right
FRAME_DURATION = 120  # ms
DIRECTIONS = ["up", "down", "left", "right"]

# === DETECT NATIVE SIZE ===
raw_frames = slice_sprite_sheet(SPRITE_SHEET, columns=COLUMNS, rows=ROWS, resize_to=None)
native_frame = raw_frames[0][0]
native_w, native_h = native_frame.get_size()

# === SAFE AUTO SCALING ===
max_w = SCREEN_WIDTH * 0.8
max_h = SCREEN_HEIGHT * 0.8
scale_factor = min(max_w / native_w, max_h / native_h)
scaled_w, scaled_h = int(native_w * scale_factor), int(native_h * scale_factor)
scaled_size = (scaled_w, scaled_h)

# === LOAD SCALED FRAMES ===
frames = slice_sprite_sheet(SPRITE_SHEET, columns=COLUMNS, rows=ROWS, resize_to=scaled_size)

# === Animation State ===
dir_idx = 1   # Start facing down
frame_idx = 0
timer = 0
is_moving = False
font = pygame.font.Font(None, 28)

# === Game Loop ===
running = True
while running:
    dt = clock.tick(60)
    timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    is_moving = any([keys[pygame.K_UP], keys[pygame.K_DOWN], keys[pygame.K_LEFT], keys[pygame.K_RIGHT]])

    if keys[pygame.K_UP]: dir_idx = 0
    elif keys[pygame.K_DOWN]: dir_idx = 1
    elif keys[pygame.K_LEFT]: dir_idx = 2
    elif keys[pygame.K_RIGHT]: dir_idx = 3

    if is_moving and timer >= FRAME_DURATION:
        frame_idx = (frame_idx + 1) % COLUMNS
        timer = 0
    elif not is_moving:
        frame_idx = 0

    screen.fill((30, 30, 40))

    try:
        current_frame = frames[dir_idx][frame_idx]
        frame_rect = current_frame.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(current_frame, frame_rect)
        pygame.draw.rect(screen, (255, 0, 0), frame_rect, 2)  # Frame outline
    except IndexError:
        print(f"⚠️ Missing frame: dir {dir_idx}, idx {frame_idx}")

    # === Debug Info ===
    debug = [
        f"Direction: {DIRECTIONS[dir_idx]}",
        f"Frame: {frame_idx + 1}/{COLUMNS}",
        f"Native: {native_w}x{native_h}",
        f"Scaled: {scaled_w}x{scaled_h}",
        f"Scale Factor: {scale_factor:.2f}",
        f"Moving: {'YES' if is_moving else 'NO'}"
    ]
    for i, line in enumerate(debug):
        txt = font.render(line, True, (255, 255, 255))
        screen.blit(txt, (20, 20 + i * 30))

    pygame.display.flip()

pygame.quit()
