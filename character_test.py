import pygame
import os
from loader import load_character_sheet
from utils.settings import SCREEN_WIDTH, SCREEN_HEIGHT

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Character Animation Tester")
clock = pygame.time.Clock()

SHEET_PATH = os.path.join("assets", "sprites", "character", "grass_boss.png")
data = load_character_sheet(SHEET_PATH)
frames = data["frames"]
frame_size = data["metadata"]["frame_size"]

current_dir = "down"
current_anim = "idle_down"
frame_idx = 0
frame_timer = 0
FRAME_DURATION = 120
font = pygame.font.Font(None, 28)

running = True
while running:
    dt = clock.tick(60)
    frame_timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    is_moving = False

    if keys[pygame.K_UP]:
        current_dir = "up"
        is_moving = True
    elif keys[pygame.K_DOWN]:
        current_dir = "down"
        is_moving = True
    elif keys[pygame.K_LEFT]:
        current_dir = "left"
        is_moving = True
    elif keys[pygame.K_RIGHT]:
        current_dir = "right"
        is_moving = True

    current_anim = f"walk_{current_dir}" if is_moving else f"idle_{current_dir}"

    if frame_timer >= FRAME_DURATION:
        frame_idx = (frame_idx + 1) % len(frames[current_anim])
        frame_timer = 0
    elif not is_moving:
        frame_idx = 0

    screen.fill((30, 30, 40))

    try:
        frame = frames[current_anim][frame_idx]
        rect = frame.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(frame, rect)
        pygame.draw.rect(screen, (255, 0, 0), rect, 2)
    except Exception as e:
        print(f"⚠️ Error rendering frame: {e}")

    debug_info = [
        f"Animation: {current_anim}",
        f"Frame: {frame_idx + 1}/{len(frames[current_anim])}",
        f"Direction: {current_dir}",
        f"Moving: {'YES' if is_moving else 'NO'}"
    ]

    for i, txt in enumerate(debug_info):
        surf = font.render(txt, True, (255, 255, 255))
        screen.blit(surf, (20, 20 + i * 30))

    pygame.display.flip()

pygame.quit()
